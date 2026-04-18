"""
AI Curriculum Extractor — Gemini 2.5 Flash (google-genai)
Extracts structured curriculum data from PDF text using Gemini AI.
Outputs the EXACT JSON structure needed by the seed script generator.

Responsibility boundary:
  - This module DETECTS grade/subject from PDF text and returns JSON.
  - It does NOT write to the database.
  - The seed/import stage handles DB matching and creation.
"""

import os
import json
import asyncio
import re
from dotenv import load_dotenv
from google import genai

# Import normalizer (extractor normalizes its own output before returning)
from grade_utils import normalize_grade_name

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


# ---------------------------------------------------------------------------
# Extraction prompt — strengthened grade detection
# ---------------------------------------------------------------------------

EXTRACTION_PROMPT = """You are extracting KICD (Kenya Institute of Curriculum Development) CBC (Competency-Based Curriculum) data from a curriculum design PDF.

Return ONLY valid JSON. No markdown, no explanations, no code blocks.

STRICT RULES:
- Do NOT summarize or shorten ANY text. Preserve exact wording from the document.
- Capture ALL strands, ALL substrands, ALL SLOs (Specific Learning Outcomes) completely.
- Maintain the full hierarchy: Subject → Strands → Substrands → SLOs
- Each substrand must have its learning activities split into 4 categories:
  * introduction: Opening/warm-up activities
  * development: Main teaching activities (GENERAL classroom activities)
  * conclusion: Closing/wrap-up activities
  * extended: Activities containing keywords: practical, project, experiment, field work, assignment, research, investigation, survey, field trip, hands-on
- If an activity contains those keywords, it MUST go to "extended", not "development"
- Capture competencies, values, PCIs (Pertinent Contemporary Issues) per substrand
- Include assessment methods and learning resources when available
- Estimate lesson count per substrand from the document if mentioned

GRADE DETECTION (CRITICAL):
- You MUST identify the exact grade/class/level from the document.
- Look for grade information in: title page, headers, footers, repeated section headings,
  "Curriculum Designs for..." text, "Grade X" references, and document metadata.
- Return the grade in the format "Grade X" (e.g. "Grade 1", "Grade 10").
- For pre-primary, return "PP1" or "PP2".
- If the document says "Junior School" or "Senior School", still extract the grade number.
- If you find MULTIPLE grades mentioned (e.g. a combined Grade 7-9 document), return
  the LOWEST grade as the primary grade.
- If you genuinely CANNOT find any grade information anywhere in the text, return
  "grade": null — do NOT guess or assume a grade number.

OUTPUT FORMAT (strict JSON):
{
  "grade": "Grade X",
  "subject_name": "Subject Name",
  "strands": [
    {
      "name": "Strand Name",
      "substrands": [
        {
          "name": "Substrand Name",
          "lessons": 10,
          "slos": [
            {"name": "Full SLO text", "description": "Full SLO text"}
          ],
          "learning_activities": {
            "introduction": "Introduction activities text",
            "development": "Development activities text",
            "conclusion": "Conclusion activities text",
            "extended": "Extended activities text",
            "resources": ["Resource 1", "Resource 2"],
            "assessment": ["Method 1", "Method 2"]
          },
          "competencies": ["Competency 1", "Competency 2"],
          "values": ["Value 1", "Value 2"],
          "pcis": ["PCI 1", "PCI 2"]
        }
      ]
    }
  ]
}

If lesson count is not available, estimate based on content volume.

PDF TEXT:
"""


def _get_client():
    """Create Gemini client using API key from environment."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set in environment")
    return genai.Client(api_key=api_key)


def _post_process_grade(result: dict, grade_hint: str = "") -> dict:
    """Normalize the grade field returned by the AI.

    Priority:
      1. AI-detected grade (if not null/empty)
      2. grade_hint from filename/caller
      3. None (caller must handle)

    Never silently defaults to "Grade 10" or any other arbitrary value.
    """
    raw_grade = result.get("grade")
    normalized = normalize_grade_name(raw_grade) if raw_grade else None

    if normalized:
        result["grade"] = normalized
        return result

    # AI returned null/empty — try the hint
    hint_normalized = normalize_grade_name(grade_hint) if grade_hint else None
    if hint_normalized:
        result["grade"] = hint_normalized
        result["_grade_source"] = "hint"
        return result

    # Truly unknown
    result["grade"] = None
    result["_grade_source"] = "unknown"
    return result


async def extract_with_gemini(text: str, session_suffix: str = "") -> dict:
    """Extract curriculum data from PDF text using Gemini 2.5 Flash."""
    client = _get_client()

    prompt = EXTRACTION_PROMPT + text

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
    )

    response_text = response.text.strip()

    # Use robust JSON repair (handles fences, trailing commas, smart quotes, truncation)
    from curriculum_pipeline import repair_json
    return repair_json(response_text)


async def extract_with_gemini_chunked(
    text: str,
    subject_hint: str = "",
    grade_hint: str = "",
) -> dict:
    """For very large PDFs, extract in chunks then merge.

    Grade handling:
    - The FIRST chunk's grade (or the most explicit one) is preferred.
    - Later chunks do NOT overwrite an already-detected grade with a guess.
    - After merging, the grade is normalized via grade_utils.
    """
    # Single-shot extraction for small documents
    if len(text) < 30000:
        result = await extract_with_gemini(text, subject_hint.replace(" ", "_"))
        return _post_process_grade(result, grade_hint)

    # Chunked extraction
    chunks = _split_into_chunks(text, max_chars=25000)
    print(f"  Large PDF detected - splitting into {len(chunks)} chunks")

    all_strands = []
    detected_grade = None    # First confident detection wins
    subject_name = subject_hint

    for i, chunk in enumerate(chunks):
        print(f"  Extracting chunk {i+1}/{len(chunks)}...")
        hint = f"\nContext: This is part {i+1} of {len(chunks)} from {subject_hint}.\n"
        result = await extract_with_gemini(hint + chunk, f"{subject_hint}_{i}")

        # Grade: keep the first non-null detection, don't let later chunks overwrite
        chunk_grade = result.get("grade")
        if chunk_grade and not detected_grade:
            normalized = normalize_grade_name(chunk_grade)
            if normalized:
                detected_grade = normalized
                print(f"    Grade detected from chunk {i+1}: {detected_grade}")

        if result.get("subject_name"):
            subject_name = result["subject_name"]

        all_strands.extend(result.get("strands", []))

    merged = _merge_strands(all_strands)

    final = {
        "grade": detected_grade,
        "subject_name": subject_name,
        "strands": merged,
    }
    return _post_process_grade(final, grade_hint)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_into_chunks(text: str, max_chars: int = 25000) -> list:
    """Split text into chunks, trying to break at paragraph boundaries."""
    lines = text.split("\n")
    chunks = []
    current = []
    current_len = 0

    for line in lines:
        line_len = len(line) + 1
        if current_len + line_len > max_chars and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += line_len

    if current:
        chunks.append("\n".join(current))

    return chunks


def _merge_strands(strands: list) -> list:
    """Merge strands with the same name (from chunked extraction)."""
    merged = {}
    for strand in strands:
        name = strand.get("name", "")
        if name not in merged:
            merged[name] = strand
        else:
            existing_ss = {ss["name"] for ss in merged[name].get("substrands", [])}
            for ss in strand.get("substrands", []):
                if ss["name"] not in existing_ss:
                    merged[name]["substrands"].append(ss)
                    existing_ss.add(ss["name"])
    return list(merged.values())
