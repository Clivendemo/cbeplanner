"""
Grade normalization and matching utilities.

Responsible for:
- Converting raw grade strings from AI extraction or user input into the
  canonical format used in the database (e.g. "Grade 4", "PP1").
- Matching a normalized name against existing DB records.
- Creating a new grade ONLY when no match exists.

This module has NO database dependency — the async DB helpers accept a `db`
argument so they can be called from both the seed script generator and
the server pipeline.
"""

import re
from typing import Optional

# ---------------------------------------------------------------------------
# Canonical DB naming convention
# ---------------------------------------------------------------------------
# The CBE Planner database uses these names:
#   PP1, PP2                           — Pre-Primary
#   Grade 1 .. Grade 12               — Primary / Junior / Senior School
#
# The AI extractor and KICD PDFs may return many variants.
# This module normalises all of them into the canonical set.
# ---------------------------------------------------------------------------

# Static alias map: lowercased stripped → canonical name
_ALIASES = {
    "pp1":             "PP1",
    "pp2":             "PP2",
    "pre primary 1":   "PP1",
    "pre primary 2":   "PP2",
    "pre-primary 1":   "PP1",
    "pre-primary 2":   "PP2",
    "preprimary 1":    "PP1",
    "preprimary 2":    "PP2",
    "pre-primary one": "PP1",
    "pre-primary two": "PP2",
    "nursery":         "PP1",
    "kindergarten":    "PP1",
}

# Word-to-digit for "Grade One" → "Grade 1" etc.
_WORD_TO_DIGIT = {
    "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8",
    "nine": "9", "ten": "10", "eleven": "11", "twelve": "12",
}


def normalize_grade_name(raw: Optional[str]) -> Optional[str]:
    """Convert any raw grade string into the canonical DB name.

    Returns None if the input is empty/None or truly unrecognisable.

    Examples:
        "grade 1"              → "Grade 1"
        "GRADE 7"              → "Grade 7"
        "Grade One"            → "Grade 1"
        "Pre Primary 1"        → "PP1"
        "pre-primary 2"        → "PP2"
        "Junior School Grade 8"→ "Grade 8"
        "Senior School Grade 11" → "Grade 11"
        "Form 1"               → "Grade 7"   (8-4-4 to CBC mapping)
        ""                     → None
    """
    if not raw or not raw.strip():
        return None

    cleaned = raw.strip()
    key = re.sub(r'\s+', ' ', cleaned).lower().strip()

    # 1. Direct alias hit
    if key in _ALIASES:
        return _ALIASES[key]

    # 2. Extract a digit from "Grade X" / "grade X" patterns
    #    Also handles "Junior School Grade 8", "Senior School Grade 11", etc.
    m = re.search(r'grade\s+(\d{1,2})', key)
    if m:
        num = int(m.group(1))
        if 1 <= num <= 12:
            return f"Grade {num}"

    # 3. "Grade One", "Grade Two" etc.
    m = re.search(r'grade\s+(\w+)', key)
    if m:
        word = m.group(1).lower()
        if word in _WORD_TO_DIGIT:
            return f"Grade {_WORD_TO_DIGIT[word]}"

    # 4. Bare number: "4" or "10"
    m = re.fullmatch(r'(\d{1,2})', key)
    if m:
        num = int(m.group(1))
        if 1 <= num <= 12:
            return f"Grade {num}"

    # 5. "Class X" (some East African systems)
    m = re.search(r'class\s+(\d{1,2})', key)
    if m:
        num = int(m.group(1))
        if 1 <= num <= 12:
            return f"Grade {num}"

    # 6. "Form X" → CBC mapping (Form 1=Grade 7 ... Form 6=Grade 12)
    m = re.search(r'form\s+(\d)', key)
    if m:
        form_num = int(m.group(1))
        grade_num = form_num + 6
        if 7 <= grade_num <= 12:
            return f"Grade {grade_num}"

    # 7. "PP1" / "PP2" without space
    m = re.fullmatch(r'pp\s*([12])', key)
    if m:
        return f"PP{m.group(1)}"

    # 8. Still contains "grade" but unusual format — try last resort
    if "grade" in key:
        digits = re.findall(r'\d+', key)
        if digits:
            num = int(digits[-1])
            if 1 <= num <= 12:
                return f"Grade {num}"

    # Unrecognisable
    return None


def grade_sort_order(canonical_name: str) -> int:
    """Return a numeric sort order for a canonical grade name."""
    if canonical_name == "PP1":
        return -2
    if canonical_name == "PP2":
        return -1
    m = re.search(r'(\d+)', canonical_name)
    if m:
        return int(m.group(1))
    return 99


# ---------------------------------------------------------------------------
# Async DB helpers (take `db` as argument — no global state)
# ---------------------------------------------------------------------------

async def get_existing_or_create_grade(db, raw_grade_name: str):
    """Match a grade name against existing DB records, creating only if needed.

    Steps:
      1. Normalize the raw name.
      2. Search db.grades for an exact canonical match.
      3. If not found, try a case-insensitive regex match on all grades.
      4. If still not found, create a new grade.
      5. Return the _id (as ObjectId).

    This function NEVER creates duplicates for naming variants.
    """
    canonical = normalize_grade_name(raw_grade_name)
    if not canonical:
        # Truly unrecognisable — try the raw string as a last resort
        canonical = raw_grade_name.strip() if raw_grade_name else None
    if not canonical:
        raise ValueError(f"Cannot determine grade from: {raw_grade_name!r}")

    # Exact match
    existing = await db.grades.find_one({"name": canonical})
    if existing:
        return existing["_id"]

    # Case-insensitive match (catches "grade 4" vs "Grade 4" in DB)
    existing = await db.grades.find_one({
        "name": {"$regex": f"^{re.escape(canonical)}$", "$options": "i"}
    })
    if existing:
        return existing["_id"]

    # Alias scan: normalize every DB grade and compare
    async for doc in db.grades.find():
        db_canonical = normalize_grade_name(doc["name"])
        if db_canonical and db_canonical == canonical:
            return doc["_id"]

    # No match at all — create
    order = grade_sort_order(canonical)
    result = await db.grades.insert_one({
        "name": canonical,
        "order": order,
    })
    return result.inserted_id
