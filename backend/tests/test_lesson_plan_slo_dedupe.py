"""
Regression: lesson plan PDF must not render triplicate SLO text.

The slot schema commonly stores the same text in both `outcome` and
`description`, and the slot outcome is often a paraphrase of the parent
SLO — this resulted in the SPECIFIC LEARNING OUTCOME section looking
like the same text was printed three times.

Tests the dedupe helper directly (pure function, no DB/PDF build needed).
"""
from pdf_generator import dedupe_lesson_specific_outcomes


def test_exact_duplicates_within_list_removed():
    out = dedupe_lesson_specific_outcomes(
        ['Identify common proper nouns', 'Identify common proper nouns'],
        'Completely different SLO',
    )
    assert out == ['Identify common proper nouns']


def test_matches_primary_slo_are_removed():
    out = dedupe_lesson_specific_outcomes(
        ['Identify common proper nouns', 'Use proper nouns in sentences'],
        'Identify common proper nouns',
    )
    assert out == ['Use proper nouns in sentences']


def test_prefix_and_containment_deduped():
    # Primary contains the slot outcome text -> slot dropped
    out = dedupe_lesson_specific_outcomes(
        ['Identify', 'Use proper nouns'],
        'Identify common proper nouns in a paragraph',
    )
    assert 'Identify' not in out
    assert 'Use proper nouns' in out


def test_case_and_whitespace_insensitive():
    out = dedupe_lesson_specific_outcomes(
        ['identify  COMMON   proper  nouns'],
        'Identify common proper nouns',
    )
    assert out == []


def test_distinct_outcomes_preserved():
    out = dedupe_lesson_specific_outcomes(
        ['Explain punctuation rules', 'Apply punctuation in writing'],
        'Identify common proper nouns',
    )
    assert out == ['Explain punctuation rules', 'Apply punctuation in writing']


def test_empty_and_blank_entries_dropped():
    out = dedupe_lesson_specific_outcomes(
        ['', '   ', 'Valid outcome'],
        'Different SLO',
    )
    assert out == ['Valid outcome']


def test_primary_na_does_not_filter_valid_outcomes():
    """If primary is 'N/A', it must not accidentally match/drop outcomes."""
    out = dedupe_lesson_specific_outcomes(
        ['Outcome A', 'Outcome B'],
        'N/A',
    )
    assert out == ['Outcome A', 'Outcome B']
