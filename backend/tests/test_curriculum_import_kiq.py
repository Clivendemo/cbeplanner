"""
Regression: curriculum-import pipeline must capture Key Inquiry Questions
from CSV columns and from KICD-style PDF/DOCX section text, and the saved
preview rows must carry an `inquiry_questions: [str]` array per row.

These are pure-function tests — no MongoDB, no FastAPI client.
"""
from curriculum_import import (
    parse_csv_content,
    extract_inquiry_questions_from_text,
    rows_to_csv,
    CSV_TEMPLATE_HEADERS,
)


# ---------------- CSV parser ----------------

def test_csv_parses_inquiry_questions_column():
    csv_text = (
        "strand_name,substrand_name,slo_name,inquiry_questions\n"
        "Cells,Cell Organelles,describe mitochondria,"
        "\"Why are mitochondria called the powerhouse?; How do they make ATP?\"\n"
    )
    res = parse_csv_content(csv_text)
    assert res.summary["total_rows"] == 1
    assert res.rows[0]["inquiry_questions"] == [
        "Why are mitochondria called the powerhouse?",
        "How do they make ATP?",
    ]


def test_csv_parses_kiq_alias_header():
    csv_text = (
        "Strand,Sub-strand,SLO,Key Inquiry Question(s)\n"
        "Numbers,Whole Numbers,count to 100,How can we count efficiently?\n"
    )
    res = parse_csv_content(csv_text)
    assert res.rows[0]["inquiry_questions"] == ["How can we count efficiently?"]


def test_csv_missing_iq_cell_yields_empty_list():
    csv_text = (
        "strand_name,substrand_name,slo_name\n"
        "S,SS,describe stuff\n"
    )
    res = parse_csv_content(csv_text)
    assert res.rows[0]["inquiry_questions"] == []


def test_csv_template_header_includes_inquiry_questions():
    assert "inquiry_questions" in CSV_TEMPLATE_HEADERS


def test_rows_to_csv_round_trip_preserves_iq():
    rows = [{
        "strand_name": "S", "substrand_name": "SS", "slo_name": "do x",
        "slo_description": "do x",
        "introduction_activities": [], "development_activities": [],
        "conclusion_activities": [], "extended_activities": [],
        "competencies": [], "values": [], "pcis": [],
        "assessment_methods": [], "learning_resources": [],
        "inquiry_questions": ["Why X?", "How does X work?"],
    }]
    csv_out = rows_to_csv(rows)
    assert "inquiry_questions" in csv_out
    assert "Why X?; How does X work?" in csv_out
    # Round-trip back through parser
    parsed = parse_csv_content(csv_out)
    assert parsed.rows[0]["inquiry_questions"] == ["Why X?", "How does X work?"]


# ---------------- KICD-style section extractor ----------------

def test_extract_inquiry_questions_bulleted_section():
    """Typical KICD design: header followed by bulleted questions."""
    text = """
    Suggested Learning Experiences
    The learner is guided to:
    - Observe a leaf
    - Discuss photosynthesis

    Key Inquiry Questions:
    - How does a plant make its own food?
    - Why is sunlight important to plants?
    - What happens when plants are kept in the dark?

    Core Competencies:
    Critical thinking
    """
    qs = extract_inquiry_questions_from_text(text)
    assert qs == [
        "How does a plant make its own food?",
        "Why is sunlight important to plants?",
        "What happens when plants are kept in the dark?",
    ]


def test_extract_inquiry_questions_singular_inline():
    """KICD often writes 'Key Inquiry Question:' (singular) as one inline line."""
    text = """
    Key Inquiry Question: How can we measure the volume of irregular objects?
    Core competencies: Critical Thinking
    """
    qs = extract_inquiry_questions_from_text(text)
    assert qs == ["How can we measure the volume of irregular objects?"]


def test_extract_inquiry_questions_multiple_on_one_line():
    """Inline run-on: 'Why X? How Y? When Z?' all on a single line."""
    text = """
    Key Inquiry Question(s): Why study Geography? How does Geography affect daily life?
    Values: Respect
    """
    qs = extract_inquiry_questions_from_text(text)
    assert qs == [
        "Why study Geography?",
        "How does Geography affect daily life?",
    ]


def test_extract_inquiry_questions_no_section_returns_empty():
    text = "Some random text with no inquiry section at all."
    assert extract_inquiry_questions_from_text(text) == []


def test_extract_inquiry_questions_dedupes_and_caps():
    """Duplicates must be removed; absurdly long question lists capped at 8."""
    questions = "\n".join(f"- Why is question {i} important?" for i in range(15))
    # Add one duplicate
    text = f"Key Inquiry Questions:\n{questions}\n- Why is question 0 important?\nAssessment:"
    qs = extract_inquiry_questions_from_text(text)
    assert len(qs) <= 8
    # No duplicates (lowercase comparison)
    assert len({q.lower() for q in qs}) == len(qs)


def test_extract_inquiry_questions_filters_obvious_garbage():
    """Lines that aren't questions and aren't preceded by a question word are dropped."""
    text = """
    Key Inquiry Question(s):
    - How does the water cycle work?
    - Lorem ipsum dolor sit amet random text fragment
    - Why is rainfall variable across regions?
    Core competencies: Critical Thinking
    """
    qs = extract_inquiry_questions_from_text(text)
    assert "How does the water cycle work?" in qs
    assert "Why is rainfall variable across regions?" in qs
    assert all("lorem" not in q.lower() for q in qs)
