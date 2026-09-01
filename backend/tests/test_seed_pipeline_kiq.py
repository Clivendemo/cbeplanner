"""
Regression: the AI extractor → seed-script-generator pipeline must carry
Key Inquiry Questions all the way from the extracted JSON into the generated
seed script's SUBJECT_DATA literal AND into the runtime
db.learning_activities.insert_one(...) call.

Pure-function tests — no MongoDB, no Gemini API.
"""
import os
import sys
import tempfile

# Make the scripts/ dir importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from seed_script_generator import _format_subject_data, generate_seed_script


SAMPLE_EXTRACTED = {
    "grade": "Grade 10",
    "subject_name": "Biology",
    "strands": [
        {
            "name": "Cells",
            "substrands": [
                {
                    "name": "Cell Organelles",
                    "lessons": 4,
                    "slos": [
                        {"name": "describe mitochondria", "description": "describe mitochondria"}
                    ],
                    "learning_activities": {
                        "introduction": "Recap previous lesson",
                        "development": "Observe slides",
                        "conclusion": "Quick quiz",
                        "extended": "Research project on cell theory",
                        "resources": ["Microscope", "Slides"],
                        "assessment": ["Observation"],
                    },
                    "competencies": ["Critical Thinking"],
                    "values": ["Responsibility"],
                    "pcis": ["Health Education"],
                    "inquiry_questions": [
                        "Why are mitochondria called the powerhouse of the cell?",
                        "How do organelles work together to keep the cell alive?",
                    ],
                }
            ],
        }
    ],
}


def test_format_subject_data_includes_inquiry_questions():
    """The Python dict literal embedded in the generated script must include the IQs."""
    out = _format_subject_data("Biology", SAMPLE_EXTRACTED["strands"])
    assert '"inquiry_questions"' in out
    assert "Why are mitochondria called the powerhouse of the cell?" in out
    assert "How do organelles work together to keep the cell alive?" in out


def test_format_subject_data_empty_inquiry_questions_when_missing():
    """Substrands with no IQ key emit an empty array, not a missing field."""
    strands = [
        {
            "name": "S",
            "substrands": [
                {
                    "name": "SS", "lessons": 2, "slos": [],
                    "learning_activities": {},
                    "competencies": [], "values": [], "pcis": [],
                }
            ],
        }
    ]
    out = _format_subject_data("X", strands)
    assert '"inquiry_questions": []' in out


def test_generated_seed_script_has_runtime_insert_with_iq_field():
    """The full generated .py script must include the runtime insert_one call
    that writes learning_activities.inquiry_questions to MongoDB."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
        out_path = f.name

    try:
        generate_seed_script(SAMPLE_EXTRACTED, out_path)
        with open(out_path) as f:
            source = f.read()

        # The runtime insert MUST set inquiry_questions
        assert '"inquiry_questions": ensure_list(ss_data.get("inquiry_questions"))' in source

        # The literal data section MUST carry the actual questions through
        assert "Why are mitochondria called the powerhouse of the cell?" in source

        # Generated script must remain syntactically valid Python
        compile(source, out_path, "exec")
    finally:
        os.unlink(out_path)


def test_generated_seed_script_dict_literal_parses_back_to_json_with_iq():
    """Round-trip: extract the SUBJECT_DATA literal from the generated script
    and ensure inquiry_questions is preserved."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
        out_path = f.name

    try:
        generate_seed_script(SAMPLE_EXTRACTED, out_path)
        with open(out_path) as f:
            source = f.read()

        # Pull SUBJECT_DATA out by exec-ing the literal
        # (safe — generated content only)
        ns: dict = {}
        # Slice from "SUBJECT_DATA = " to the next blank line + "# ====" marker
        start = source.index("SUBJECT_DATA = ")
        end = source.index("# HELPER FUNCTIONS")
        snippet = source[start:end]
        exec(snippet, ns)
        subject = ns["SUBJECT_DATA"]

        ss = subject["strands"][0]["substrands"][0]
        assert ss["inquiry_questions"] == [
            "Why are mitochondria called the powerhouse of the cell?",
            "How do organelles work together to keep the cell alive?",
        ]
    finally:
        os.unlink(out_path)
