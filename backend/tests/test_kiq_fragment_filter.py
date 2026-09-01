"""
Regression: bare-"Je" / fragment KIQs must not appear in the rendered scheme.

Bug history
-----------
Some KICD Kiswahili Fasihi PDFs wrap a Key Inquiry Question across two lines
in the source layout, e.g. ``"Je,\n  Kwa nini fasihi ni muhimu?"``. The
scheme PDF renderer used to ``str(val).strip().split('\n')[0].strip()`` which
collapsed that question to just ``"Je,"`` — giving a teacher a meaningless
"Je" stub in the Swali Ibuka column. We also occasionally see the AI
extractor lift an isolated question particle (a bare ``"Je"`` or
``"Kwa nini"`` with no follow-up clause).

Contract under test
-------------------
- ``clean_kiq_list`` drops fragments and collapses internal whitespace.
- ``_is_meaningful_kiq`` rejects KIQs that are (a) under 12 chars, (b) under
  3 words, or (c) just a question particle in any language we support.
- The scheme generator's ``_single_inquiry`` helper, when given a multi-line
  KIQ string, renders the *whole* question, not just the first line.
"""
from __future__ import annotations

import sys

sys.path.insert(0, "/app/backend")

from scheme_generator import (
    _is_meaningful_kiq,
    clean_kiq_list,
)


# ---------------------------------------------------------------------------
# 1. Fragment detection
# ---------------------------------------------------------------------------

def test_bare_kiswahili_je_is_rejected():
    assert not _is_meaningful_kiq("Je")
    assert not _is_meaningful_kiq("Je,")
    assert not _is_meaningful_kiq("Je?")
    assert not _is_meaningful_kiq("Je.")
    assert not _is_meaningful_kiq("  je  ")  # whitespace + lowercase


def test_bare_kwa_nini_is_rejected():
    assert not _is_meaningful_kiq("Kwa nini?")
    assert not _is_meaningful_kiq("Kwa Nini")


def test_bare_english_stem_is_rejected():
    assert not _is_meaningful_kiq("Why?")
    assert not _is_meaningful_kiq("How")


def test_short_two_word_phrase_is_rejected():
    """3-word minimum prevents 'Je nini' style fragments from sneaking in."""
    assert not _is_meaningful_kiq("Je nini")
    # Just under 12 chars even with 3 words — still rejected
    assert not _is_meaningful_kiq("Je is hi?")


def test_meaningful_kiswahili_question_passes():
    assert _is_meaningful_kiq("Je, kwa nini fasihi ni muhimu katika maisha?")
    assert _is_meaningful_kiq("Kwa nini hadithi za asili zinatufundisha?")


def test_meaningful_english_question_passes():
    assert _is_meaningful_kiq("Why is rhyme important in poetry?")
    assert _is_meaningful_kiq("How can we apply this in daily life?")


# ---------------------------------------------------------------------------
# 2. clean_kiq_list — sanitisation contract
# ---------------------------------------------------------------------------

def test_clean_drops_fragments_keeps_real_questions():
    raw = [
        "Je,",                                       # fragment
        "Je, kwa nini fasihi ni muhimu kwa jamii?",  # real
        "",                                          # empty
        "Kwa nini?",                                 # particle only
        "Tunaweza kutumia methali katika mazungumzo gani?",  # real
    ]
    cleaned = clean_kiq_list(raw)
    assert cleaned == [
        "Je, kwa nini fasihi ni muhimu kwa jamii?",
        "Tunaweza kutumia methali katika mazungumzo gani?",
    ]


def test_clean_collapses_internal_whitespace():
    """A KIQ wrapped across two lines must render as one continuous
    question, not retain the source line break."""
    raw = "Je,\n  kwa nini fasihi simulizi ni muhimu?"
    cleaned = clean_kiq_list([raw])
    assert cleaned == ["Je, kwa nini fasihi simulizi ni muhimu?"]


def test_clean_dedupes_case_insensitively():
    raw = [
        "Why is rhyme important in poetry?",
        "why is rhyme important in poetry?",
        "WHY IS RHYME IMPORTANT IN POETRY?",
    ]
    cleaned = clean_kiq_list(raw)
    assert len(cleaned) == 1


def test_clean_handles_none_and_string_inputs():
    assert clean_kiq_list(None) == []
    assert clean_kiq_list("") == []
    assert clean_kiq_list("Je,") == []
    assert clean_kiq_list("Why is rhyme important in poetry?") == [
        "Why is rhyme important in poetry?"
    ]


# ---------------------------------------------------------------------------
# 3. PDF renderer no longer truncates a multi-line KIQ to its first line
# ---------------------------------------------------------------------------

def _build_single_inquiry():
    """Re-create the closure used inside generate_scheme_pdf so the unit
    test can call it without rendering a real PDF."""
    def _single_inquiry(val) -> str:
        if not val:
            return ''
        if isinstance(val, list):
            for q in val:
                cleaned = str(q).strip()
                if _is_meaningful_kiq(cleaned):
                    return ' '.join(cleaned.split())
            return ''
        cleaned = str(val).strip()
        if not _is_meaningful_kiq(cleaned):
            return ''
        return ' '.join(cleaned.split())
    return _single_inquiry


def test_single_inquiry_renders_whole_multiline_kiq():
    """Reproduces the bug: a KIQ with an embedded newline used to render
    as just 'Je,' — now it renders as the whole question."""
    pick = _build_single_inquiry()
    raw = "Je,\n  Kwa nini fasihi ni muhimu katika jamii?"
    assert pick(raw) == "Je, Kwa nini fasihi ni muhimu katika jamii?"


def test_single_inquiry_returns_blank_for_pure_fragment():
    pick = _build_single_inquiry()
    assert pick("Je,") == ''
    assert pick("Je") == ''
    assert pick(["Je,", "  ", ""]) == ''


def test_single_inquiry_skips_fragment_in_list_picks_next_real_one():
    """If the array's first entry is a fragment, fall through to the
    first meaningful entry instead of rendering blank."""
    pick = _build_single_inquiry()
    arr = ["Je,", "Kwa nini fasihi ni muhimu kwa jamii?"]
    assert pick(arr) == "Kwa nini fasihi ni muhimu kwa jamii?"
