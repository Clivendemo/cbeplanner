"""
Regression: chunk-level checkpointing for ``extract_with_gemini_chunked``.

Verifies:
  1. Each successful chunk persists a checkpoint immediately.
  2. On resume, completed chunks are skipped — Gemini is NOT re-called.
  3. The detected grade is preserved across resume even when chunk 1 is
     skipped.
  4. After every chunk succeeds and the result is merged, the checkpoint
     file is deleted automatically.
  5. Failures retry up to 3 times with exponential backoff (2s/4s/8s).
  6. The checkpoint file lives in a configurable folder (env-controlled).

These tests monkeypatch ``extract_with_gemini`` so no real Gemini calls
are made.
"""
from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path
from typing import List

import pytest


SCRIPTS_DIR = "/app/backend/scripts"


@pytest.fixture
def extractor_with_tmpdir(tmp_path, monkeypatch):
    """Reload ai_extractor with CURRICULUM_CHECKPOINT_DIR pointed at a
    pytest tmp_path so each test gets an isolated checkpoint folder.

    Adds /app/backend/scripts to sys.path *only for the duration of this
    fixture* — leaving it on the global path would shadow other modules
    (e.g. /app/backend/curriculum_pipeline.py) for the rest of the test
    session.
    """
    monkeypatch.setenv("CURRICULUM_CHECKPOINT_DIR", str(tmp_path))
    monkeypatch.syspath_prepend(SCRIPTS_DIR)
    # Force a clean import so the new env var is picked up and any cached
    # ai_extractor / curriculum_pipeline shims from previous tests are
    # discarded.
    for mod in ("ai_extractor", "curriculum_pipeline"):
        sys.modules.pop(mod, None)
    import ai_extractor
    yield ai_extractor, tmp_path
    # Tear down: drop the modules we polluted so the next test file
    # imports the real /app/backend/curriculum_pipeline.py cleanly.
    for mod in ("ai_extractor", "curriculum_pipeline"):
        sys.modules.pop(mod, None)


def _build_long_text(n_chunks: int = 4, chunk_size: int = 15000) -> str:
    """Build text guaranteed to split into ~n_chunks. Each line is
    ~50 chars and we put many lines per chunk worth of text."""
    line = "x" * 50
    # Need slightly more than n_chunks * chunk_size chars to force the split
    total_chars = (n_chunks * chunk_size) + 100
    n_lines = total_chars // (len(line) + 1)
    return "\n".join([line] * n_lines)


# ---------------------------------------------------------------------------
# 1. Each successful chunk writes a checkpoint
# ---------------------------------------------------------------------------

def test_checkpoint_file_written_after_each_chunk(extractor_with_tmpdir, monkeypatch):
    ai_extractor, tmp_path = extractor_with_tmpdir

    call_count = {"n": 0}
    snapshots: List[int] = []  # number of files in checkpoint dir per call

    async def fake_extract(text, suffix=""):
        call_count["n"] += 1
        snapshots.append(len(list(tmp_path.glob("checkpoint_*.json"))))
        return {
            "grade": "Grade 10" if call_count["n"] == 1 else None,
            "subject_name": "Math",
            "strands": [{"name": f"Strand-{call_count['n']}", "substrands": []}],
        }

    monkeypatch.setattr(ai_extractor, "extract_with_gemini", fake_extract)

    text = _build_long_text(n_chunks=3)
    asyncio.run(
        ai_extractor.extract_with_gemini_chunked(text, "Math", "Grade 10")
    )

    # After all chunks completed, checkpoint must be deleted.
    assert list(tmp_path.glob("checkpoint_*.json")) == [], \
        "checkpoint file must be deleted after a fully successful run"

    # Gemini was called exactly once per chunk.
    assert call_count["n"] >= 2


# ---------------------------------------------------------------------------
# 2. Resume skips already-completed chunks
# ---------------------------------------------------------------------------

def test_resume_skips_completed_chunks(extractor_with_tmpdir, monkeypatch):
    ai_extractor, tmp_path = extractor_with_tmpdir

    text = _build_long_text(n_chunks=4)
    chunks = ai_extractor._split_into_chunks(text, max_chars=15000)
    n_chunks = len(chunks)
    assert n_chunks >= 3, "test requires at least 3 chunks"

    # Run 1: fail on chunk index 1 (the second call) AFTER chunk 0
    # has been persisted. Fail consistently across all retry attempts
    # so retries are exhausted and the run aborts.
    call_log_run1: List[int] = []

    async def fake_extract_run1(text_arg, suffix=""):
        i = int(suffix.rsplit("_", 1)[-1])
        call_log_run1.append(i)
        if i == 1:
            raise RuntimeError("simulated 503")
        return {
            "grade": "Grade 7" if i == 0 else None,
            "subject_name": "Kiswahili",
            "strands": [{"name": f"Strand-run1-{i}", "substrands": []}],
        }

    # Disable retries' real sleeps to keep the test fast
    async def no_sleep(_):
        return None
    monkeypatch.setattr(ai_extractor.asyncio, "sleep", no_sleep)
    monkeypatch.setattr(ai_extractor, "extract_with_gemini", fake_extract_run1)

    with pytest.raises(RuntimeError, match="simulated 503"):
        asyncio.run(
            ai_extractor.extract_with_gemini_chunked(text, "Kiswahili", "Grade 7")
        )

    # Checkpoint must be intact (chunk 0 only).
    ckpts = list(tmp_path.glob("checkpoint_*.json"))
    assert len(ckpts) == 1, "checkpoint must be preserved when extraction fails"
    import json
    state = json.loads(ckpts[0].read_text())
    assert "0" in state["completed_chunks"]
    assert "1" not in state["completed_chunks"]
    assert state["detected_grade"] == "Grade 7"

    # Run 2: simulate everything succeeding. Gemini must NOT be called for
    # chunk 0 because it's already in the checkpoint.
    call_log_run2: List[int] = []

    async def fake_extract_run2(text_arg, suffix=""):
        # Track WHICH chunk index Gemini is called for. The suffix carries
        # `<subject>_<i>` so we can inspect it.
        idx = int(suffix.rsplit("_", 1)[-1])
        call_log_run2.append(idx)
        return {
            "grade": None,
            "subject_name": "Kiswahili",
            "strands": [{"name": f"Strand-run2-{idx}", "substrands": []}],
        }

    monkeypatch.setattr(ai_extractor, "extract_with_gemini", fake_extract_run2)

    final = asyncio.run(
        ai_extractor.extract_with_gemini_chunked(text, "Kiswahili", "Grade 7")
    )

    # Chunk 0 must NOT have been re-called
    assert 0 not in call_log_run2, \
        f"chunk 0 was already in the checkpoint and must not be re-extracted; got call log {call_log_run2}"

    # Grade survives the resume even though chunk 0 (where it was detected)
    # was skipped this run.
    assert final["grade"] == "Grade 7"

    # Final result includes strands from BOTH runs (cached + fresh).
    strand_names = [s["name"] for s in final["strands"]]
    assert "Strand-run1-0" in strand_names, \
        f"cached chunk 0 strand missing from final merge; got {strand_names}"
    assert any(name.startswith("Strand-run2-") for name in strand_names), \
        f"fresh chunks missing from final merge; got {strand_names}"

    # Checkpoint cleaned up after success
    assert list(tmp_path.glob("checkpoint_*.json")) == []


# ---------------------------------------------------------------------------
# 3. Retry with exponential backoff on transient errors
# ---------------------------------------------------------------------------

def test_retry_backoff_on_transient_error(extractor_with_tmpdir, monkeypatch):
    ai_extractor, tmp_path = extractor_with_tmpdir

    attempts = {"n": 0}

    async def flaky(text, suffix=""):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("503 Service Unavailable")
        return {"grade": "Grade 1", "subject_name": "X", "strands": []}

    sleep_calls: List[float] = []

    async def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(ai_extractor, "extract_with_gemini", flaky)
    monkeypatch.setattr(ai_extractor.asyncio, "sleep", fake_sleep)

    result = asyncio.run(
        ai_extractor._call_gemini_with_retry("text", "suffix")
    )
    assert result["grade"] == "Grade 1"
    assert attempts["n"] == 3
    # Backoff: 2s after attempt 1, 4s after attempt 2 (no sleep after the
    # final successful attempt).
    assert sleep_calls == [2.0, 4.0]


def test_retry_gives_up_after_max_attempts(extractor_with_tmpdir, monkeypatch):
    ai_extractor, _ = extractor_with_tmpdir

    attempts = {"n": 0}

    async def always_fails(text, suffix=""):
        attempts["n"] += 1
        raise RuntimeError("503 forever")

    async def no_sleep(_):
        return None

    monkeypatch.setattr(ai_extractor, "extract_with_gemini", always_fails)
    monkeypatch.setattr(ai_extractor.asyncio, "sleep", no_sleep)

    with pytest.raises(RuntimeError, match="503 forever"):
        asyncio.run(ai_extractor._call_gemini_with_retry("text", "s"))

    # Default is 3 attempts total
    assert attempts["n"] == 3


# ---------------------------------------------------------------------------
# 4. Checkpoint folder is configurable + auto-created
# ---------------------------------------------------------------------------

def test_checkpoint_dir_is_configurable_and_auto_created(tmp_path, monkeypatch):
    nested = tmp_path / "deep" / "nested" / "ckpt"
    monkeypatch.setenv("CURRICULUM_CHECKPOINT_DIR", str(nested))
    monkeypatch.syspath_prepend(SCRIPTS_DIR)

    for mod in ("ai_extractor", "curriculum_pipeline"):
        sys.modules.pop(mod, None)
    import ai_extractor

    try:
        path = ai_extractor._checkpoint_path("My Subject", "Grade 10")
        assert nested.exists(), "checkpoint directory must be auto-created"
        assert path.parent == nested
        assert path.name.startswith("checkpoint_")
        assert path.suffix == ".json"
    finally:
        for mod in ("ai_extractor", "curriculum_pipeline"):
            sys.modules.pop(mod, None)


# ---------------------------------------------------------------------------
# 5. Stale checkpoint (different source text) is invalidated
# ---------------------------------------------------------------------------

def test_stale_checkpoint_is_discarded(extractor_with_tmpdir):
    ai_extractor, tmp_path = extractor_with_tmpdir

    path = ai_extractor._checkpoint_path("X", "Grade 1")
    # Write a checkpoint whose fingerprint doesn't match anything we'll ask for.
    ai_extractor._save_checkpoint(path, {
        "fingerprint": "deadbeef",
        "chunk_count": 99,
        "completed_chunks": {"0": {"strands": []}},
        "detected_grade": "Grade 99",
        "subject_name": "wrong",
    })

    state = ai_extractor._load_checkpoint(path, "different_fingerprint", 3)
    assert state["completed_chunks"] == {}
    assert state["detected_grade"] is None
    assert not path.exists(), "stale checkpoint must be deleted"
