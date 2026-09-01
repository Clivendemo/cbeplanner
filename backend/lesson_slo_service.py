"""
Lesson SLO Service Layer
Manages lesson-level curriculum intelligence: sync, auto-generation, CRUD.
Used by admin endpoints and scheme/lesson-plan generators.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from bson import ObjectId

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Auto-generation helpers (no LLM — rule-based, content-aware)
# ---------------------------------------------------------------------------

def _generate_lesson_outcome(
    subject_name: str,
    strand_name: str,
    substrand_name: str,
    parent_slo_name: str,
    lesson_number: int,
    total_lessons: int,
) -> str:
    """Generate a content-aware lesson SLO outcome from parent context.

    Uses structured progression:
    - Early lessons: introduce / identify / explain
    - Middle lessons: apply / demonstrate / practise
    - Late lessons: evaluate / create / consolidate
    """
    slo_lower = parent_slo_name.lower().strip().rstrip(".")

    if total_lessons == 1:
        return f"Demonstrate understanding of {slo_lower}"

    # Progression verbs by position
    position = lesson_number / total_lessons
    if position <= 0.33:
        verbs = ["Identify and explain", "Describe", "Explore"]
    elif position <= 0.66:
        verbs = ["Apply", "Demonstrate", "Practise"]
    else:
        verbs = ["Evaluate", "Create", "Consolidate understanding of"]

    verb = verbs[lesson_number % len(verbs)]

    # Make it subject/content-aware
    return f"{verb} {slo_lower} in the context of {substrand_name}"


# ---------------------------------------------------------------------------
# Core service functions (all take `db` as first arg — no global state)
# ---------------------------------------------------------------------------

async def sync_lesson_slos_for_substrand(db, substrand_id: str) -> Dict[str, Any]:
    """Synchronise lesson_slos to match substrand.number_of_lessons.

    Rules:
    - No number_of_lessons → do nothing (returns early).
    - Missing lesson SLOs → auto-generate as drafts.
    - Extra lesson SLOs (count decreased) → mark isActive=False.
    - Never overwrite admin-edited (isDraft=False) records.
    - Returns stats dict.
    """
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        return {"error": "substrand_not_found"}

    num_lessons = substrand.get("number_of_lessons")
    if not num_lessons or num_lessons < 1:
        return {"synced": False, "reason": "no_lesson_count"}

    # Load context for auto-generation
    strand = await db.strands.find_one({"_id": ObjectId(substrand.get("strandId", ""))})
    strand_name = strand["name"] if strand else ""
    subject_name = ""
    if strand:
        subj = await db.subjects.find_one({"_id": ObjectId(strand.get("subjectId", ""))})
        subject_name = subj["name"] if subj else ""

    # Load parent SLOs for outcome generation
    parent_slos = await db.slos.find(
        {"substrandId": substrand_id}
    ).sort("order", 1).to_list(100)
    parent_slo_name = parent_slos[0]["name"] if parent_slos else substrand["name"]

    # Load existing lesson_slos
    existing = await db.lesson_slos.find(
        {"substrandId": substrand_id}
    ).sort("lessonNumber", 1).to_list(500)
    existing_by_num = {doc["lessonNumber"]: doc for doc in existing}

    created = 0
    deactivated = 0

    # Create missing lesson SLOs
    for i in range(1, num_lessons + 1):
        if i not in existing_by_num:
            # Pick parent SLO in round-robin
            parent_slo = parent_slos[(i - 1) % len(parent_slos)] if parent_slos else None
            parent_slo_id = str(parent_slo["_id"]) if parent_slo else None
            used_slo_name = parent_slo["name"] if parent_slo else parent_slo_name

            outcome = _generate_lesson_outcome(
                subject_name, strand_name, substrand["name"],
                used_slo_name, i, num_lessons,
            )
            # KIQs are seeded directly from the curriculum extractor onto
            # the parent SLO row. No algorithmic generation. If the parent
            # has no extracted KIQs, the lesson stays blank — admins can
            # fill it in via the curriculum editor.
            inquiry = list(parent_slo.get("key_inquiry_questions") or []) if parent_slo else []

            await db.lesson_slos.insert_one({
                "strandId": substrand.get("strandId", ""),
                "substrandId": substrand_id,
                "parentSloId": parent_slo_id,
                "lessonNumber": i,
                "outcome": outcome,
                "description": "",
                "keyInquiryQuestions": inquiry,
                "learningExperiences": [],
                "learningResources": [],
                "assessmentMethods": [],
                "coreCompetencies": [],
                "values": [],
                "pcis": [],
                "isDraft": True,
                "isAutoGenerated": True,
                "isActive": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            })
            created += 1
        else:
            # Ensure existing active ones stay active
            doc = existing_by_num[i]
            if not doc.get("isActive", True):
                await db.lesson_slos.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"isActive": True, "updatedAt": datetime.utcnow()}}
                )

    # Deactivate extras (lesson numbers > current count)
    for num, doc in existing_by_num.items():
        if num > num_lessons and doc.get("isActive", True):
            await db.lesson_slos.update_one(
                {"_id": doc["_id"]},
                {"$set": {"isActive": False, "updatedAt": datetime.utcnow()}}
            )
            deactivated += 1

    logger.info(
        f"Synced lesson_slos for substrand {substrand_id}: "
        f"created={created}, deactivated={deactivated}, target={num_lessons}"
    )
    return {"synced": True, "created": created, "deactivated": deactivated, "target": num_lessons}


async def regenerate_lesson_slos(db, substrand_id: str, force: bool = False) -> Dict[str, Any]:
    """Regenerate draft lesson SLOs for a substrand.

    - If force=True, replaces all auto-generated drafts.
    - Never touches admin-edited records (isDraft=False).
    """
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        return {"error": "substrand_not_found"}

    num_lessons = substrand.get("number_of_lessons")
    if not num_lessons or num_lessons < 1:
        return {"error": "no_lesson_count"}

    if force:
        # Only delete auto-generated drafts
        result = await db.lesson_slos.delete_many({
            "substrandId": substrand_id,
            "isDraft": True,
            "isAutoGenerated": True,
        })
        logger.info(f"Deleted {result.deleted_count} auto-generated drafts for regeneration")

    return await sync_lesson_slos_for_substrand(db, substrand_id)


async def get_active_lesson_slos(db, substrand_id: str) -> List[Dict[str, Any]]:
    """Return active lesson SLOs in lesson number order, serialised for API."""
    docs = await db.lesson_slos.find(
        {"substrandId": substrand_id, "isActive": True}
    ).sort("lessonNumber", 1).to_list(500)

    result = []
    for doc in docs:
        doc["id"] = str(doc.pop("_id"))
        result.append(doc)
    return result


async def get_lesson_slo_for_slot(
    db, substrand_id: str, lesson_number: int
) -> Optional[Dict[str, Any]]:
    """Get a single active lesson SLO for a specific lesson slot.

    Used by scheme generation and lesson plan generation.
    Returns None if not found (caller should fallback).
    """
    doc = await db.lesson_slos.find_one({
        "substrandId": substrand_id,
        "lessonNumber": lesson_number,
        "isActive": True,
    })
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


async def bootstrap_missing_lesson_slos(db) -> Dict[str, int]:
    """Migration: scan all substrands with number_of_lessons and
    generate missing lesson_slos. Never overwrites existing records.
    """
    stats = {"scanned": 0, "synced": 0, "created_total": 0}

    cursor = db.substrands.find(
        {"number_of_lessons": {"$exists": True, "$gte": 1}}
    )
    async for substrand in cursor:
        stats["scanned"] += 1
        sid = str(substrand["_id"])
        result = await sync_lesson_slos_for_substrand(db, sid)
        if result.get("created", 0) > 0:
            stats["synced"] += 1
            stats["created_total"] += result["created"]

    logger.info(f"Bootstrap complete: {stats}")
    return stats
