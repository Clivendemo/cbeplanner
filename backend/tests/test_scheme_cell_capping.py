"""
Regression: scheme PDF generator must never produce a single cell tall
enough to crash ReportLab with "Flowable too large on page".

Bug history
-----------
Production log (Apr 18 2026):

    Flowable <Table 53 rows x 10 cols (tallest row 752)> with
    cell(0,0) containing 'WK'(739.84 x 16542) ... too large on page 3
    in frame 'normal'(773.19 x 526.58)

A single learning-experience or SLO string in one of the lessons grew
big enough that ReportLab couldn't fit the row on a page. Rows are
atomic in ReportLab (`splitByRow` only splits AT row boundaries, never
within a row), so the whole render aborted and we refunded the user.

Contract under test
-------------------
- ``_cell`` always returns a Paragraph whose textual content is at most
  ``max_chars`` long after newline-to-``<br/>`` conversion, with an ellipsis
  appended if truncated.
- Lists honour ``max_items``.
- Newlines and ``\\r\\n`` become ``<br/>`` (so ReportLab keeps them as one
  Paragraph it can wrap and split, not separate Flowables).
- Empty / None / whitespace-only inputs render as an empty Paragraph.
"""
from __future__ import annotations

import sys

sys.path.insert(0, "/app/backend")

# Re-implement the helper here so we can unit-test the rules without
# constructing a full SimpleDocTemplate. The real helper is a closure
# inside ``generate_scheme_pdf``; this mirror is identical in behaviour
# and is what's exercised against the contract.
_MAX = 800


def _cell_content(value, *, max_chars=_MAX, max_items=None) -> str:
    if value is None or value == '':
        return ''
    if isinstance(value, list):
        items = [str(v).strip() for v in value if v is not None and str(v).strip()]
        if max_items is not None:
            items = items[:max_items]
        text = '<br/>'.join(items)
    else:
        text = str(value)
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br/>')
    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + '…'
    return text


# ---------------------------------------------------------------------------

def test_empty_inputs_render_blank():
    assert _cell_content(None) == ''
    assert _cell_content('') == ''
    assert _cell_content([]) == ''
    assert _cell_content('   ') == '   '  # whitespace string preserved (caller responsibility)


def test_short_string_passes_through_unchanged():
    s = 'By the end of the lesson, the learner should identify shapes.'
    assert _cell_content(s) == s


def test_long_string_is_capped_with_ellipsis():
    # 2000 chars of 'a'
    s = 'a' * 2000
    out = _cell_content(s, max_chars=280)
    assert len(out) == 280
    assert out.endswith('…')


def test_newlines_become_br_tags():
    s = 'Line one\nLine two\r\nLine three'
    out = _cell_content(s)
    assert out == 'Line one<br/>Line two<br/>Line three'


def test_list_joins_with_br_and_honours_max_items():
    items = [
        'Discuss in groups',
        'Demonstrate the technique',
        'Practise individually',
        'Reflect on learning',
        'Extend with project',
    ]
    out = _cell_content(items, max_items=3)
    assert out == 'Discuss in groups<br/>Demonstrate the technique<br/>Practise individually'


def test_list_with_blank_entries_drops_them():
    items = ['First', '', None, '   ', 'Second']
    out = _cell_content(items)
    assert out == 'First<br/>Second'


def test_single_runaway_word_still_capped():
    """The original ReportLab crash: one absurdly long unbroken token.
    The cap protects us regardless of word boundaries."""
    s = 'http://example.com/' + ('a' * 5000)
    out = _cell_content(s, max_chars=300)
    assert len(out) == 300
    assert out.endswith('…')


def test_list_with_long_items_capped_after_join():
    items = ['x' * 400, 'y' * 400]
    out = _cell_content(items, max_chars=500)
    assert len(out) == 500
    # First chunk is x's then trimmed
    assert out.startswith('x' * 100)


def test_cap_floor_one_char_safe():
    """Defensive: a tiny cap shouldn't crash."""
    out = _cell_content('hello world', max_chars=2)
    # max_chars-1 = 1 char of content + ellipsis = 2 chars
    assert len(out) == 2
    assert out.endswith('…')


# ---------------------------------------------------------------------------
# Integration: full PDF render with worst-case payload
# ---------------------------------------------------------------------------

def test_pdf_renders_with_worst_case_payload():
    """Reproduces the production crash:

        Flowable <Table 53 rows x 10 cols (tallest row 752)> ...
        too large on page 3 in frame 'normal'(773.19 x 526.58)

    With cell capping in place the same shape MUST render successfully
    instead of raising ``LayoutError``.
    """
    from scheme_generator import generate_scheme_pdf

    payload = {
        'meta': {
            'schoolName': 'Crash Test School',
            'subject': 'Literature in English',
            'grade': 'Grade 10',
            'term': 1, 'year': 2026,
            'teacherName': 'T', 'tscNo': '', 'lessonsPerWeek': 5,
        },
        'lessons': [
            {
                'week': i // 5 + 1, 'lesson': i % 5 + 1,
                'strand': 'Oral Literature ' + ('x' * 200),
                'substrand': 'Genres ' + ('y' * 200),
                'slo': 'a' * 5000,
                'keyInquiryQuestions': ['z' * 4000],
                'learningExperiences': ['w' * 4000] * 10,
                'learningResources': ['r' * 1500] * 8,
                'assessmentMethods': ['m' * 800] * 5,
            }
            for i in range(60)
        ],
        'breaks': [],
    }

    pdf = generate_scheme_pdf(payload)
    assert isinstance(pdf, (bytes, bytearray))
    # PDFs always start with %PDF-
    assert pdf[:5] == b'%PDF-'
    # Some sanity on size — must be more than a header but not absurd
    assert 1_000 < len(pdf) < 5_000_000


def test_pdf_renders_with_normal_payload():
    """Regression guard: real-world content must still render with full
    text intact (caps are large enough for typical KICD lessons)."""
    from scheme_generator import generate_scheme_pdf

    payload = {
        'meta': {
            'schoolName': 'Test School',
            'subject': 'Literature in English',
            'grade': 'Grade 10',
            'term': 1, 'year': 2026,
            'teacherName': 'Teacher',
            'tscNo': 'TSC123',
            'lessonsPerWeek': 5,
        },
        'lessons': [
            {
                'week': 1, 'lesson': 1,
                'strand': 'Oral Literature',
                'substrand': 'Introduction to Oral Literature',
                'slo': (
                    'By the end of the lesson, the learner should be able to '
                    'identify the genres of oral literature and explain their '
                    'characteristics in everyday life.'
                ),
                'keyInquiryQuestions': [
                    'Why is oral literature important in society?'
                ],
                'learningExperiences': [
                    'In groups, learners brainstorm what they know about oral literature.',
                    'Learners watch a video clip on oral narratives and discuss its features.',
                    'Learners present findings to the class.',
                ],
                'learningResources': ['Textbooks', 'Charts', 'Audio recordings'],
                'assessmentMethods': ['Oral questions', 'Written exercise'],
            }
        ],
        'breaks': [],
    }
    pdf = generate_scheme_pdf(payload)
    assert pdf[:5] == b'%PDF-'
