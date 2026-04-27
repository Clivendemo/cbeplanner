"""
Schemes of Work routes.

Handles:
- Scheme generation (persists to db.schemes, returns schemeId)
- Listing user's schemes (My Schemes)
- Fetching a single scheme by ID
- Deleting a scheme
- Paid PDF download (atomic KES 15 deduction, auto-refund on failure)
- Supporting reads: lessons-per-week config and topic list
"""
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, List, Optional
import uuid as uuid_lib

from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.deps import (
    api_router, db, logger,
    SCHEME_DOWNLOAD_COST, to_int, validate_object_id, verify_token, serialize_doc,
)
from scheme_generator import (
    generate_scheme_pdf, get_lessons_per_week, get_assessment_for_slo,
    generate_inquiry_questions, generate_learning_experiences, generate_learning_resources,
    derive_inquiry_from_slo, format_slo_with_prefix,
)
from slot_service import format_resource_display


# Generated schemes expire 24 hours after creation. MongoDB TTL index on
# `expiresAt` handles physical deletion; endpoints also defensively filter
# expired rows so the TTL sweep lag window never leaks stale data to users.
SCHEME_TTL_HOURS = 24


# ==================== SCHEME HELPER FUNCTIONS ====================

def _format_slo_for_scheme(raw_slo: str, is_kiswahili: bool = False) -> str:
    """Clean a lesson SLO for scheme display.

    Strips prefixes and normalises wording. Kiswahili subjects use KICD standard.
    """
    import re
    if not raw_slo:
        return ""

    text = str(raw_slo).strip()

    if is_kiswahili:
        patterns = [
            r"^(?:Kufikia\s+mwisho\s+wa\s+somo,?\s*mwanafunzi\s+aweze\s+(?:kuweza\s+)?(?:ku)?)",
            r"^(?:Mwanafunzi\s+aweze\s+(?:kuweza\s+)?(?:ku)?)",
            r"^(?:Aweze\s+(?:kuweza\s+)?(?:ku)?)",
        ]
        for p in patterns:
            text = re.sub(p, "", text, flags=re.IGNORECASE).strip()
        return text

    patterns = [
        r"^(?:By\s+the\s+end\s+of\s+the\s+(?:lesson|sub-?strand|topic),?\s*)",
        r"^(?:the\s+learner\s+should\s+be\s+able\s+to\s+)",
        r"^(?:learners?\s+(?:should|will)\s+be\s+able\s+to\s+)",
        r"^(?:by\s+the\s+end,?\s*)",
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE).strip()
    return text


def generate_assessment_methods(slo: str, is_kiswahili: bool = False) -> str:
    """Return an appropriate assessment method based on SLO content."""
    if not slo:
        return "Oral questions"

    slo_lower = slo.lower()
    if is_kiswahili:
        if any(k in slo_lower for k in ["andika", "tunga", "buni"]):
            return "Kazi ya maandishi"
        if any(k in slo_lower for k in ["eleza", "jadili", "taja"]):
            return "Maswali ya mdomo"
        if any(k in slo_lower for k in ["onyesha", "igiza"]):
            return "Uchunguzi wa kitendo"
        return "Maswali ya mdomo"

    if any(k in slo_lower for k in ["solve", "calculate", "compute"]):
        return "Written test"
    if any(k in slo_lower for k in ["explain", "describe", "discuss"]):
        return "Oral questions"
    if any(k in slo_lower for k in ["demonstrate", "show", "perform"]):
        return "Observation"
    if any(k in slo_lower for k in ["design", "create", "build"]):
        return "Project work"
    return "Oral questions"


# ==================== BREAK HELPERS ====================

def validate_break(brk: Dict[str, Any], lessons_per_week: int, total_weeks: int) -> Dict[str, Any]:
    """Validate and normalize break data."""
    start_week = to_int(brk.get("startWeek"), 1)
    start_lesson = to_int(brk.get("startLesson"), 1)
    end_week = to_int(brk.get("endWeek"), start_week)
    end_lesson = to_int(brk.get("endLesson"), lessons_per_week)

    start_week = max(1, min(start_week, total_weeks))
    end_week = max(start_week, min(end_week, total_weeks))
    start_lesson = max(1, min(start_lesson, lessons_per_week))
    end_lesson = max(1, min(end_lesson, lessons_per_week))

    if end_week == start_week and end_lesson < start_lesson:
        end_lesson = start_lesson

    return {
        "breakType": brk.get("breakType", "Break"),
        "startWeek": start_week,
        "startLesson": start_lesson,
        "endWeek": end_week,
        "endLesson": end_lesson,
        "startDate": brk.get("startDate"),
    }


def calculate_break_duration(start_week: int, start_lesson: int, end_week: int, end_lesson: int, lessons_per_week: int) -> int:
    """Calculate total lessons covered by a break."""
    if start_week == end_week:
        return (end_lesson - start_lesson) + 1
    first_week_lessons = lessons_per_week - start_lesson + 1
    full_weeks = (end_week - start_week - 1) * lessons_per_week
    last_week_lessons = end_lesson
    return first_week_lessons + full_weeks + last_week_lessons


# ==================== PYDANTIC REQUEST MODELS ====================

class SchemeGenerateRequest(BaseModel):
    gradeId: str
    subjectId: str
    term: int
    year: int = datetime.now().year
    totalWeeks: int = 12
    lessonsPerWeek: Optional[int] = None
    selectedTopics: List[str]
    breaks: List[Dict[str, Any]] = []
    doubleLesson: Optional[Dict[str, Any]] = None
    includeCarryOver: bool = False


# ==================== READ ENDPOINTS ====================

@api_router.get("/schemes")
async def get_schemes(user: dict = Depends(verify_token)):
    # Defensive filter on expiresAt — TTL sweep runs ~every 60s so it's possible
    # a just-expired row would otherwise linger in the list.
    now = datetime.utcnow()
    schemes = await db.schemes.find({
        "teacherId": user["id"],
        "$or": [
            {"expiresAt": {"$exists": False}},
            {"expiresAt": {"$gt": now}},
        ],
    }).sort("createdAt", -1).to_list(100)
    return {"success": True, "schemes": [serialize_doc(s) for s in schemes]}


@api_router.get("/schemes/config/lessons-per-week")
async def get_lessons_per_week_config(
    gradeId: str,
    subjectId: str,
    user: dict = Depends(verify_token),
):
    """Get the default lessons per week for a subject in a grade."""
    grade_oid = validate_object_id(gradeId, "grade id")
    subject_oid = validate_object_id(subjectId, "subject id")
    grade = await db.grades.find_one({"_id": grade_oid})
    subject = await db.subjects.find_one({"_id": subject_oid})

    if not grade or not subject:
        raise HTTPException(status_code=404, detail="Invalid grade or subject")

    lessons = get_lessons_per_week(grade["name"], subject["name"])
    return {
        "success": True,
        "lessonsPerWeek": lessons,
        "gradeName": grade["name"],
        "subjectName": subject["name"],
    }


@api_router.get("/schemes/topics/{subjectId}")
async def get_scheme_topics(subjectId: str, user: dict = Depends(verify_token)):
    """Get all topics (strands/substrands) for topic selection UI."""
    strands = await db.strands.find({"subjectId": subjectId}).sort("order", 1).to_list(100)

    topics = []
    for strand in strands:
        strand_id = str(strand["_id"])
        substrands = await db.substrands.find({"strandId": strand_id}).sort("order", 1).to_list(100)

        substrand_items = []
        for ss in substrands:
            ss_id = str(ss["_id"])
            slo_count = await db.slos.count_documents({"substrandId": ss_id})
            substrand_items.append({
                "id": ss_id,
                "name": ss["name"],
                "sloCount": slo_count,
            })

        topics.append({
            "id": strand_id,
            "name": strand["name"],
            "substrands": substrand_items,
            "totalSlos": sum(s["sloCount"] for s in substrand_items),
        })

    return {"success": True, "topics": topics}


# Dynamic scheme ID route — MUST come after all static /schemes/... routes
@api_router.get("/schemes/{scheme_id}")
async def get_scheme(scheme_id: str, user: dict = Depends(verify_token)):
    oid = validate_object_id(scheme_id, "scheme id")
    scheme = await db.schemes.find_one({"_id": oid, "teacherId": user["id"]})
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    # 24h expiry window — surface a 410 Gone with a clean message rather than
    # a generic 404 so the UI can show an "expired" state if it wants to.
    expires_at = scheme.get("expiresAt")
    if expires_at and expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=410,
            detail="This scheme has expired. Schemes are automatically removed 24 hours after generation."
        )
    return {"success": True, "scheme": serialize_doc(scheme)}


# ==================== GENERATE (V2) ====================

@api_router.post("/schemes/generate-v2")
async def generate_scheme_v2(request: SchemeGenerateRequest, user: dict = Depends(verify_token)):
    """Generate scheme of work from selected topics and persist to db.schemes."""
    try:
        grade_oid = validate_object_id(request.gradeId, "grade id")
        subject_oid = validate_object_id(request.subjectId, "subject id")
        grade = await db.grades.find_one({"_id": grade_oid})
        subject = await db.subjects.find_one({"_id": subject_oid})

        if not grade or not subject:
            raise HTTPException(status_code=404, detail="Invalid grade or subject")

        total_weeks = to_int(request.totalWeeks, 12)
        lessons_per_week = to_int(request.lessonsPerWeek) if request.lessonsPerWeek else get_lessons_per_week(grade["name"], subject["name"])

        user_profile = await db.users.find_one({"firebaseUid": user.get("firebaseUid", user.get("id", ""))})
        school_name = user_profile.get("schoolName", "") if user_profile else ""

        is_kiswahili = 'kiswahili' in subject["name"].lower() or 'fasihi' in subject["name"].lower()

        curriculum_content = []

        for substrand_id in request.selectedTopics:
            try:
                ss_oid = ObjectId(substrand_id)
            except Exception:
                continue
            substrand = await db.substrands.find_one({"_id": ss_oid})
            if not substrand:
                continue
            strand = await db.strands.find_one({"_id": ObjectId(substrand["strandId"])})
            if not strand:
                continue

            num_lessons = substrand.get("number_of_lessons")
            if not num_lessons or int(num_lessons) < 1:
                slo_count = await db.slos.count_documents({"substrandId": substrand_id})
                num_lessons = max(1, slo_count)
            else:
                num_lessons = int(num_lessons)

            parent_slos = await db.slos.find(
                {"substrandId": substrand_id}
            ).sort("order", 1).to_list(100)
            if not parent_slos:
                continue

            learning_act = await db.learning_activities.find_one({"substrandId": substrand_id})

            raw_slots = await db.lesson_slo_slots.find(
                {"substrandId": substrand_id}
            ).sort("slot_index", 1).to_list(500)
            slots_by_idx = {s["slot_index"]: s for s in raw_slots}

            for idx in range(num_lessons):
                slot = slots_by_idx.get(idx)
                parent_slo = parent_slos[idx % len(parent_slos)]
                parent_slo_id = str(parent_slo["_id"])

                slo_text = slot["outcome"] if (slot and slot.get("outcome")) else parent_slo["name"]

                inquiry_q = ""
                if slot and slot.get("key_inquiry_question"):
                    inquiry_q = slot["key_inquiry_question"]

                competencies = (slot.get("competencies") if slot else None) or []
                values_list = (slot.get("values") if slot else None) or []
                pcis = (slot.get("pcis") if slot else None) or []

                if not competencies:
                    mapping = await db.slo_mappings.find_one({"sloId": parent_slo_id})
                    if mapping:
                        for cid in mapping.get("competencyIds", []):
                            doc = await db.competencies.find_one({"_id": ObjectId(cid)})
                            if doc:
                                competencies.append(doc["name"])
                        if not values_list:
                            for vid in mapping.get("valueIds", []):
                                doc = await db.values.find_one({"_id": ObjectId(vid)})
                                if doc:
                                    values_list.append(doc["name"])
                        if not pcis:
                            for pid in mapping.get("pciIds", []):
                                doc = await db.pcis.find_one({"_id": ObjectId(pid)})
                                if doc:
                                    pcis.append(doc["name"])

                raw_resources = (slot.get("resources") if slot else None) or []
                if raw_resources:
                    formatted_resources = [format_resource_display(r) for r in raw_resources]
                elif learning_act:
                    formatted_resources = learning_act.get("learning_resources", [])
                else:
                    formatted_resources = []

                activities = (slot.get("learning_activities") if slot else None) or (
                    learning_act.get("development_activities", []) if learning_act else []
                )
                assessment = (slot.get("assessment_methods") if slot else None) or (
                    learning_act.get("assessment_methods", []) if learning_act else []
                )

                curriculum_content.append({
                    "strandId": str(strand["_id"]),
                    "strand": strand["name"],
                    "substrandId": substrand_id,
                    "substrand": substrand["name"],
                    "sloId": parent_slo_id,
                    "slo": slo_text,
                    "sloDescription": parent_slo.get("description", parent_slo["name"]),
                    "lessonInSubstrand": idx + 1,
                    "totalLessonsInSubstrand": num_lessons,
                    "competencies": competencies or ["Critical Thinking", "Communication"],
                    "values": values_list or ["Responsibility", "Respect"],
                    "pcis": pcis,
                    "learningActivities": activities,
                    "resources": formatted_resources,
                    "assessmentMethods": assessment,
                    "_slotInquiry": inquiry_q,
                    # Substrand-level KICD-seeded inquiry questions; cycled per
                    # lesson position so multi-lesson substrands get variety.
                    "_substrandInquiries": (learning_act.get("inquiry_questions", []) if learning_act else []),
                })

        if not curriculum_content:
            raise HTTPException(status_code=400, detail="No valid topics selected")

        # Process breaks
        breaks_map = {}
        validated_breaks = []

        for brk in request.breaks:
            validated = validate_break(brk, lessons_per_week, total_weeks)
            validated_breaks.append(validated)

            start_week = validated["startWeek"]
            start_lesson = validated["startLesson"]
            end_week = validated["endWeek"]
            end_lesson = validated["endLesson"]

            current_week = start_week
            current_lesson = start_lesson
            while True:
                breaks_map[(current_week, current_lesson)] = validated["breakType"]
                if current_week == end_week and current_lesson == end_lesson:
                    break
                current_lesson += 1
                if current_lesson > lessons_per_week:
                    current_lesson = 1
                    current_week += 1
                if current_week > end_week:
                    break

        # Double lesson config
        double_lesson = request.doubleLesson or {}
        double_enabled = bool(double_lesson.get("enabled"))
        double_position = str(double_lesson.get("position", "")) if double_enabled else ""

        # Build scheme lessons grid
        lessons = []
        content_index = 0

        for week in range(1, total_weeks + 1):
            lesson_num = 1
            while lesson_num <= lessons_per_week:
                is_double = False
                lesson_display = str(lesson_num)

                if double_enabled and double_position:
                    parts = double_position.split('-')
                    if len(parts) == 2:
                        try:
                            first = int(parts[0])
                            second = int(parts[1])
                            if lesson_num == first:
                                is_double = True
                                lesson_display = f"{first}-{second}"
                        except ValueError:
                            pass

                break_key = (week, lesson_num)
                break_key2 = (week, lesson_num + 1) if is_double else None
                if break_key in breaks_map or (break_key2 and break_key2 in breaks_map):
                    lessons.append({
                        "week": week,
                        "lesson": lesson_display,
                        "isBreak": True,
                        "isDouble": is_double,
                        "breakType": breaks_map.get(break_key) or breaks_map.get(break_key2),
                    })
                    lesson_num += 2 if is_double else 1
                    continue

                if content_index < len(curriculum_content):
                    content = curriculum_content[content_index]
                    slot_inquiry = content.get("_slotInquiry")
                    substrand_iqs = content.get("_substrandInquiries") or []

                    # Key inquiry question priority:
                    #  1. lesson_slo_slots.key_inquiry_question (admin-curated, per lesson)
                    #  2. learning_activities.inquiry_questions[] cycled by lesson position
                    #     (KICD-seeded, hand-curated per substrand — grammatically correct)
                    #  3. SLO-derived question (algorithmic — used only when DB has nothing)
                    #  4. Generic fallback
                    if slot_inquiry:
                        inquiry_qs = slot_inquiry
                    elif substrand_iqs:
                        # 1-based lesson position cycled through the array
                        pos = max(0, content.get("lessonInSubstrand", 1) - 1)
                        inquiry_qs = substrand_iqs[pos % len(substrand_iqs)]
                    else:
                        derived = derive_inquiry_from_slo(content["slo"], is_kiswahili)
                        if derived:
                            inquiry_qs = derived
                        else:
                            inquiry_qs = generate_inquiry_questions(
                                content["strand"],
                                content["substrand"],
                                content["slo"],
                            )

                    experiences = content.get("learningActivities", [])
                    if not experiences:
                        experiences = generate_learning_experiences(
                            content["strand"],
                            content["substrand"],
                            content["slo"],
                        )

                    resources = content.get("resources", [])
                    if not resources:
                        resources = generate_learning_resources(
                            content["strand"],
                            content["substrand"],
                        )

                    assessment = content.get("assessmentMethods", [])
                    if not assessment:
                        assessment = get_assessment_for_slo(content["slo"], is_kiswahili)

                    lessons.append({
                        "week": week,
                        "lesson": lesson_display,
                        "isDouble": is_double,
                        "strand": content["strand"],
                        "substrand": content["substrand"],
                        "slo": format_slo_with_prefix(
                            _format_slo_for_scheme(content["slo"], is_kiswahili),
                            is_kiswahili,
                        ),
                        "lessonInSubstrand": content.get("lessonInSubstrand", 1),
                        "totalLessonsInSubstrand": content.get("totalLessonsInSubstrand", 1),
                        "keyInquiryQuestions": inquiry_qs,
                        "learningExperiences": experiences[:4] if isinstance(experiences, list) else [experiences],
                        "learningResources": resources[:4] if isinstance(resources, list) else [resources],
                        "assessmentMethods": assessment[:2] if isinstance(assessment, list) else [assessment],
                        "competencies": content["competencies"],
                        "values": content["values"],
                        "pcis": content.get("pcis", []),
                    })

                    content_index += 1
                    lesson_num += 2 if is_double else 1
                else:
                    if request.includeCarryOver:
                        break
                    content_index = 0
                    lesson_num += 1

        scheme_data = {
            "teacherId": user.get("id", ""),
            "gradeId": request.gradeId,
            "gradeName": grade["name"],
            "subjectId": request.subjectId,
            "subjectName": subject["name"],
            "term": request.term,
            "year": request.year,
            "totalWeeks": total_weeks,
            "lessonsPerWeek": lessons_per_week,
            "schoolName": school_name,
            "selectedTopics": request.selectedTopics,
            "lessons": lessons,
            "breaks": validated_breaks,
            "doubleLesson": request.doubleLesson,
            "includeCarryOver": request.includeCarryOver,
            "createdAt": datetime.utcnow(),
        }

        # Persist for My Schemes list/preview/download workflow
        scheme_record = dict(scheme_data)
        scheme_record["inputs"] = {
            "gradeId": request.gradeId,
            "subjectId": request.subjectId,
            "term": request.term,
            "year": request.year,
            "totalWeeks": total_weeks,
            "lessonsPerWeek": lessons_per_week,
            "selectedTopics": request.selectedTopics,
            "breaks": validated_breaks,
            "doubleLesson": request.doubleLesson,
            "includeCarryOver": request.includeCarryOver,
        }
        scheme_record["isPaid"] = False
        scheme_record["downloadCount"] = 0
        scheme_record["lastDownloadedAt"] = None
        scheme_record["updatedAt"] = datetime.utcnow()
        # Schemes auto-expire 24h after generation. The TTL index on `expiresAt`
        # (see _create_indexes in server.py) will physically delete the row.
        scheme_record["expiresAt"] = scheme_record["createdAt"] + timedelta(hours=SCHEME_TTL_HOURS)
        insert_result = await db.schemes.insert_one(scheme_record)
        scheme_id = str(insert_result.inserted_id)
        scheme_data["id"] = scheme_id
        scheme_data["expiresAt"] = scheme_record["expiresAt"].isoformat()

        return {
            "success": True,
            "schemeId": scheme_id,
            "scheme": scheme_data,
            "summary": {
                "totalLessons": len([l for l in lessons if not l.get("isBreak")]),
                "totalBreaks": len([l for l in lessons if l.get("isBreak")]),
                "doubleLessons": len([l for l in lessons if l.get("isDouble")]),
                "topics": len(request.selectedTopics),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating scheme: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to generate scheme", "error": str(e)},
        )


# ==================== MY SCHEMES — owner-scoped preview & paid download ====================

@api_router.delete("/schemes/{scheme_id}")
async def delete_scheme(scheme_id: str, user: dict = Depends(verify_token)):
    """Delete an owned scheme record."""
    oid = validate_object_id(scheme_id, "scheme id")
    result = await db.schemes.delete_one({"_id": oid, "teacherId": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return {"success": True}


@api_router.post("/schemes/{scheme_id}/download")
async def download_owned_scheme(scheme_id: str, user: dict = Depends(verify_token)):
    """Download a stored scheme (owner only). Charges KES 15 atomically, refunds on failure."""
    oid = validate_object_id(scheme_id, "scheme id")
    scheme = await db.schemes.find_one({"_id": oid, "teacherId": user["id"]})
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    # Block download on expired schemes BEFORE any wallet charge.
    expires_at = scheme.get("expiresAt")
    if expires_at and expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=410,
            detail="This scheme has expired. Schemes are automatically removed 24 hours after generation."
        )

    firebase_uid = user.get("firebaseUid")
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Invalid user session")

    user_profile = await db.users.find_one({"firebaseUid": firebase_uid})
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    current_balance = user_profile.get("walletBalance", 0)
    if current_balance < SCHEME_DOWNLOAD_COST:
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Insufficient wallet balance",
                "required": SCHEME_DOWNLOAD_COST,
                "current": current_balance,
            },
        )

    ledger_ref = f"SCHEME-{uuid_lib.uuid4().hex[:12].upper()}"

    ledger_entry = {
        "userId": user["id"],
        "type": "DEBIT",
        "amount": SCHEME_DOWNLOAD_COST,
        "reference": ledger_ref,
        "source": "SCHEME_DOWNLOAD",
        "schemeId": scheme_id,
        "description": f"Scheme of Work — {scheme.get('subjectName', 'Subject')} Term {scheme.get('term', 1)}",
        "createdAt": datetime.utcnow(),
    }
    try:
        await db.wallet_ledger.insert_one(ledger_entry)
    except Exception:
        raise HTTPException(status_code=500, detail="Payment processing error. Please try again.")

    result = await db.users.update_one(
        {"firebaseUid": firebase_uid, "walletBalance": {"$gte": SCHEME_DOWNLOAD_COST}},
        {"$inc": {"walletBalance": -SCHEME_DOWNLOAD_COST}},
    )
    if result.modified_count == 0:
        await db.wallet_ledger.delete_one({"reference": ledger_ref})
        raise HTTPException(status_code=402, detail="Insufficient wallet balance")

    await db.wallets.update_one(
        {"userId": user["id"]},
        {"$inc": {"balance": -SCHEME_DOWNLOAD_COST}, "$set": {"updatedAt": datetime.utcnow()}},
        upsert=True,
    )

    logger.info(f"Scheme {scheme_id} download charged KES {SCHEME_DOWNLOAD_COST} for user {user['id']}. Ref: {ledger_ref}")

    try:
        render_payload = {k: v for k, v in scheme.items() if k not in {"_id", "inputs", "isPaid", "downloadCount", "lastDownloadedAt", "updatedAt"}}
        pdf_bytes = generate_scheme_pdf(render_payload)

        subject = scheme.get('subjectName', 'Subject').replace(' ', '_')
        grade = scheme.get('gradeName', 'Grade').replace(' ', '_')
        term = scheme.get('term', 1)
        filename = f"Scheme_{subject}_{grade}_Term{term}.pdf"

        await db.schemes.update_one(
            {"_id": oid},
            {
                "$set": {
                    "isPaid": True,
                    "lastDownloadedAt": datetime.utcnow(),
                    "lastPaymentReference": ledger_ref,
                },
                "$inc": {"downloadCount": 1},
            },
        )

        updated_user = await db.users.find_one({"firebaseUid": firebase_uid})
        new_balance = updated_user.get("walletBalance", 0) if updated_user else 0

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
                "X-New-Balance": str(new_balance),
            },
        )
    except Exception as e:
        # Refund on failure
        await db.users.update_one(
            {"firebaseUid": firebase_uid},
            {"$inc": {"walletBalance": SCHEME_DOWNLOAD_COST}},
        )
        await db.wallet_ledger.delete_one({"reference": ledger_ref})
        await db.wallets.update_one(
            {"userId": user["id"]},
            {"$inc": {"balance": SCHEME_DOWNLOAD_COST}, "$set": {"updatedAt": datetime.utcnow()}},
        )
        logger.error(f"Scheme {scheme_id} PDF generation failed, refunded user {user['id']}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF. Your payment has been refunded.")
