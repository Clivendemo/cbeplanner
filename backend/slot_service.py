"""
Lesson SLO Slot Service
Phase 1 + 2: Data model operations and slot generation.

Collection: lesson_slo_slots
- Each slot represents ONE lesson in a substrand
- slot_index driven EXCLUSIVELY by substrand.number_of_lessons
- Customised slots persist; uncustomised slots use fallback from parent SLOs

This module has NO route definitions — called by server.py endpoints.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Slot generation — strictly from number_of_lessons
# ---------------------------------------------------------------------------

async def generate_slots_for_substrand(db, substrand_id: str) -> Dict[str, Any]:
    """Generate lesson SLO slots for a substrand.

    STRICT RULE: slot count = substrand.number_of_lessons.
    If number_of_lessons is missing/null/0, returns an error.
    Never infers count from SLO count.

    Existing customised slots (is_customized=True) are NEVER overwritten.
    Missing slots are filled with fallback data from parent SLOs.
    Excess slots (if number decreased) are deleted.
    """
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        return {"error": "substrand_not_found"}

    total_lessons = substrand.get("number_of_lessons")
    if not total_lessons or int(total_lessons) < 1:
        return {"error": "no_number_of_lessons",
                "message": "Set number_of_lessons on this substrand first"}

    total_lessons = int(total_lessons)

    # Resolve hierarchy IDs
    strand_id = substrand.get("strandId", "")
    strand = await db.strands.find_one({"_id": ObjectId(strand_id)}) if strand_id else None
    subject_id = strand.get("subjectId", "") if strand else ""
    subject = await db.subjects.find_one({"_id": ObjectId(subject_id)}) if subject_id else None
    grade_id = ""
    if subject:
        gids = subject.get("gradeIds", [])
        grade_id = gids[0] if isinstance(gids, list) and gids else (gids if isinstance(gids, str) else "")

    # Load parent SLOs for fallback
    parent_slos = await db.slos.find(
        {"substrandId": substrand_id}
    ).sort("order", 1).to_list(100)

    # Load existing learning activities for substrand-level fallback
    learning_act = await db.learning_activities.find_one({"substrandId": substrand_id})

    # Load existing slots
    existing_slots = await db.lesson_slo_slots.find(
        {"substrandId": substrand_id}
    ).sort("slot_index", 1).to_list(500)
    existing_by_idx = {s["slot_index"]: s for s in existing_slots}

    created = 0

    for idx in range(total_lessons):
        if idx in existing_by_idx:
            continue  # Slot exists — never overwrite

        # Build fallback from parent SLO (round-robin)
        parent = parent_slos[idx % len(parent_slos)] if parent_slos else None
        fallback_outcome = parent["name"] if parent else f"Lesson {idx + 1}"
        fallback_desc = parent.get("description", fallback_outcome) if parent else ""

        # Fallback resources from learning_activities
        fallback_resources = []
        if learning_act:
            for r in learning_act.get("learning_resources", []):
                if isinstance(r, str):
                    fallback_resources.append({"type": "material", "display_text": r})
                elif isinstance(r, dict):
                    fallback_resources.append(r)

        # Fallback activities
        fallback_activities = []
        if learning_act:
            fallback_activities = learning_act.get("development_activities", [])

        # Fallback assessment
        fallback_assessment = []
        if learning_act:
            fallback_assessment = learning_act.get("assessment_methods", [])

        # Fallback competencies/values/pcis from SLO mapping
        competencies, values, pcis = [], [], []
        if parent:
            mapping = await db.slo_mappings.find_one({"sloId": str(parent["_id"])})
            if mapping:
                for cid in mapping.get("competencyIds", []):
                    doc = await db.competencies.find_one({"_id": ObjectId(cid)})
                    if doc:
                        competencies.append(doc["name"])
                for vid in mapping.get("valueIds", []):
                    doc = await db.values.find_one({"_id": ObjectId(vid)})
                    if doc:
                        values.append(doc["name"])
                for pid in mapping.get("pciIds", []):
                    doc = await db.pcis.find_one({"_id": ObjectId(pid)})
                    if doc:
                        pcis.append(doc["name"])

        await db.lesson_slo_slots.insert_one({
            "gradeId": grade_id,
            "subjectId": subject_id,
            "strandId": strand_id,
            "substrandId": substrand_id,
            "slot_index": idx,
            "outcome": fallback_outcome,
            "description": fallback_desc,
            "key_inquiry_question": "",
            "learning_activities": fallback_activities,
            "resources": fallback_resources,
            "assessment_methods": fallback_assessment,
            "competencies": competencies or ["Critical Thinking", "Communication"],
            "values": values or ["Responsibility", "Respect"],
            "pcis": pcis,
            "is_customized": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        })
        created += 1

    # Delete excess slots (slot_index >= total_lessons)
    deleted = await db.lesson_slo_slots.delete_many({
        "substrandId": substrand_id,
        "slot_index": {"$gte": total_lessons},
    })

    logger.info(
        f"generate_slots: substrand={substrand_id}, "
        f"target={total_lessons}, created={created}, deleted={deleted.deleted_count}"
    )
    return {
        "success": True,
        "total_lessons": total_lessons,
        "created": created,
        "deleted": deleted.deleted_count,
    }


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def _serialize(doc: dict) -> dict:
    """Convert a slot document for JSON response."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


async def get_slots_for_substrand(db, substrand_id: str) -> List[Dict[str, Any]]:
    """Return all slots for a substrand, ordered by slot_index.
    Auto-generates if slots don't exist yet but number_of_lessons is set.
    """
    count = await db.lesson_slo_slots.count_documents({"substrandId": substrand_id})
    if count == 0:
        # Auto-generate on first access
        await generate_slots_for_substrand(db, substrand_id)

    docs = await db.lesson_slo_slots.find(
        {"substrandId": substrand_id}
    ).sort("slot_index", 1).to_list(500)
    return [_serialize(d) for d in docs]


async def get_slot(db, substrand_id: str, slot_index: int) -> Optional[Dict[str, Any]]:
    """Get a single slot by substrand + index."""
    doc = await db.lesson_slo_slots.find_one({
        "substrandId": substrand_id,
        "slot_index": slot_index,
    })
    return _serialize(doc) if doc else None


async def update_slot(db, substrand_id: str, slot_index: int, data: dict) -> Dict[str, Any]:
    """Update a slot with admin-provided data. Marks as customised."""
    update_fields = {"is_customized": True, "updatedAt": datetime.utcnow()}

    for field in [
        "outcome", "description", "key_inquiry_question",
        "learning_activities", "resources", "assessment_methods",
        "competencies", "values", "pcis",
    ]:
        if field in data:
            update_fields[field] = data[field]

    result = await db.lesson_slo_slots.update_one(
        {"substrandId": substrand_id, "slot_index": slot_index},
        {"$set": update_fields},
    )
    if result.matched_count == 0:
        return {"error": "slot_not_found"}
    return {"success": True, "action": "updated"}


async def clear_slot(db, substrand_id: str, slot_index: int) -> Dict[str, Any]:
    """Clear a slot back to fallback state. Deletes and regenerates it."""
    await db.lesson_slo_slots.delete_one({
        "substrandId": substrand_id,
        "slot_index": slot_index,
    })
    # Regenerate will fill the gap with fallback
    await generate_slots_for_substrand(db, substrand_id)
    slot = await get_slot(db, substrand_id, slot_index)
    return {"success": True, "slot": slot}


# ---------------------------------------------------------------------------
# Scheme/lesson-plan integration helper
# ---------------------------------------------------------------------------

def format_resource_display(resource) -> str:
    """Format a resource object into display text for PDF/scheme.

    Supports:
      {"type": "textbook", "title": "...", "pages": "50-52", "display_text": "..."}
      {"type": "material", "display_text": "Charts"}
      "Plain string"
    """
    if isinstance(resource, str):
        return resource
    if isinstance(resource, dict):
        # Prefer explicit display_text
        if resource.get("display_text"):
            return resource["display_text"]
        # Build from title + pages
        title = resource.get("title", "")
        pages = resource.get("pages", "")
        if title and pages:
            return f"{title}, pp. {pages}"
        return title or str(resource)
    return str(resource)


async def get_slot_for_scheme(
    db, substrand_id: str, slot_index: int
) -> Optional[Dict[str, Any]]:
    """Get a slot for use in scheme/lesson-plan generation.

    Returns the slot data with resources formatted as display strings.
    Returns None if no slot exists (caller should use fallback).
    """
    doc = await db.lesson_slo_slots.find_one({
        "substrandId": substrand_id,
        "slot_index": slot_index,
    })
    if not doc:
        return None

    # Format resources for display
    raw_resources = doc.get("resources", [])
    doc["formatted_resources"] = [format_resource_display(r) for r in raw_resources]

    return _serialize(doc)
