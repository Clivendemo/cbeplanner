"""
AI Curriculum Extractor — Gemini 2.5 Flash (google-genai)
Extracts structured curriculum data from PDF text using Gemini AI.
Outputs the EXACT JSON structure needed by the seed script generator.

Responsibility boundary:
  - This module DETECTS grade/subject from PDF text and returns JSON.
  - It does NOT write to the database.
  - The seed/import stage handles DB matching and creation.
"""

import os
import json
import asyncio
import hashlib
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Import normalizer (extractor normalizes its own output before returning)
from grade_utils import normalize_grade_name

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


# ---------------------------------------------------------------------------
# Checkpointing — survive 503s / network blips during multi-chunk extraction.
# ---------------------------------------------------------------------------
#
# A long PDF (≥18 KB of text) is split into 15 KB chunks, and each chunk is a
# separate Gemini call. If chunk 7 of 12 hits a transient 503, we don't want
# to re-pay the cost of chunks 1-6. The checkpoint file persists per-chunk
# results to disk after each success; on restart, we skip what's already
# done and only re-call Gemini for the remainder. The file is deleted once
# the extraction completes successfully.
#
# Checkpoint location is configurable via CURRICULUM_CHECKPOINT_DIR.

CHECKPOINT_DIR = Path(
    os.environ.get("CURRICULUM_CHECKPOINT_DIR")
    or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checkpoints")
)


def _checkpoint_slug(value: str) -> str:
    """Filesystem-safe slug for filenames: lowercase, alphanum + dashes."""
    if not value:
        return "unknown"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip()).strip("-").lower()
    return slug or "unknown"


def _checkpoint_path(subject_hint: str, grade_hint: str) -> Path:
    """Build the checkpoint file path for a (subject, grade) pair."""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    return CHECKPOINT_DIR / f"checkpoint_{_checkpoint_slug(subject_hint)}_{_checkpoint_slug(grade_hint)}.json"


def _text_fingerprint(text: str) -> str:
    """Short hash of the source text — invalidates the checkpoint when the
    underlying PDF changes between runs (e.g. user re-uploads a corrected
    version)."""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _load_checkpoint(path: Path, expected_fingerprint: str, expected_chunk_count: int) -> dict:
    """Load a checkpoint if it matches the current text + chunk count.

    Returns an empty fresh-state dict if the file is missing, corrupt, or
    stale. Stale checkpoints are deleted so the run starts clean.
    """
    fresh = {
        "fingerprint": expected_fingerprint,
        "chunk_count": expected_chunk_count,
        "completed_chunks": {},   # {"<index>": {<gemini result dict>}}
        "detected_grade": None,
        "subject_name": "",
    }
    if not path.exists():
        return fresh
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # Corrupt — treat as missing and start fresh
        try:
            path.unlink()
        except OSError:
            pass
        return fresh

    if (
        data.get("fingerprint") != expected_fingerprint
        or data.get("chunk_count") != expected_chunk_count
    ):
        # Source PDF or chunking changed — invalid resume target
        try:
            path.unlink()
        except OSError:
            pass
        return fresh

    # Make sure shape matches what the rest of the code expects
    data.setdefault("completed_chunks", {})
    data.setdefault("detected_grade", None)
    data.setdefault("subject_name", "")
    return data


def _save_checkpoint(path: Path, state: dict) -> None:
    """Atomic write — temp file + rename, so a crash mid-write doesn't
    corrupt the checkpoint."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _delete_checkpoint(path: Path) -> None:
    """Best-effort cleanup. Missing file is fine."""
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        # Don't fail the extraction over a stuck file lock
        pass


async def _call_gemini_with_retry(
    text: str,
    suffix: str,
    *,
    max_attempts: int = 3,
    base_delay: float = 2.0,
) -> dict:
    """Wrap ``extract_with_gemini`` with exponential-backoff retries.

    Retries on ANY exception (503s from the Gemini service, transient
    network errors, momentary JSON-repair failures). Backoff: 2s, 4s, 8s.
    Re-raises the last exception when ``max_attempts`` is exhausted.
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await extract_with_gemini(text, suffix)
        except Exception as exc:  # noqa: BLE001 — intentional: retry any failure
            last_exc = exc
            if attempt >= max_attempts:
                break
            delay = base_delay * (2 ** (attempt - 1))
            print(
                f"    Gemini call failed (attempt {attempt}/{max_attempts}): "
                f"{exc!s}. Retrying in {delay:.0f}s…"
            )
            await asyncio.sleep(delay)
    assert last_exc is not None  # for type-checkers; loop guarantees this
    raise last_exc


# ---------------------------------------------------------------------------
# Extraction prompt — strengthened grade detection
# ---------------------------------------------------------------------------

EXTRACTION_PROMPT = """You are extracting KICD (Kenya Institute of Curriculum Development) CBC (Competency-Based Curriculum) data from a curriculum design PDF.

Return ONLY valid JSON. No markdown, no explanations, no code blocks.

STRICT RULES:
- Do NOT summarize or shorten ANY text. Preserve exact wording from the document.
- Capture ALL strands, ALL substrands, ALL SLOs (Specific Learning Outcomes) completely.
- Maintain the full hierarchy: Subject → Strands → Substrands → SLOs
- Each substrand must have its learning activities split into 4 categories:
  * introduction: Opening/warm-up activities
  * development: Main teaching activities (GENERAL classroom activities)
  * conclusion: Closing/wrap-up activities
  * extended: Activities containing keywords: practical, project, experiment, field work, assignment, research, investigation, survey, field trip, hands-on
- If an activity contains those keywords, it MUST go to "extended", not "development"
- Capture competencies, values, PCIs (Pertinent Contemporary Issues) per substrand
- Capture Key Inquiry Question(s) per substrand. KICD documents present these
  under headings like "Key Inquiry Question(s)", "Key Inquiry Questions:" or
  the singular "Key Inquiry Question:". Extract every distinct question as a
  separate string, preserving the trailing "?" verbatim. Do NOT paraphrase or
  invent questions if none are present in the source.
- Include assessment methods and learning resources when available
- Estimate lesson count per substrand from the document if mentioned

GRADE DETECTION (CRITICAL):
- You MUST identify the exact grade/class/level from the document.
- Look for grade information in: title page, headers, footers, repeated section headings,
  "Curriculum Designs for..." text, "Grade X" references, and document metadata.
- Return the grade in the format "Grade X" (e.g. "Grade 1", "Grade 10").
- For pre-primary, return "PP1" or "PP2".
- If the document says "Junior School" or "Senior School", still extract the grade number.
- If you find MULTIPLE grades mentioned (e.g. a combined Grade 7-9 document), return
  the LOWEST grade as the primary grade.
- If you genuinely CANNOT find any grade information anywhere in the text, return
  "grade": null — do NOT guess or assume a grade number.

OUTPUT FORMAT (strict JSON):
{
  "grade": "Grade X",
  "subject_name": "Subject Name",
  "strands": [
    {
      "name": "Strand Name",
      "substrands": [
        {
          "name": "Substrand Name",
          "lessons": 10,
          "slos": [
            {"name": "Full SLO text", "description": "Full SLO text"}
          ],
          "learning_activities": {
            "introduction": "Introduction activities text",
            "development": "Development activities text",
            "conclusion": "Conclusion activities text",
            "extended": "Extended activities text",
            "resources": ["Resource 1", "Resource 2"],
            "assessment": ["Method 1", "Method 2"]
          },
          "competencies": ["Competency 1", "Competency 2"],
          "values": ["Value 1", "Value 2"],
          "pcis": ["PCI 1", "PCI 2"],
          "inquiry_questions": ["Key inquiry question 1?", "Key inquiry question 2?"]
        }
      ]
    }
  ]
}

If lesson count is not available, estimate based on content volume.

PDF TEXT:
"""


def _get_client():
    """Create Gemini client using API key from environment."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set in environment")
    return genai.Client(api_key=api_key)


def _post_process_grade(result: dict, grade_hint: str = "") -> dict:
    """Normalize the grade field returned by the AI.

    Priority:
      1. AI-detected grade (if not null/empty)
      2. grade_hint from filename/caller
      3. None (caller must handle)

    Never silently defaults to "Grade 10" or any other arbitrary value.
    """
    raw_grade = result.get("grade")
    normalized = normalize_grade_name(raw_grade) if raw_grade else None

    if normalized:
        result["grade"] = normalized
        return result

    # AI returned null/empty — try the hint
    hint_normalized = normalize_grade_name(grade_hint) if grade_hint else None
    if hint_normalized:
        result["grade"] = hint_normalized
        result["_grade_source"] = "hint"
        return result

    # Truly unknown
    result["grade"] = None
    result["_grade_source"] = "unknown"
    return result


async def extract_with_gemini(text: str, session_suffix: str = "") -> dict:
    """Extract curriculum data from PDF text using Gemini 2.5 Flash.

    Forces strict JSON output via ``response_mime_type='application/json'``
    and bumps ``max_output_tokens`` to the Gemini 2.5 Flash ceiling so the
    response is never truncated mid-document — that was the root cause of
    intermittent ``Cannot repair JSON`` failures on long KICD PDFs like
    the Kiswahili Fasihi designs.
    """
    from google.genai import types as genai_types

    client = _get_client()

    prompt = EXTRACTION_PROMPT + text

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                # Gemini 2.5 Flash supports up to 65 535 output tokens.
                # Curriculum extractions for the largest KICD PDFs land
                # around ~30k tokens, so this comfortably avoids truncation.
                max_output_tokens=65535,
                # Deterministic-ish output is fine for structured extraction.
                temperature=0.2,
            ),
        )
    )

    response_text = (response.text or "").strip()

    # Hard fail with a useful message if Gemini still hit the ceiling.
    finish_reason = None
    try:
        finish_reason = response.candidates[0].finish_reason
    except (AttributeError, IndexError):
        pass
    if finish_reason and str(finish_reason).endswith("MAX_TOKENS"):
        raise ValueError(
            "Gemini truncated the response (finish_reason=MAX_TOKENS). "
            "Re-run with a smaller chunk or split the PDF further."
        )

    # Use robust JSON repair (handles fences, trailing commas, smart quotes, truncation)
    from curriculum_pipeline import repair_json
    return repair_json(response_text)


async def extract_with_gemini_chunked(
    text: str,
    subject_hint: str = "",
    grade_hint: str = "",
) -> dict:
    """For very large PDFs, extract in chunks then merge.

    Grade handling:
    - The FIRST chunk's grade (or the most explicit one) is preferred.
    - Later chunks do NOT overwrite an already-detected grade with a guess.
    - After merging, the grade is normalized via grade_utils.
    """
    # Single-shot extraction for small documents
    if len(text) < 18000:
        result = await extract_with_gemini(text, subject_hint.replace(" ", "_"))
        return _post_process_grade(result, grade_hint)

    # Chunked extraction. 15 000 chars per chunk keeps each Gemini call
    # well under the response-token ceiling, which avoids truncation on
    # dense KICD curriculum tables (Kiswahili / Fasihi etc.).
    chunks = _split_into_chunks(text, max_chars=15000)
    print(f"  Large PDF detected - splitting into {len(chunks)} chunks")

    # ── Checkpoint setup ────────────────────────────────────────────────
    # Persist per-chunk results so a 503 / network blip mid-extraction
    # only costs us the failing chunk, not the whole document.
    fingerprint = _text_fingerprint(text)
    ckpt_path = _checkpoint_path(subject_hint, grade_hint)
    state = _load_checkpoint(ckpt_path, fingerprint, len(chunks))

    completed: dict = state["completed_chunks"]
    detected_grade = state.get("detected_grade")    # First confident detection wins
    subject_name = state.get("subject_name") or subject_hint

    if completed:
        print(
            f"  Resuming from checkpoint: {len(completed)}/{len(chunks)} chunks "
            f"already extracted (file: {ckpt_path.name})"
        )

    for i, chunk in enumerate(chunks):
        key = str(i)
        if key in completed:
            # Already done in a prior run — replay grade detection so the
            # priority order is preserved if chunk 1 was the one cached.
            cached = completed[key]
            chunk_grade = cached.get("grade")
            if chunk_grade and not detected_grade:
                normalized = normalize_grade_name(chunk_grade)
                if normalized:
                    detected_grade = normalized
                    state["detected_grade"] = detected_grade
            if cached.get("subject_name") and not state.get("subject_name"):
                subject_name = cached["subject_name"]
                state["subject_name"] = subject_name
            print(f"  Chunk {i+1}/{len(chunks)}: skipped (cached)")
            continue

        print(f"  Extracting chunk {i+1}/{len(chunks)}...")
        hint = f"\nContext: This is part {i+1} of {len(chunks)} from {subject_hint}.\n"
        result = await _call_gemini_with_retry(hint + chunk, f"{subject_hint}_{i}")

        # Grade: keep the first non-null detection, don't let later chunks overwrite
        chunk_grade = result.get("grade")
        if chunk_grade and not detected_grade:
            normalized = normalize_grade_name(chunk_grade)
            if normalized:
                detected_grade = normalized
                print(f"    Grade detected from chunk {i+1}: {detected_grade}")

        if result.get("subject_name"):
            subject_name = result["subject_name"]

        # Persist this chunk's result before moving on. If the next chunk
        # fails, the next run will skip everything up to and including
        # this index.
        completed[key] = result
        state["completed_chunks"] = completed
        state["detected_grade"] = detected_grade
        state["subject_name"] = subject_name
        _save_checkpoint(ckpt_path, state)

    # All chunks succeeded — flatten strands in original chunk order.
    all_strands: list = []
    for i in range(len(chunks)):
        all_strands.extend(completed[str(i)].get("strands", []))

    merged = _merge_strands(all_strands)

    final = {
        "grade": detected_grade,
        "subject_name": subject_name,
        "strands": merged,
    }

    # Successful end-to-end — clean up the checkpoint so the next run
    # of the same (subject, grade) pair starts fresh.
    _delete_checkpoint(ckpt_path)

    return _post_process_grade(final, grade_hint)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_into_chunks(text: str, max_chars: int = 25000) -> list:
    """Split text into chunks, trying to break at paragraph boundaries."""
    lines = text.split("\n")
    chunks = []
    current = []
    current_len = 0

    for line in lines:
        line_len = len(line) + 1
        if current_len + line_len > max_chars and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += line_len

    if current:
        chunks.append("\n".join(current))

    return chunks


def _merge_strands(strands: list) -> list:
    """Merge strands with the same name (from chunked extraction)."""
    merged = {}
    for strand in strands:
        name = strand.get("name", "")
        if name not in merged:
            merged[name] = strand
        else:
            existing_ss = {ss["name"] for ss in merged[name].get("substrands", [])}
            for ss in strand.get("substrands", []):
                if ss["name"] not in existing_ss:
                    merged[name]["substrands"].append(ss)
                    existing_ss.add(ss["name"])
    return list(merged.values())
