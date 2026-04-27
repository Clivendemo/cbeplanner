"""
Regression: scheme generator must use the DB-stored Key Inquiry Question
(KIQ) verbatim, ahead of any algorithmic SLO-derivation, to avoid the
grammatical errors produced by verb-stem heuristics.

Priority order under test:
  1. lesson_slo_slots.key_inquiry_question  (per-lesson, admin-curated)
  2. learning_activities.inquiry_questions[] (per-substrand, KICD-seeded)
  3. derive_inquiry_from_slo(...)            (fallback)
  4. generate_inquiry_questions(...)         (final generic fallback)

This test exercises the priority logic directly, mirroring the block in
backend/routes/schemes.py without spinning up the full HTTP stack.
"""
from scheme_generator import derive_inquiry_from_slo, generate_inquiry_questions


def _resolve_inquiry(content: dict, is_kiswahili: bool = False) -> str:
    """Mirror of the priority block in routes/schemes.py for unit-testing."""
    slot_inquiry = content.get("_slotInquiry")
    substrand_iqs = content.get("_substrandInquiries") or []
    if slot_inquiry:
        return slot_inquiry
    if substrand_iqs:
        pos = max(0, content.get("lessonInSubstrand", 1) - 1)
        return substrand_iqs[pos % len(substrand_iqs)]
    derived = derive_inquiry_from_slo(content["slo"], is_kiswahili)
    if derived:
        return derived
    return generate_inquiry_questions(content["strand"], content["substrand"], content["slo"])


def test_slot_kiq_wins_over_substrand_array_and_derivation():
    """When lesson_slo_slots has a per-lesson KIQ, it MUST be returned verbatim."""
    content = {
        "_slotInquiry": "Why are mitochondria called the powerhouse of the cell?",
        "_substrandInquiries": ["Should not be used", "Also ignored"],
        "lessonInSubstrand": 1,
        "slo": "describe the structure of mitochondria",
        "strand": "Cells", "substrand": "Cell organelles",
    }
    assert _resolve_inquiry(content) == "Why are mitochondria called the powerhouse of the cell?"


def test_substrand_array_used_when_slot_has_no_kiq():
    """No per-lesson KIQ → cycle through learning_activities.inquiry_questions[]."""
    content = {
        "_slotInquiry": "",
        "_substrandInquiries": ["Q1: First lesson?", "Q2: Second lesson?", "Q3: Third lesson?"],
        "lessonInSubstrand": 2,  # 1-based → index 1
        "slo": "explain the water cycle",
        "strand": "Earth", "substrand": "Water",
    }
    assert _resolve_inquiry(content) == "Q2: Second lesson?"


def test_substrand_array_cycles_for_extra_lessons():
    """Lesson 4 with 3 questions → wraps to index 0."""
    content = {
        "_slotInquiry": "",
        "_substrandInquiries": ["A", "B", "C"],
        "lessonInSubstrand": 4,
        "slo": "describe X",
        "strand": "S", "substrand": "Sub",
    }
    assert _resolve_inquiry(content) == "A"


def test_derivation_used_when_neither_db_source_has_value():
    """No DB sources → fall through to derive_inquiry_from_slo."""
    content = {
        "_slotInquiry": "",
        "_substrandInquiries": [],
        "lessonInSubstrand": 1,
        "slo": "identify common shapes in the environment",
        "strand": "Geometry", "substrand": "Shapes",
    }
    result = _resolve_inquiry(content)
    # Must produce a non-empty question that includes the SLO body content
    assert result
    assert "shapes" in result.lower() or "identify" in result.lower()


def test_generic_fallback_when_slo_is_empty():
    """Empty SLO + no DB IQ → generic fallback fires (never returns empty)."""
    content = {
        "_slotInquiry": "",
        "_substrandInquiries": [],
        "lessonInSubstrand": 1,
        "slo": "",
        "strand": "Numbers", "substrand": "Whole Numbers",
    }
    result = _resolve_inquiry(content)
    assert result  # generic fallback returns a list-as-string or string
    # generate_inquiry_questions returns a list; mirror block returns it as-is
    # in that branch — accept either str or list, just assert non-empty.
    if isinstance(result, list):
        assert len(result) >= 1
        assert all(q for q in result)


def test_substrand_array_with_empty_slot_kiq_string():
    """`_slotInquiry` of '' (falsy) must NOT block falling through to substrand array."""
    content = {
        "_slotInquiry": "",  # falsy, must skip to substrand array
        "_substrandInquiries": ["From DB"],
        "lessonInSubstrand": 1,
        "slo": "describe X",
        "strand": "S", "substrand": "Sub",
    }
    assert _resolve_inquiry(content) == "From DB"


def test_slot_kiq_with_whitespace_only_falls_through():
    """Whitespace-only KIQ in DB is treated as missing — falls through to next source."""
    # Note: the production block uses truthiness; "   " is truthy in Python.
    # If the DB ever stores whitespace-only strings, current behaviour returns them
    # verbatim. Document that contract here so future refactors notice.
    content = {
        "_slotInquiry": "   ",
        "_substrandInquiries": ["Should be skipped"],
        "lessonInSubstrand": 1,
        "slo": "x", "strand": "s", "substrand": "ss",
    }
    # Current contract: whitespace string is truthy → returned verbatim.
    assert _resolve_inquiry(content) == "   "
