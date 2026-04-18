"""
Curriculum Pipeline — Production-grade PDF ingestion.

Replaces the fragile process_single_pdf flow with:
1. Robust PDF text cleaning
2. Reliable JSON parsing with repair
3. Direct MongoDB insertion (no subprocess seed scripts)
4. Background job queue using MongoDB (no Redis needed)
5. Job status tracking for admin visibility

Architecture: single FastAPI service + background asyncio worker.
No extra services, no Redis, no Celery.
"""

import asyncio
import json
import logging
import os
import re
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pdfplumber
from bson import ObjectId

logger = logging.getLogger("pipeline")

# ---------------------------------------------------------------------------
# Section E — JSON Reliability
# ---------------------------------------------------------------------------

def repair_json(raw: str) -> dict:
    """Parse JSON from AI output, repairing common Gemini issues.

    Handles:
    - Markdown code fences (```json ... ```)
    - Prose before/after JSON
    - Trailing commas
    - Smart quotes (curly quotes)
    - Single-quoted strings
    - Truncation detection
    """
    text = raw.strip()

    # Strip markdown fences
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    text = text.strip()

    # Extract JSON object from surrounding prose
    brace_start = text.find('{')
    brace_end = text.rfind('}')
    if brace_start >= 0 and brace_end > brace_start:
        text = text[brace_start:brace_end + 1]

    # Fix smart quotes → straight quotes
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")

    # Try parsing as-is first (fast path)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Repair trailing commas: ,] → ] and ,} → }
    repaired = re.sub(r',\s*([}\]])', r'\1', text)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # Try fixing single quotes → double quotes (risky but last resort)
    repaired2 = repaired.replace("'", '"')
    try:
        return json.loads(repaired2)
    except json.JSONDecodeError:
        pass

    # Check for truncation — close unmatched brackets in correct order
    open_braces = repaired.count('{') - repaired.count('}')
    open_brackets = repaired.count('[') - repaired.count(']')
    if open_braces > 0 or open_brackets > 0:
        # Build closing sequence by tracking what's still open
        stack = []
        in_string = False
        escaped = False
        for ch in repaired:
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch in ('{', '['):
                stack.append('}' if ch == '{' else ']')
            elif ch in ('}', ']') and stack:
                stack.pop()

        suffix = '"' if in_string else ''
        suffix += ''.join(reversed(stack))
        try:
            return json.loads(repaired + suffix)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Cannot repair JSON. First 200 chars: {raw[:200]}")


# ---------------------------------------------------------------------------
# Section C — PDF Text Cleaning
# ---------------------------------------------------------------------------

def clean_pdf_text(raw_text: str) -> str:
    """Clean extracted PDF text before sending to Gemini.

    Removes:
    - Repeated headers/footers
    - Page numbers
    - Excessive whitespace
    - Control characters
    """
    lines = raw_text.split('\n')
    cleaned = []

    # Detect repeated lines (headers/footers appear on every page)
    from collections import Counter
    line_counts = Counter(line.strip() for line in lines if line.strip())
    # Lines appearing more than 3 times are likely headers/footers
    repeated = {line for line, count in line_counts.items() if count > 3 and len(line) < 100}

    for line in lines:
        stripped = line.strip()
        # Skip empty lines
        if not stripped:
            cleaned.append('')
            continue
        # Skip repeated headers/footers
        if stripped in repeated:
            continue
        # Skip standalone page numbers
        if re.match(r'^\d{1,3}$', stripped):
            continue
        # Remove control characters but keep normal Unicode
        stripped = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', stripped)
        cleaned.append(stripped)

    # Collapse excessive blank lines
    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(cleaned))
    return result.strip()


# ---------------------------------------------------------------------------
# Section G — Direct DB Insertion (replaces seed script subprocess)
# ---------------------------------------------------------------------------

async def insert_curriculum_data(db, extracted: dict) -> Dict[str, int]:
    """Insert extracted curriculum data directly into MongoDB.

    This replaces the fragile generate-seed-script-then-subprocess pattern.
    Uses the same logic as the seed script generator but runs in-process.

    Returns stats dict.
    """
    from scripts.grade_utils import normalize_grade_name

    grade_name = normalize_grade_name(extracted.get("grade")) or extracted.get("grade", "")
    subject_name = extracted.get("subject_name", "Unknown")

    if not grade_name:
        raise ValueError("Grade could not be determined")

    # Get or create grade
    grade = await db.grades.find_one({"name": grade_name})
    if not grade:
        grade = await db.grades.find_one(
            {"name": {"$regex": f"^{re.escape(grade_name)}$", "$options": "i"}}
        )
    if not grade:
        digits = re.findall(r'\d+', grade_name)
        order = int(digits[0]) if digits else 99
        result = await db.grades.insert_one({"name": grade_name, "order": order})
        grade_id = str(result.inserted_id)
    else:
        grade_id = str(grade["_id"])

    # Safe reseed: delete existing subject-scoped data
    existing_subject = await db.subjects.find_one({"name": subject_name, "gradeIds": {"$in": [grade_id]}})
    if not existing_subject:
        existing_subject = await db.subjects.find_one({"name": subject_name, "gradeIds": grade_id})

    if existing_subject:
        subj_id = str(existing_subject["_id"])
        strands = await db.strands.find({"subjectId": subj_id}).to_list(500)
        for strand in strands:
            sid = str(strand["_id"])
            subs = await db.substrands.find({"strandId": sid}).to_list(500)
            for ss in subs:
                ssid = str(ss["_id"])
                slos = await db.slos.find({"substrandId": ssid}).to_list(500)
                for slo in slos:
                    await db.slo_mappings.delete_many({"sloId": str(slo["_id"])})
                await db.slos.delete_many({"substrandId": ssid})
                await db.learning_activities.delete_many({"substrandId": ssid})
                await db.lesson_slo_slots.delete_many({"substrandId": ssid})
                await db.lesson_slos.delete_many({"substrandId": ssid})
            await db.substrands.delete_many({"strandId": sid})
        await db.strands.delete_many({"subjectId": subj_id})
        await db.subjects.delete_one({"_id": existing_subject["_id"]})

    # Create subject
    subj_result = await db.subjects.insert_one({
        "name": subject_name,
        "gradeIds": [grade_id],
        "createdAt": datetime.utcnow(),
    })
    subject_id = str(subj_result.inserted_id)

    stats = {"strands": 0, "substrands": 0, "slos": 0, "activities": 0, "mappings": 0}

    def ensure_list(val):
        if not val:
            return []
        if isinstance(val, str):
            return [val] if val.strip() else []
        if isinstance(val, list):
            return [str(v).strip() for v in val if str(v).strip()]
        return []

    async def get_or_create(collection, name):
        if not name or not name.strip():
            return None
        name = name.strip()
        existing = await collection.find_one(
            {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
        )
        if existing:
            return str(existing["_id"])
        result = await collection.insert_one({
            "name": name, "description": name, "createdAt": datetime.utcnow()
        })
        return str(result.inserted_id)

    for strand_data in extracted.get("strands", []):
        strand_result = await db.strands.insert_one({
            "name": strand_data.get("name", ""),
            "subjectId": subject_id,
            "createdAt": datetime.utcnow(),
        })
        strand_id = str(strand_result.inserted_id)
        stats["strands"] += 1

        for ss_data in strand_data.get("substrands", []):
            num_lessons = ss_data.get("lessons")
            try:
                num_lessons = int(num_lessons) if num_lessons else None
            except (ValueError, TypeError):
                num_lessons = None

            ss_result = await db.substrands.insert_one({
                "name": ss_data.get("name", ""),
                "strandId": strand_id,
                "number_of_lessons": num_lessons,
                "createdAt": datetime.utcnow(),
            })
            ss_id = str(ss_result.inserted_id)
            stats["substrands"] += 1

            # Resolve competencies/values/PCIs for this substrand
            comp_ids = []
            for c in ensure_list(ss_data.get("competencies")):
                cid = await get_or_create(db.competencies, c)
                if cid:
                    comp_ids.append(cid)

            val_ids = []
            for v in ensure_list(ss_data.get("values")):
                vid = await get_or_create(db.values, v)
                if vid:
                    val_ids.append(vid)

            pci_ids = []
            for p in ensure_list(ss_data.get("pcis")):
                pid = await get_or_create(db.pcis, p)
                if pid:
                    pci_ids.append(pid)

            la = ss_data.get("learning_activities") or {}
            assess_ids = []
            for a in ensure_list(la.get("assessment")):
                aid = await get_or_create(db.assessment_methods, a)
                if aid:
                    assess_ids.append(aid)

            # Insert SLOs with populated mappings
            for slo_idx, slo_data in enumerate(ss_data.get("slos", [])):
                slo_name = slo_data.get("name", "") if isinstance(slo_data, dict) else str(slo_data)
                slo_desc = slo_data.get("description", slo_name) if isinstance(slo_data, dict) else slo_name

                slo_result = await db.slos.insert_one({
                    "name": slo_name,
                    "description": slo_desc,
                    "substrandId": ss_id,
                    "order": slo_idx + 1,
                    "createdAt": datetime.utcnow(),
                })
                slo_id = str(slo_result.inserted_id)
                stats["slos"] += 1

                # SLO-level overrides
                slo_comp = comp_ids[:]
                slo_val = val_ids[:]
                slo_pci = pci_ids[:]
                slo_assess = assess_ids[:]

                if isinstance(slo_data, dict):
                    for c in ensure_list(slo_data.get("competencies")):
                        cid = await get_or_create(db.competencies, c)
                        if cid and cid not in slo_comp:
                            slo_comp.append(cid)
                    for v in ensure_list(slo_data.get("values")):
                        vid = await get_or_create(db.values, v)
                        if vid and vid not in slo_val:
                            slo_val.append(vid)

                await db.slo_mappings.insert_one({
                    "sloId": slo_id,
                    "competencyIds": slo_comp,
                    "valueIds": slo_val,
                    "pciIds": slo_pci,
                    "assessmentIds": slo_assess,
                    "createdAt": datetime.utcnow(),
                })
                stats["mappings"] += 1

            # Insert learning activities
            await db.learning_activities.insert_one({
                "name": f"{ss_data.get('name', '')} Activities",
                "substrandId": ss_id,
                "introduction_activities": ensure_list(la.get("introduction")),
                "development_activities": ensure_list(la.get("development")),
                "conclusion_activities": ensure_list(la.get("conclusion")),
                "extended_activities": ensure_list(la.get("extended")),
                "learning_resources": ensure_list(la.get("resources")),
                "assessment_methods": ensure_list(la.get("assessment")),
                "createdAt": datetime.utcnow(),
            })
            stats["activities"] += 1

    return stats


# ---------------------------------------------------------------------------
# Section A — Background Job Queue (MongoDB-backed, no Redis)
# ---------------------------------------------------------------------------

JOB_COLLECTION = "curriculum_jobs"

async def create_job(db, filename: str, admin_id: str) -> str:
    """Create a new curriculum processing job. Returns job_id."""
    job_id = str(uuid.uuid4())
    await db[JOB_COLLECTION].insert_one({
        "_id": job_id,
        "filename": filename,
        "adminId": admin_id,
        "status": "queued",
        "progress": 0,
        "progressMessage": "Queued for processing",
        "result": None,
        "error": None,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    })
    return job_id


async def update_job(db, job_id: str, **kwargs):
    """Update job status fields."""
    kwargs["updatedAt"] = datetime.utcnow()
    await db[JOB_COLLECTION].update_one({"_id": job_id}, {"$set": kwargs})


async def get_job(db, job_id: str) -> Optional[dict]:
    """Get job status."""
    return await db[JOB_COLLECTION].find_one({"_id": job_id})


async def process_curriculum_job(db, job_id: str, file_path: Path):
    """Background worker: process a queued curriculum PDF job.

    Updates job status at each stage so admin can see progress.
    """
    try:
        await update_job(db, job_id, status="processing", progress=10,
                         progressMessage="Extracting text from PDF...")

        # Step 1: Extract text
        all_text = []
        with pdfplumber.open(str(file_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text)

        raw_text = "\n\n".join(all_text)
        if not raw_text.strip():
            await update_job(db, job_id, status="failed", error="No text found in PDF")
            return

        full_text = clean_pdf_text(raw_text)
        logger.info(f"[Job {job_id}] Extracted {len(full_text)} chars")

        await update_job(db, job_id, progress=25,
                         progressMessage="Sending to AI for extraction...")

        # Step 2: AI extraction
        import sys
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
        from ai_extractor import extract_with_gemini_chunked

        filename = file_path.name
        grade_num = re.search(r'(\d+)', filename)
        grade_hint = f"Grade {grade_num.group(1)}" if grade_num else ""
        subject_hint = file_path.stem.replace("_", " ").replace("-", " ")
        # Remove grade number from subject hint
        subject_hint = re.sub(r'\b(?:grade|Grade)\s*\d+\b', '', subject_hint).strip()

        extracted = await extract_with_gemini_chunked(full_text, subject_hint, grade_hint)

        if not extracted or not extracted.get("strands"):
            await update_job(db, job_id, status="failed",
                             error="AI extraction returned no curriculum data")
            return

        strand_count = len(extracted.get("strands", []))
        ss_count = sum(len(s.get("substrands", [])) for s in extracted.get("strands", []))
        slo_count = sum(
            sum(len(ss.get("slos", [])) for ss in s.get("substrands", []))
            for s in extracted.get("strands", [])
        )
        logger.info(f"[Job {job_id}] Extracted: {strand_count} strands, {ss_count} substrands, {slo_count} SLOs")

        await update_job(db, job_id, progress=60,
                         progressMessage=f"Inserting {slo_count} SLOs into database...")

        # Step 3: Save JSON for audit
        json_dir = Path(__file__).parent / "curriculum_data"
        json_dir.mkdir(exist_ok=True)
        safe_name = file_path.stem.lower().replace(" ", "_")
        json_path = json_dir / f"extracted_{safe_name}.json"
        with open(json_path, "w") as f:
            json.dump(extracted, f, indent=2, ensure_ascii=False)

        # Step 4: Direct DB insertion
        stats = await insert_curriculum_data(db, extracted)
        logger.info(f"[Job {job_id}] Inserted: {stats}")

        await update_job(db, job_id, progress=90,
                         progressMessage="Moving processed file...")

        # Step 5: Move to processed
        processed_dir = Path(__file__).parent / "pdfs_processed"
        processed_dir.mkdir(exist_ok=True)
        processed_path = processed_dir / file_path.name
        if file_path.exists():
            import shutil
            shutil.move(str(file_path), str(processed_path))

        await update_job(db, job_id, status="completed", progress=100,
                         progressMessage="Completed",
                         result={
                             "grade": extracted.get("grade", grade_hint),
                             "subject": extracted.get("subject_name", subject_hint),
                             "strands": stats["strands"],
                             "substrands": stats["substrands"],
                             "slos": stats["slos"],
                             "activities": stats["activities"],
                             "mappings": stats["mappings"],
                         })

    except Exception as e:
        logger.error(f"[Job {job_id}] Failed: {traceback.format_exc()}")
        await update_job(db, job_id, status="failed",
                         error=str(e)[:500])
        # Clean up file
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass
