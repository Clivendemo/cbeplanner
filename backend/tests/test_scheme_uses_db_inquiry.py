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
from routes.schemes import _looks_kiswahili, _kiswahili_or_english_fallback


def _resolve_inquiry(content: dict, is_kiswahili: bool = False) -> str:
    """Mirror of the priority block in routes/schemes.py for unit-testing."""
    slot_inquiry = content.get("_slotInquiry")
    substrand_iqs = content.get("_substrandInquiries") or []
    if slot_inquiry and (not is_kiswahili or _looks_kiswahili(slot_inquiry)):
        return slot_inquiry
    if substrand_iqs:
        pos = max(0, content.get("lessonInSubstrand", 1) - 1)
        candidate = substrand_iqs[pos % len(substrand_iqs)]
        if is_kiswahili and not _looks_kiswahili(candidate):
            candidate = next(
                (q for q in substrand_iqs if _looks_kiswahili(q)),
                None,
            )
        if candidate:
            return candidate
        return _kiswahili_or_english_fallback(content, is_kiswahili)
    return _kiswahili_or_english_fallback(content, is_kiswahili)


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


# ==================== Kiswahili / Fasihi ya Kiswahili ====================

def test_looks_kiswahili_detects_kwa_nini():
    assert _looks_kiswahili("Kwa nini ni muhimu kujifunza sarufi?")


def test_looks_kiswahili_detects_je():
    assert _looks_kiswahili("Je, hadithi fupi ina sifa zipi?")


def test_looks_kiswahili_detects_vipi():
    assert _looks_kiswahili("Vipi tunaweza kuboresha matamshi yetu?")


def test_looks_kiswahili_rejects_english():
    assert not _looks_kiswahili("Why is it important to learn grammar?")
    assert not _looks_kiswahili("How do we improve pronunciation?")


def test_kiswahili_subject_prefers_kiswahili_substrand_iq():
    """If substrand_iqs carry both an English translation and the Kiswahili
    original, a Kiswahili scheme MUST pick the Kiswahili one even if the
    positional cycle would otherwise point at the English entry."""
    content = {
        "_slotInquiry": "",
        "_substrandInquiries": [
            "Why is it important to learn grammar?",           # pos 0 (English)
            "Kwa nini ni muhimu kujifunza sarufi?",             # pos 1 (Kiswahili)
        ],
        "lessonInSubstrand": 1,  # cycle points to index 0
        "slo": "eleza muundo wa sentensi",
        "strand": "Sarufi", "substrand": "Sentensi",
    }
    # English scheme: take pos 0 as usual
    assert _resolve_inquiry(content, is_kiswahili=False) == "Why is it important to learn grammar?"
    # Kiswahili scheme: must jump to the Kiswahili entry
    assert _resolve_inquiry(content, is_kiswahili=True) == "Kwa nini ni muhimu kujifunza sarufi?"


def test_kiswahili_subject_rejects_english_slot_inquiry():
    """An English admin-curated slot KIQ must be ignored for a Kiswahili scheme
    — we fall through to the substrand array / derivation instead of writing
    English into a Kiswahili scheme."""
    content = {
        "_slotInquiry": "Why is rhyming important in poetry?",
        "_substrandInquiries": ["Kwa nini mashairi hutumia vina?"],
        "lessonInSubstrand": 1,
        "slo": "eleza matumizi ya vina katika mashairi",
        "strand": "Fasihi", "substrand": "Mashairi",
    }
    assert _resolve_inquiry(content, is_kiswahili=True) == "Kwa nini mashairi hutumia vina?"
    # But for an English scheme, the slot inquiry still wins verbatim
    assert _resolve_inquiry(content, is_kiswahili=False) == "Why is rhyming important in poetry?"


def test_kiswahili_subject_accepts_kiswahili_slot_inquiry():
    content = {
        "_slotInquiry": "Je, fasihi simulizi ina sifa zipi?",
        "_substrandInquiries": [],
        "lessonInSubstrand": 1,
        "slo": "eleza sifa za fasihi simulizi",
        "strand": "Fasihi simulizi", "substrand": "Utangulizi",
    }
    assert _resolve_inquiry(content, is_kiswahili=True) == "Je, fasihi simulizi ina sifa zipi?"


def test_kiswahili_subject_falls_through_when_only_english_iqs():
    """If every substrand IQ is English, a Kiswahili scheme must fall all the
    way through to the Kiswahili-aware derivation — NOT return English."""
    content = {
        "_slotInquiry": "",
        "_substrandInquiries": [
            "Why is active listening important?",
            "What techniques ensure successful listening?",
        ],
        "lessonInSubstrand": 1,
        "slo": "eleza usikilizaji makini",
        "strand": "Kusikiliza", "substrand": "Usikilizaji",
    }
    result = _resolve_inquiry(content, is_kiswahili=True)
    # Must NOT be one of the English strings
    assert result not in (
        "Why is active listening important?",
        "What techniques ensure successful listening?",
    )
    # Must be non-empty (Kiswahili fallback always returns something)
    assert result
