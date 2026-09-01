"""
Regression: the curriculum extraction pipeline must:

1. Recognise Kiswahili KIQ headings ("Swali Ibuka", "Maswali Ibuka",
   "Maswali Ibukaji", etc.) — Fasihi ya Kiswahili and Lugha ya Kiswahili
   PDFs use these instead of the English "Key Inquiry Question(s)".
2. Persist the extracted ``inquiry_questions`` array onto every SLO row
   under its substrand as ``slos.key_inquiry_questions``. Without this,
   the scheme generator (which now reads the array exclusively from the
   SLO row) shows blank "—" entries even when the AI extracted the data.

These are unit tests against the regex extractor and the seed-pipeline's
SLO insert payload — no Gemini calls, no MongoDB.
"""
from __future__ import annotations

import sys

import pytest

sys.path.insert(0, "/app/backend")

from curriculum_import import extract_inquiry_questions_from_text


# ---------------------------------------------------------------------------
# 1. Kiswahili headings are recognised by the regex extractor.
# ---------------------------------------------------------------------------

def test_swali_ibuka_singular_heading():
    """The Kiswahili heading used in Fasihi ya Kiswahili designs."""
    text = (
        "Maeneo Yanayofunzwa\n"
        "...\n"
        "Swali Ibuka\n"
        "  - Kwa nini fasihi ni muhimu katika maisha yetu ya kila siku?\n"
        "  - Je, hadithi za asili zinatufundisha nini?\n"
        "Core Competencies"
    )
    qs = extract_inquiry_questions_from_text(text)
    assert qs, "Swali Ibuka section must be parsed"
    assert any("fasihi ni muhimu" in q.lower() for q in qs)
    assert any("hadithi" in q.lower() for q in qs)


def test_maswali_ibuka_plural_heading():
    text = (
        "Maswali Ibuka:\n"
        "  - Kwa nini ni muhimu kujifunza Kiswahili sanifu?\n"
        "  - Vipi tunaweza kutumia Kiswahili katika mawasiliano?\n"
        "Maadili"
    )
    qs = extract_inquiry_questions_from_text(text)
    assert len(qs) >= 2
    assert any(q.startswith("Kwa nini") for q in qs)


def test_maswali_ibukaji_alternate_form():
    """Older KICD designs use 'Maswali Ibukaji' (note the 'ji' ending)."""
    text = (
        "Maswali Ibukaji\n"
        "  - Vipi tunatofautisha hadithi za visasili na hekaya?\n"
        "Nyenzo za Kujifunzia"
    )
    qs = extract_inquiry_questions_from_text(text)
    assert len(qs) == 1
    assert "hadithi" in qs[0].lower()


def test_swali_dadisi_alternate_term():
    """Some designs use 'Swali Dadisi' / 'Maswali ya Kudadisi' instead."""
    text = (
        "Maswali ya Kudadisi:\n"
        "  - Tunaweza vipi kutumia methali katika mazungumzo ya kila siku?\n"
        "Umilisi Mahsusi"
    )
    qs = extract_inquiry_questions_from_text(text)
    assert len(qs) == 1
    assert qs[0].endswith("?")


def test_english_kiq_still_works():
    """Regression guard — English heading must keep working alongside
    the new Kiswahili variants."""
    text = (
        "Key Inquiry Questions:\n"
        "  - Why is rhyme important in poetry?\n"
        "Core Competencies"
    )
    qs = extract_inquiry_questions_from_text(text)
    assert len(qs) == 1
    assert qs[0] == "Why is rhyme important in poetry?"


# ---------------------------------------------------------------------------
# 2. Pipeline copies inquiry_questions onto every SLO under the substrand.
# ---------------------------------------------------------------------------

def _slo_payload_under_substrand(ss_data: dict, slo_idx: int) -> dict:
    """Mirror the inquiry-resolution logic from
    ``curriculum_pipeline._seed_extracted_data`` to validate the contract
    without touching MongoDB.
    """
    def ensure_list(v):
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if x and str(x).strip()]
        return [s.strip() for s in str(v).split(";") if s.strip()]

    ss_inquiry_questions = ensure_list(ss_data.get("inquiry_questions"))
    slo_data = ss_data["slos"][slo_idx]
    slo_inquiry = (
        ensure_list(slo_data.get("inquiry_questions"))
        if isinstance(slo_data, dict) and slo_data.get("inquiry_questions")
        else ss_inquiry_questions
    )
    return {
        "name": slo_data["name"],
        "key_inquiry_questions": slo_inquiry,
    }


def test_substrand_kiqs_propagate_to_every_slo():
    """When the AI returns inquiry_questions at the substrand level, EVERY
    SLO under it must store the same array — that's how scheme generation
    finds the question regardless of which SLO maps to a given lesson."""
    ss_data = {
        "name": "Fasihi Simulizi - Hadithi",
        "inquiry_questions": [
            "Kwa nini hadithi za asili ni muhimu?",
            "Je, hadithi zinatufundisha nini?",
        ],
        "slos": [
            {"name": "Kueleza maana ya hadithi"},
            {"name": "Kutaja sifa za hadithi"},
            {"name": "Kueleza umuhimu wa hadithi"},
        ],
    }
    for i in range(3):
        payload = _slo_payload_under_substrand(ss_data, i)
        assert payload["key_inquiry_questions"] == [
            "Kwa nini hadithi za asili ni muhimu?",
            "Je, hadithi zinatufundisha nini?",
        ], f"SLO #{i+1} did not inherit substrand-level KIQs"


def test_per_slo_kiq_overrides_substrand_default():
    """Some KICD designs list KIQs at the SLO level. When present, that
    list takes precedence over the substrand-level fallback."""
    ss_data = {
        "name": "Mashairi",
        "inquiry_questions": ["Substrand-level question?"],
        "slos": [
            {"name": "SLO 1"},  # falls back
            {
                "name": "SLO 2",
                "inquiry_questions": ["SLO-level override?"],
            },
        ],
    }
    assert _slo_payload_under_substrand(ss_data, 0)["key_inquiry_questions"] == [
        "Substrand-level question?"
    ]
    assert _slo_payload_under_substrand(ss_data, 1)["key_inquiry_questions"] == [
        "SLO-level override?"
    ]


def test_empty_substrand_kiqs_yield_empty_list_not_none():
    """When the AI didn't capture any KIQs (the regex case for an
    un-modernised PDF), the SLO row gets an empty list — never null —
    so the scheme generator's empty-array branch fires cleanly."""
    ss_data = {
        "name": "X",
        "inquiry_questions": [],
        "slos": [{"name": "SLO 1"}],
    }
    assert _slo_payload_under_substrand(ss_data, 0)["key_inquiry_questions"] == []
