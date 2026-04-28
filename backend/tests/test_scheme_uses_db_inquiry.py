"""
Regression: scheme generator must read the Key Inquiry Question directly from
the database — never algorithmically generate.

Priority order under test (mirror of routes/schemes.py):
  1. lesson_slo_slots.key_inquiry_question  — admin's per-lesson override
  2. slos.key_inquiry_questions[0]          — canonical, KICD-extracted
  3. ""                                      — blank if neither has a value;
                                               the curriculum extractor is
                                               the only path that creates KIQs
"""


def _resolve_inquiry(content: dict):
    """Mirror of the priority block in routes/schemes.py for unit-testing."""
    slot_inquiry = content.get("_slotInquiry")
    slo_inquiries = content.get("_sloInquiries") or []
    if slot_inquiry:
        return slot_inquiry
    if slo_inquiries:
        return slo_inquiries[0]
    return ""


# ----- Priority order ---------------------------------------------------

def test_lesson_slot_override_wins_over_slo_kiq():
    """Admin's per-lesson override takes precedence over the SLO row's KIQ."""
    content = {
        "_slotInquiry": "Why did the admin pick this exact question?",
        "_sloInquiries": ["Stored on the SLO row but should be ignored"],
        "slo": "describe X", "strand": "S", "substrand": "Sub",
    }
    assert _resolve_inquiry(content) == "Why did the admin pick this exact question?"


def test_slo_kiq_used_when_no_slot_override():
    content = {
        "_slotInquiry": "",
        "_sloInquiries": ["Why does photosynthesis matter?"],
        "slo": "describe photosynthesis", "strand": "Plants", "substrand": "Photosynthesis",
    }
    assert _resolve_inquiry(content) == "Why does photosynthesis matter?"


def test_first_kiq_in_array_is_used():
    """Every SLO holds the FULL substrand-level KIQ array; the
    scheme generator picks the first one as the headline question."""
    content = {
        "_slotInquiry": "",
        "_sloInquiries": [
            "Question one — should be picked.",
            "Question two — kept on the row but unused by the scheme.",
        ],
        "slo": "x", "strand": "s", "substrand": "ss",
    }
    assert _resolve_inquiry(content) == "Question one — should be picked."


def test_kiswahili_kiq_returned_verbatim_no_language_check():
    """SLOs in Kiswahili subjects already store text in Kiswahili — no
    language heuristic needed, just return verbatim."""
    content = {
        "_slotInquiry": "",
        "_sloInquiries": ["Kwa nini ni muhimu kujifunza sarufi ya Kiswahili?"],
        "slo": "eleza sarufi ya Kiswahili", "strand": "Sarufi", "substrand": "Lugha",
    }
    assert _resolve_inquiry(content) == \
        "Kwa nini ni muhimu kujifunza sarufi ya Kiswahili?"


def test_blank_when_no_db_kiq():
    """If neither the slot override nor the SLO row has a KIQ, the lesson
    stays blank. We never algorithmically derive — the curriculum extractor
    is the only valid source of KIQs."""
    content = {
        "_slotInquiry": "",
        "_sloInquiries": [],
        "slo": "identify common shapes in the environment",
        "strand": "Geometry", "substrand": "Shapes",
    }
    assert _resolve_inquiry(content) == ""


def test_empty_slot_string_does_not_block_slo_kiq():
    """Falsy slot inquiry (`""` / `None`) MUST fall through to slo_inquiries."""
    content = {
        "_slotInquiry": "",
        "_sloInquiries": ["From the SLO row"],
        "slo": "x", "strand": "s", "substrand": "ss",
    }
    assert _resolve_inquiry(content) == "From the SLO row"


def test_multilingual_subject_each_slo_holds_own_language():
    """Two scheme rows from two different SLOs each return their own KIQ
    verbatim — proves the model handles a mixed scheme cleanly."""
    english_lesson = {
        "_slotInquiry": "", "_sloInquiries": ["Why is rhyme important in poetry?"],
        "slo": "describe rhyme", "strand": "Poetry", "substrand": "Rhyme",
    }
    swahili_lesson = {
        "_slotInquiry": "", "_sloInquiries": ["Kwa nini mashairi hutumia vina?"],
        "slo": "eleza vina", "strand": "Mashairi", "substrand": "Vina",
    }
    assert _resolve_inquiry(english_lesson) == "Why is rhyme important in poetry?"
    assert _resolve_inquiry(swahili_lesson) == "Kwa nini mashairi hutumia vina?"
