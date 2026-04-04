"""
AI Curriculum Extractor — Gemini 2.5 Flash
Extracts structured curriculum data from PDF text using Gemini AI.
Outputs the EXACT JSON structure needed by seed scripts.
"""

import os
import json
import asyncio
import uuid
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from emergentintegrations.llm.chat import LlmChat, UserMessage


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

If grade is not clear from the text, use "Grade 10" as default.
If lesson count is not available, estimate based on content volume.

PDF TEXT:
"""


async def extract_with_gemini(text: str, session_suffix: str = "") -> dict:
    """Extract curriculum data from PDF text using Gemini 2.5 Flash."""
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise ValueError("EMERGENT_LLM_KEY not set in environment")

    session_id = f"curriculum-extract-{session_suffix or uuid.uuid4().hex[:8]}"

    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message="You are a precise curriculum data extraction system. Return ONLY valid JSON."
    ).with_model("gemini", "gemini-2.5-flash")

    # Send the full text
    message = UserMessage(text=EXTRACTION_PROMPT + text)
    response = await chat.send_message(message)

    # Parse JSON from response
    response_text = response.strip()

    # Clean markdown code blocks if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        response_text = "\n".join(lines)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response_text[start:end])
        raise ValueError(f"Could not parse AI response as JSON: {response_text[:200]}...")


async def extract_with_gemini_chunked(text: str, subject_hint: str = "", grade_hint: str = "Grade 10") -> dict:
    """For very large PDFs, extract in chunks then merge."""
    # If text is small enough, extract in one shot
    if len(text) < 30000:
        return await extract_with_gemini(text, subject_hint.replace(" ", "_"))

    # Split into chunks by looking for strand-level breaks
    chunks = _split_into_chunks(text, max_chars=25000)
    print(f"  Large PDF detected — splitting into {len(chunks)} chunks")

    all_strands = []
    grade = grade_hint
    subject_name = subject_hint

    for i, chunk in enumerate(chunks):
        print(f"  Extracting chunk {i+1}/{len(chunks)}...")
        hint = f"\nContext: This is part {i+1} of {len(chunks)} from {subject_hint} ({grade_hint}).\n"
        result = await extract_with_gemini(hint + chunk, f"{subject_hint}_{i}")

        if result.get("grade"):
            grade = result["grade"]
        if result.get("subject_name"):
            subject_name = result["subject_name"]
        all_strands.extend(result.get("strands", []))

    # Merge strands with the same name
    merged = _merge_strands(all_strands)

    return {
        "grade": grade,
        "subject_name": subject_name,
        "strands": merged
    }


def _split_into_chunks(text: str, max_chars: int = 25000) -> list:
    """Split text into chunks, trying to break at strand boundaries."""
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
        name = strand["name"]
        if name not in merged:
            merged[name] = strand
        else:
            # Append substrands
            existing_ss = {ss["name"] for ss in merged[name].get("substrands", [])}
            for ss in strand.get("substrands", []):
                if ss["name"] not in existing_ss:
                    merged[name]["substrands"].append(ss)
                    existing_ss.add(ss["name"])
    return list(merged.values())
