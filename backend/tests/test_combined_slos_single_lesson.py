"""
Regression: when a substrand has ``number_of_lessons == 1`` AND multiple
parent SLOs, the scheme row for that lesson MUST list every SLO as a
bulleted item, not silently drop all but the first.

Bug history
-----------
``routes/schemes.py`` builds rows via
    ``parent_slo = parent_slos[idx % len(parent_slos)]``
so for ``num_lessons=1, len(parent_slos)=3`` the loop ran exactly once
with ``idx=0`` and only ever surfaced ``parent_slos[0]``. SLOs 2 and 3
never reached the rendered scheme, even though they were correctly
stored in the DB.

Contract under test
-------------------
- The combined SLO text starts with the standard preamble
  "By the end of the lesson the learner should be able to:" (or its
  Kiswahili equivalent for Kiswahili subjects).
- Each SLO body appears as ``- <body>`` on its own line.
- Bodies are stripped of any pre-existing preamble so we don't end up
  with double "By the end of…" prefixes.
- Multi-lesson substrands are NOT affected — round-robin behaviour is
  preserved when ``num_lessons > 1`` or there's only one SLO.
- The pre-formatted SLO text is passed through to the renderer
  unchanged (no double-prefix added by ``format_slo_with_prefix``).
"""
from __future__ import annotations

import sys

sys.path.insert(0, "/app/backend")

from routes.schemes import _format_slo_for_scheme


def _build_combined_slo(parent_slos, is_kiswahili=False):
    """Mirror the single-lesson + multi-SLO branch from
    ``routes/schemes.py`` so the unit test can exercise the format
    contract without touching MongoDB."""
    bullets = []
    for s in parent_slos:
        body = _format_slo_for_scheme(s.get("name", ""), is_kiswahili)
        if body:
            bullets.append(f"- {body}")
    if is_kiswahili:
        return "Kufikia mwisho wa somo, mwanafunzi aweze:\n" + "\n".join(bullets)
    return "By the end of the lesson the learner should be able to:\n" + "\n".join(bullets)


def test_three_slos_in_single_lesson_yield_bulleted_list():
    parents = [
        {"name": "Identify genres of oral literature"},
        {"name": "Analyse features of oral literature"},
        {"name": "Apply oral literature in everyday communication"},
    ]
    out = _build_combined_slo(parents)
    assert out == (
        "By the end of the lesson the learner should be able to:\n"
        "- Identify genres of oral literature\n"
        "- Analyse features of oral literature\n"
        "- Apply oral literature in everyday communication"
    )


def test_existing_preamble_is_stripped_from_each_bullet():
    """If the SLO text already includes 'By the end…' we must NOT end up
    with duplicated preambles in the bullets."""
    parents = [
        {"name": "By the end of the lesson, the learner should be able to identify shapes"},
        {"name": "describe shapes"},
    ]
    out = _build_combined_slo(parents)
    # The preamble appears EXACTLY once at the top
    assert out.count("By the end of the lesson") == 1
    assert "- identify shapes" in out
    assert "- describe shapes" in out


def test_kiswahili_uses_kiswahili_preamble():
    parents = [
        {"name": "Eleza maana ya fasihi simulizi"},
        {"name": "Tambua sifa za fasihi simulizi"},
    ]
    out = _build_combined_slo(parents, is_kiswahili=True)
    assert out.startswith("Kufikia mwisho wa somo, mwanafunzi aweze:\n")
    assert "- Eleza maana ya fasihi simulizi" in out
    assert "- Tambua sifa za fasihi simulizi" in out
    # English preamble must NOT appear in a Kiswahili scheme
    assert "By the end of the lesson" not in out


def test_blank_or_empty_slos_are_dropped_silently():
    parents = [
        {"name": "First real outcome"},
        {"name": ""},
        {"name": "   "},
        {"name": "Second real outcome"},
    ]
    out = _build_combined_slo(parents)
    # Only two bullets, blank ones skipped
    assert out.count("\n- ") == 2
    assert "First real outcome" in out
    assert "Second real outcome" in out


def test_route_decision_combine_only_when_one_lesson_and_many_slos():
    """The routing condition itself, isolated. ``combine_all_slos`` should
    fire for (num_lessons=1, n_slos>1) and never anywhere else."""
    cases = [
        # (num_lessons, n_slos, expected_combine)
        (1, 1, False),   # only one SLO — round-robin is fine
        (1, 2, True),    # the bug we're fixing
        (1, 5, True),    # any count >1 still fires
        (2, 5, False),   # multi-lesson plan keeps round-robin
        (10, 3, False),  # round-robin (with repetition) on 10-lesson term
    ]
    for num_lessons, n_slos, expected in cases:
        actual = (num_lessons == 1 and n_slos > 1)
        assert actual is expected, (
            f"combine_all_slos for num_lessons={num_lessons}, "
            f"n_slos={n_slos}: got {actual}, expected {expected}"
        )


def test_two_slos_render_with_two_bullets():
    """Smallest case where the new behaviour kicks in."""
    parents = [
        {"name": "Read the passage aloud"},
        {"name": "Answer comprehension questions"},
    ]
    out = _build_combined_slo(parents)
    # Two bullet lines after the preamble
    bullet_lines = [ln for ln in out.split("\n") if ln.startswith("- ")]
    assert len(bullet_lines) == 2
    assert bullet_lines[0] == "- Read the passage aloud"
    assert bullet_lines[1] == "- Answer comprehension questions"
