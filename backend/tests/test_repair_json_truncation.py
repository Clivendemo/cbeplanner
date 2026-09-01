"""
Regression: ``repair_json`` must recover from the failure modes that
have actually killed extraction jobs in production.

Triggering bug:
  ERROR:pipeline:[Job ...] Failed: ValueError: Cannot repair JSON.
  First 200 chars: ```json
  {
    "grade": "Grade 10",
    "subject_name": "FASIHI YA KISWAHILI",
    "strands": [
      {
        "name": "Misingi ya Fasihi",
        ...
        "name": "Fasihi Simulizi - D     <-- truncated mid-string

Root cause was Gemini hitting MAX_TOKENS on dense KICD curriculum PDFs
(Kiswahili / Fasihi tables) and the repair function clipping at the last
``}`` instead of letting the bracket-balancer reconstruct the structure.
"""
import pytest

from curriculum_pipeline import repair_json


def test_repair_truncated_mid_string_with_markdown_fence():
    """The exact failure pattern from the production logs."""
    raw = (
        "```json\n"
        "{\n"
        '  "grade": "Grade 10",\n'
        '  "subject_name": "FASIHI YA KISWAHILI",\n'
        '  "strands": [\n'
        "    {\n"
        '      "name": "Misingi ya Fasihi",\n'
        '      "substrands": [\n'
        "        {\n"
        '          "name": "Fasihi Simulizi - D'
    )
    result = repair_json(raw)
    # Critical fields must survive even when the response was truncated.
    assert result["grade"] == "Grade 10"
    assert result["subject_name"] == "FASIHI YA KISWAHILI"
    assert isinstance(result["strands"], list)
    assert result["strands"][0]["name"] == "Misingi ya Fasihi"


def test_repair_fenced_complete_json():
    """Plain markdown-fenced output must still parse cleanly."""
    raw = '```json\n{"a": 1, "b": 2}\n```'
    assert repair_json(raw) == {"a": 1, "b": 2}


def test_repair_trailing_comma_after_truncation():
    """Truncation often leaves a dangling comma right before the synthetic
    closing bracket — strip it and try again."""
    raw = '{"items":[{"x":1},'
    result = repair_json(raw)
    assert result == {"items": [{"x": 1}]}


def test_repair_dangling_key_after_truncation():
    """A truncation that leaves a hanging key (`"name":`) must drop the
    incomplete pair instead of crashing."""
    raw = '{"a": 1, "b":'
    result = repair_json(raw)
    assert result["a"] == 1
    # `b` should NOT be present because it was incomplete
    assert "b" not in result


def test_repair_smart_quotes():
    """Gemini occasionally emits curly quotes — those must convert to
    straight quotes before parsing."""
    raw = '{\u201cname\u201d: \u201cFasihi\u201d}'
    assert repair_json(raw) == {"name": "Fasihi"}


def test_repair_completely_unparseable_raises():
    """Garbage in must raise a ValueError with diagnostic context."""
    with pytest.raises(ValueError, match=r"Cannot repair JSON"):
        repair_json("hello world this is not json at all")
