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
    ADMIN_EMAILS,
)
from scheme_generator import (
    generate_scheme_pdf, get_lessons_per_week, get_assessment_for_slo,
    generate_learning_experiences, generate_learning_resources,
    format_slo_with_prefix, clean_kiq_list,
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
            r"^(?:Kufikia\s+mwisho\s+wa\s+somo,?\s*mwanafunzi\s+aweze\s+(?:kuweza\s+)?(?:ku)?\s*:?\s*)",
            r"^(?:Mwanafunzi\s+aweze\s+(?:kuweza\s+)?(?:ku)?\s*:?\s*)",
            r"^(?:Aweze\s+(?:kuweza\s+)?(?:ku)?\s*:?\s*)",
        ]
        for p in patterns:
            text = re.sub(p, "", text, flags=re.IGNORECASE).strip()
        return text

    # NOTE: every pattern below ends in \s*:?\s* rather than a bare \s+.
    # Curriculum data isn't consistently punctuated — some SLO records
    # store "the learner should be able to " (trailing space, no colon),
    # others store "the learner should be able to:" (trailing colon, no
    # space) as its own line with the actual outcomes on following lines.
    # The old \s+-only patterns only matched the first form, so the second
    # silently failed to strip at all and the raw "the learner should be
    # able to:" text leaked straight into the rendered scheme as if it
    # were itself an outcome. \s*:?\s* matches both forms, and also
    # collapses a line that is *purely* this phrase down to "" (correctly
    # signalling "nothing left here, drop this line") rather than leaving
    # a dangling, half-stripped fragment.
    patterns = [
        r"^(?:By\s+the\s+end\s+of\s+the\s+(?:lesson|sub-?strand|topic),?\s*(?:the\s+learner\s+should\s+be\s+able\s+to)?\s*:?\s*)",
        r"^(?:the\s+learner\s+should\s+be\s+able\s+to\s*:?\s*)",
        r"^(?:learners?\s+(?:should|will)\s+be\s+able\s+to\s*:?\s*)",
        r"^(?:by\s+the\s+end,?\s*:?\s*)",
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE).strip()
    return text


def _slo_outcome_lines(raw_slo: str, is_kiswahili: bool = False) -> List[str]:
    """Break a raw SLO outcome statement into one or more clean bullet lines.

    Curriculum data isn't uniformly clean. Some SLO `name` fields hold a
    single sentence ("Define the term business transaction"); others hold a
    multi-line blob that already contains its own "the learner should be
    able to:" sub-heading plus several outcome lines crammed into the same
    field (an authoring/extraction artifact from whichever pipeline the
    substrand originally came through). Rendering the second kind as a
    single bullet produces a broken-looking cell — one bullet reading just
    "- the learner should be able to:" with the *real* outcomes dangling
    underneath, unbulleted.

    This always returns a flat list of individually-cleaned outcome lines
    — never a single line still carrying an embedded preamble or a raw
    newline — so every call site that bullets SLO text gets the same
    guarantee regardless of how messy the source record is.
    """
    import re
    if not raw_slo:
        return []

    raw_lines = str(raw_slo).replace("\r\n", "\n").split("\n")
    lines: List[str] = []
    for ln in raw_lines:
        ln = ln.strip()
        if not ln:
            continue
        cleaned = _format_slo_for_scheme(ln, is_kiswahili)
        if not cleaned:
            # A line that was *entirely* a preamble phrase (with or without
            # a trailing colon) reduces to "" once genuinely stripped —
            # drop it rather than keep a bare fragment or the untouched
            # original.
            continue
        # Strip any bullet marker the raw data may already carry so we
        # never end up with a doubled "- - Define the term…" once our own
        # leading dash is added by the caller.
        cleaned = re.sub(r"^[-•*]\s*", "", cleaned).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def _dedupe_lines(lines: List[str]) -> List[str]:
    """Drop exact duplicate outcome lines, keeping the first occurrence.

    Duplicate SLO records do exist in the curriculum data (the same
    substrand occasionally has two near-identical SLO rows), and merging
    that into one row would otherwise print the same bullet twice with no
    legitimate reason for it. Comparison is case/whitespace-insensitive so
    trivial formatting differences ("Define the term." vs "define the
    term.") still count as the same outcome.
    """
    seen = set()
    out: List[str] = []
    for ln in lines:
        key = " ".join(ln.lower().split())
        if key and key not in seen:
            seen.add(key)
            out.append(ln)
    return out


def _resolve_content_kiq(content: Dict[str, Any]) -> str:
    """Priority-resolve a single content item's Key Inquiry Question.

    1. lesson_slo_slots.key_inquiry_question — admin's per-lesson override.
    2. slos.key_inquiry_questions[0] — the canonical, KICD-extracted value.
    3. "" — never algorithmically generate.
    """
    slot_inquiry = content.get("_slotInquiry")
    slo_inquiries = content.get("_sloInquiries") or []
    if slot_inquiry:
        return slot_inquiry
    if slo_inquiries:
        return slo_inquiries[0]
    return ""


_REVISION_ACTIVITIES_EN = [
    "Class discussion recapping key concepts covered",
    "Learners work through past-paper/revision questions",
    "Question-and-answer session on the topics covered",
]
_REVISION_ACTIVITIES_SW = [
    "Majadiliano darasani ya kuimarisha dhana zilizofunzwa",
    "Wanafunzi kufanya maswali ya marudio/karatasi za zamani",
    "Kipindi cha maswali na majibu kuhusu mada zilizofunzwa",
]
_REVISION_RESOURCES_EN = ["Past papers", "Revision questions", "Learner's notes"]
_REVISION_RESOURCES_SW = ["Karatasi za zamani", "Maswali ya marudio", "Daftari la mwanafunzi"]
_REVISION_ASSESSMENT_EN = ["Oral questions", "Written revision exercise"]
_REVISION_ASSESSMENT_SW = ["Maswali ya mdomo", "Zoezi la maandishi la marudio"]


def _build_revision_content(strand_name: str, is_kiswahili: bool) -> Dict[str, Any]:
    """A pseudo curriculum-content item representing a revision/consolidation
    lesson for a strand, rather than a specific SLO.

    Used to fill genuinely spare time (when selected content is shorter than
    the term) instead of the old behaviour of either repeating earlier
    lessons verbatim or leaving trailing weeks blank. Deliberately generic —
    no fabricated Key Inquiry Question, no invented SLO outcome — this is
    revision time, not new curriculum content, and should never be
    mistaken for either.
    """
    return {"isRevision": True, "strand": strand_name}


def _build_lesson_fields(content: Dict[str, Any], is_kiswahili: bool) -> Dict[str, Any]:
    """Build the display field-set for ONE curriculum content item.

    Returns everything a lesson row needs except week/lesson/isDouble, which
    the grid-building loop attaches afterward. Used both for ordinary
    (unmerged) rows and as the per-item building block inside
    _merge_lesson_items below, so a merged row with exactly one item behaves
    identically to the original unmerged code path.
    """
    if content.get("isRevision"):
        strand_name = content.get("strand", "")
        return {
            "strand": strand_name,
            "substrand": "Marudio" if is_kiswahili else "Revision",
            "slo": (
                f"Marudio ya {strand_name}" if is_kiswahili
                else f"Revision of {strand_name}"
            ),
            "lessonInSubstrand": 1,
            "totalLessonsInSubstrand": 1,
            "keyInquiryQuestions": "",
            "learningExperiences": (_REVISION_ACTIVITIES_SW if is_kiswahili else _REVISION_ACTIVITIES_EN)[:4],
            "learningResources": (_REVISION_RESOURCES_SW if is_kiswahili else _REVISION_RESOURCES_EN)[:4],
            "assessmentMethods": (_REVISION_ASSESSMENT_SW if is_kiswahili else _REVISION_ASSESSMENT_EN)[:2],
            "competencies": [],
            "values": [],
            "pcis": [],
        }

    inquiry_qs = _resolve_content_kiq(content)

    experiences = content.get("learningActivities", [])
    if not experiences:
        experiences = generate_learning_experiences(
            content["strand"], content["substrand"], content["slo"], is_kiswahili,
        )

    resources = content.get("resources", [])
    if not resources:
        resources = generate_learning_resources(content["strand"], content["substrand"], is_kiswahili)

    assessment = content.get("assessmentMethods", [])
    if not assessment:
        assessment = get_assessment_for_slo(content["slo"], is_kiswahili)

    return {
        "strand": content["strand"],
        "substrand": content["substrand"],
        "slo": (
            content["slo"]
            if content.get("sloPreFormatted")
            else format_slo_with_prefix(
                _format_slo_for_scheme(content["slo"], is_kiswahili),
                is_kiswahili,
            )
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
    }


def _merge_lesson_items(items: List[Dict[str, Any]], is_kiswahili: bool) -> Dict[str, Any]:
    """Combine 1+ curriculum content items into a single lesson row.

    Used for:
      - a double lesson merging two adjacent items into one extended session
      - a compression group merging however many items were assigned to one
        row when the term doesn't have enough slots for one-item-per-row

    With exactly one item this must produce the same output as the plain
    (unmerged) path, so single-item schemes are byte-for-byte unaffected.
    """
    if len(items) == 1:
        return _build_lesson_fields(items[0], is_kiswahili)

    built = [_build_lesson_fields(c, is_kiswahili) for c in items]

    # Strand: still joined inline with " / " when a row spans more than one
    # (rare — only when a double lesson straddles a strand boundary, since
    # compression segments are already grouped by strand). Sub-strand: each
    # distinct name on its own line with a blank line between them, per
    # request — a merged row combining two sub-strands reads as two clearly
    # separate names stacked vertically, not one run-together line.
    def _dedupe_join(values, sep=" / "):
        seen = []
        for v in values:
            if v and v not in seen:
                seen.append(v)
        return sep.join(seen)

    strand = _dedupe_join([b["strand"] for b in built])
    substrand = _dedupe_join([b["substrand"] for b in built], sep="\n\n")

    # SLO text: one shared "By the end of the lesson…" preamble with every
    # item's own outcome statement bulleted underneath. Each item's `slo`
    # field may already be a pre-formatted multi-bullet block (if it was
    # itself a combine_all_slos group) — in that case take only the bullet
    # lines, dropping its own preamble, so we never nest one "By the end of
    # the lesson…" inside another.
    bullets: List[str] = []
    for c, b in zip(items, built):
        raw = b["slo"]
        if c.get("isRevision"):
            # b["slo"] is already the final "Revision of <strand>" text —
            # no preamble to strip, no "By the end of the lesson…" body to
            # derive it from (there is no raw content['slo'] on a revision
            # placeholder at all).
            bullets.append(raw)
        elif c.get("sloPreFormatted"):
            # Existing bulleted block: strip the first (preamble) line and
            # the leading "- " each bullet already carries, so it can be
            # deduped/re-bulleted on the same footing as the other branches.
            lines = raw.split("\n")
            bullets.extend(
                line[1:].strip() if line.strip().startswith("-") else line.strip()
                for line in lines[1:] if line.strip()
            )
        else:
            # Rare fallback path (content-building couldn't produce any
            # clean outcome lines for this item at all — see the "else"
            # branch above). Still fan out through the same helper rather
            # than assuming c["slo"] is a single clean sentence: if it's
            # genuinely a raw, uncleaned multi-line blob, this is what
            # prevents it turning into one bullet containing an embedded
            # "the learner should be able to:" line and several unbulleted
            # outcomes underneath it.
            bullets.extend(_slo_outcome_lines(c["slo"], is_kiswahili))
    # A double lesson or a compressed row can combine items whose SLOs
    # happen to be identical (duplicate curriculum records, or the same
    # substrand legitimately repeating a sub-point) — never print the same
    # outcome twice just because it arrived from two different items.
    bullets = [f"- {line}" for line in _dedupe_lines(bullets)]
    if is_kiswahili:
        slo_text = "Kufikia mwisho wa somo, mwanafunzi aweze:\n" + "\n".join(bullets)
    else:
        slo_text = "By the end of the lesson the learner should be able to:\n" + "\n".join(bullets)

    # KIQs: dedupe across items, keep as a list so the PDF/web renderer can
    # show every distinct question bulleted rather than only the first.
    kiq_list: List[str] = []
    for b in built:
        q = b["keyInquiryQuestions"]
        if q and q not in kiq_list:
            kiq_list.append(q)

    def _merge_field_lists(field: str, cap: int) -> List[str]:
        out: List[str] = []
        for b in built:
            vals = b[field] if isinstance(b[field], list) else [b[field]]
            for v in vals:
                if v and v not in out:
                    out.append(v)
        return out[:cap]

    return {
        "strand": strand,
        "substrand": substrand,
        "slo": slo_text,
        "lessonInSubstrand": built[0]["lessonInSubstrand"],
        "totalLessonsInSubstrand": built[0]["totalLessonsInSubstrand"],
        "keyInquiryQuestions": kiq_list,
        "learningExperiences": _merge_field_lists("learningExperiences", 4),
        "learningResources": _merge_field_lists("learningResources", 4),
        "assessmentMethods": _merge_field_lists("assessmentMethods", 2),
        "competencies": _merge_field_lists("competencies", 6),
        "values": _merge_field_lists("values", 6),
        "pcis": _merge_field_lists("pcis", 6),
    }


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
    # Substrand IDs (a subset of selectedTopics) that are carried over from a
    # previous term and weren't fully covered. These are scheduled first, in
    # the order given, ahead of the term's own new content — see the
    # compression/ordering logic in generate_scheme_v2.
    carryOverTopics: List[str] = []
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
    # Capped at 2000, matching /admin/strands and /admin/substrands — this
    # was previously capped at 100, which silently dropped every strand past
    # the 100th for a subject like English with 195 strands (one substrand
    # each). Those strands weren't broken or missing data; they just never
    # made it into this response, so they could never be selected here even
    # though they showed up fine in the admin curriculum panel.
    strands = await db.strands.find({"subjectId": subjectId}).sort("order", 1).to_list(2000)

    topics = []
    for strand in strands:
        strand_id = str(strand["_id"])
        substrands = await db.substrands.find({"strandId": strand_id}).sort("order", 1).to_list(2000)

        substrand_items = []
        for ss in substrands:
            ss_id = str(ss["_id"])
            slo_count = await db.slos.count_documents({"substrandId": ss_id})
            substrand_items.append({
                "id": ss_id,
                "name": ss["name"],
                "sloCount": slo_count,
                "term": ss.get("term"),
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

        # Hidden grades/subjects (admin still finishing curriculum updates)
        # are already excluded from the teacher-facing dropdown, but that's
        # a client-side convenience, not enforcement — this is the actual
        # gate, closing off direct API calls for anything the dropdown
        # wouldn't have offered. Admins are exempt so they can generate
        # against unfinished/hidden content themselves to check it before
        # making it visible.
        is_admin = user.get("email", "").lower().strip() in ADMIN_EMAILS
        if not is_admin:
            if not grade.get("isVisible", True) or not subject.get("isVisible", True):
                raise HTTPException(
                    status_code=403,
                    detail="This grade or subject isn't available yet. Please check back later.",
                )

        total_weeks = to_int(request.totalWeeks, 12)
        lessons_per_week = to_int(request.lessonsPerWeek) if request.lessonsPerWeek else get_lessons_per_week(grade["name"], subject["name"])

        user_profile = await db.users.find_one({"firebaseUid": user.get("firebaseUid", user.get("id", ""))})
        school_name = user_profile.get("schoolName", "") if user_profile else ""

        is_kiswahili = 'kiswahili' in subject["name"].lower() or 'fasihi' in subject["name"].lower()

        curriculum_content = []

        # Carry-over substrands (content not fully covered in a previous
        # term) are scheduled first, since they're already overdue. Within
        # each group (carry-over, then the rest), topics are placed in the
        # SAME order they appear in the topic-picker list — i.e. by
        # (strand.order, substrand.order), the exact sort GET
        # /schemes/topics/{subjectId} uses to build that list — rather than
        # the order the teacher happened to tap them in. selectedTopics
        # arrives from the frontend as Array.from(a JS Set), which preserves
        # insertion/click order, not curriculum order, so without this
        # re-sort a scheme could teach topic 12 before topic 3 just because
        # it was clicked first.
        selected_oids = []
        for ss_id in request.selectedTopics:
            try:
                selected_oids.append(ObjectId(ss_id))
            except Exception:
                continue

        substrand_order_docs = await db.substrands.find(
            {"_id": {"$in": selected_oids}}
        ).to_list(len(selected_oids) or 1)
        substrand_order_by_id = {str(d["_id"]): d for d in substrand_order_docs}

        strand_ids_needed = {
            d["strandId"] for d in substrand_order_docs if d.get("strandId")
        }
        strand_oids_needed = []
        for sid in strand_ids_needed:
            try:
                strand_oids_needed.append(ObjectId(sid))
            except Exception:
                continue
        strand_order_docs = await db.strands.find(
            {"_id": {"$in": strand_oids_needed}}
        ).to_list(len(strand_oids_needed) or 1)
        strand_order_by_id = {str(d["_id"]): d for d in strand_order_docs}

        def _sort_key(ss_id: str):
            ss_doc = substrand_order_by_id.get(ss_id)
            if not ss_doc:
                # Selected topic doesn't resolve to a real substrand (bad ID,
                # deleted since selection, etc.) — push it to the very end
                # deterministically rather than crashing the sort.
                return (float('inf'), float('inf'))
            strand_doc = strand_order_by_id.get(str(ss_doc.get("strandId", "")))
            strand_order = strand_doc.get("order") if strand_doc else None
            substrand_order = ss_doc.get("order")
            return (
                strand_order if strand_order is not None else float('inf'),
                substrand_order if substrand_order is not None else float('inf'),
            )

        carry_over_ids = [
            ss_id for ss_id in request.selectedTopics
            if ss_id in (request.carryOverTopics or [])
        ]
        rest_ids = [
            ss_id for ss_id in request.selectedTopics
            if ss_id not in (request.carryOverTopics or [])
        ]
        # Dedupe while preserving whichever bucket a repeated ID landed in
        # first (carry-over takes priority over "rest" for duplicates).
        seen_topics = set()
        ordered_topics: List[str] = []
        for ss_id in sorted(carry_over_ids, key=_sort_key) + sorted(rest_ids, key=_sort_key):
            if ss_id not in seen_topics:
                ordered_topics.append(ss_id)
                seen_topics.add(ss_id)

        for substrand_id in ordered_topics:
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
            # Same cap-too-low bug as the topics endpoint above, but worse
            # here: a substrand with more than 100 SLOs would silently lose
            # the rest from every generated scheme forever (not just hidden
            # from a picker — actually dropped from the round-robin pool
            # below), with no error anywhere to reveal it happened.
            ).sort("order", 1).to_list(2000)
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

                # Single-lesson substrand with multiple SLOs: combine ALL of
                # them into one bulleted list so the scheme row reflects the
                # full lesson scope. Only the SLO text (and KIQs / mappings)
                # change shape — everything downstream (sloId pointer,
                # ordering, lessonInSubstrand counter) stays untouched so
                # checkpointing and per-SLO download flows are unaffected.
                combine_all_slos = num_lessons == 1 and len(parent_slos) > 1

                if combine_all_slos:
                    # Fan each SLO's raw `name` out into 1+ clean bullet
                    # lines rather than assuming one SLO == one bullet.
                    # Some curriculum records store a single clean sentence
                    # ("Define the term business transaction") and fan out
                    # to exactly one bullet; others store a multi-line blob
                    # that already contains its own "the learner should be
                    # able to:" sub-heading plus several outcomes crammed
                    # into the same field — _slo_outcome_lines strips that
                    # sub-heading and splits the rest into one bullet per
                    # real outcome, however many a given record holds.
                    bullets = []
                    for s in parent_slos:
                        for line in _slo_outcome_lines(s.get("name", ""), is_kiswahili):
                            bullets.append(line)
                    bullets = [f"- {line}" for line in _dedupe_lines(bullets)]
                    if is_kiswahili:
                        slo_text = (
                            "Kufikia mwisho wa somo, mwanafunzi aweze:\n"
                            + "\n".join(bullets)
                        )
                    else:
                        slo_text = (
                            "By the end of the lesson the learner should be able to:\n"
                            + "\n".join(bullets)
                        )
                    # Skip the standard prefix logic later — flag with
                    # leading newline that the slo string is already
                    # fully formatted.
                    slo_text_pre_formatted = True
                else:
                    # Even a single SLO can carry the same messy multi-line
                    # blob (raw record already containing "the learner
                    # should be able to:" plus several outcomes crammed
                    # into one field) — route it through the same
                    # fan-out/bullet path as the combined case so every row
                    # in the scheme, single-outcome or multi-outcome, reads
                    # the same way: one preamble line, one bullet per real
                    # outcome, never a dangling half-stripped preamble
                    # fragment.
                    raw_text = slot["outcome"] if (slot and slot.get("outcome")) else parent_slo["name"]
                    outcome_lines = _slo_outcome_lines(raw_text, is_kiswahili)
                    if not outcome_lines:
                        # Nothing survived cleaning (a genuinely blank or
                        # pure-preamble record) — fall back to whatever raw
                        # text existed rather than silently emitting an
                        # empty cell, and let the downstream prefix logic
                        # handle it as before.
                        slo_text = raw_text
                        slo_text_pre_formatted = False
                    else:
                        bullets = [f"- {line}" for line in outcome_lines]
                        if is_kiswahili:
                            slo_text = "Kufikia mwisho wa somo, mwanafunzi aweze:\n" + "\n".join(bullets)
                        else:
                            slo_text = "By the end of the lesson the learner should be able to:\n" + "\n".join(bullets)
                        slo_text_pre_formatted = True

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

                # When combining all SLOs into one row, also union the
                # competency / value / PCI mappings of the *other* SLOs so
                # the row reflects the full coverage of the lesson.
                if combine_all_slos:
                    seen_c = {c.lower() for c in competencies if c}
                    seen_v = {v.lower() for v in values_list if v}
                    seen_p = {p.lower() for p in pcis if p}
                    for other in parent_slos:
                        if str(other["_id"]) == parent_slo_id:
                            continue
                        m = await db.slo_mappings.find_one({"sloId": str(other["_id"])})
                        if not m:
                            continue
                        for cid in m.get("competencyIds", []):
                            doc = await db.competencies.find_one({"_id": ObjectId(cid)})
                            if doc and doc["name"].lower() not in seen_c:
                                competencies.append(doc["name"]); seen_c.add(doc["name"].lower())
                        for vid in m.get("valueIds", []):
                            doc = await db.values.find_one({"_id": ObjectId(vid)})
                            if doc and doc["name"].lower() not in seen_v:
                                values_list.append(doc["name"]); seen_v.add(doc["name"].lower())
                        for pid in m.get("pciIds", []):
                            doc = await db.pcis.find_one({"_id": ObjectId(pid)})
                            if doc and doc["name"].lower() not in seen_p:
                                pcis.append(doc["name"]); seen_p.add(doc["name"].lower())

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
                    "sloPreFormatted": slo_text_pre_formatted,
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
                    # NEW: questions stored directly on the SLO doc itself
                    # (option C — every SLO under a substrand carries the full
                    # KIQ array for that substrand). This is the new authoritative
                    # source the scheme generator reads from. We sanitise the
                    # list here so any historical fragments ("Je", "Kwa nini")
                    # that slipped through the AI extractor never make it into
                    # the rendered scheme — the cell stays blank instead.
                    #
                    # Single-lesson + multi-SLO substrand: union the KIQs
                    # across every SLO in the substrand so the row reflects
                    # the full scope of the merged outcomes.
                    "_sloInquiries": (
                        clean_kiq_list([
                            q
                            for s in parent_slos
                            for q in (s.get("key_inquiry_questions") or [])
                        ])
                        if combine_all_slos
                        else clean_kiq_list(parent_slo.get("key_inquiry_questions"))
                    ),
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

        # ---- Pass 1: build the ordered grid of slots (breaks + content) ----
        # This mirrors the exact week/lesson/double/break detection that
        # existed before compression was introduced — nothing about how
        # breaks or double-lesson positions are found has changed. We split
        # "figure out the grid" from "fill the grid with content" into two
        # passes so real capacity (in rows, and in content-items once
        # doubles are accounted for) is known before deciding whether
        # compression is needed.
        grid_slots = []  # each: {week, lesson_display, is_double, is_break, break_type}
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
                    grid_slots.append({
                        "week": week,
                        "lesson_display": lesson_display,
                        "is_double": is_double,
                        "is_break": True,
                        "break_type": breaks_map.get(break_key) or breaks_map.get(break_key2),
                    })
                    lesson_num += 2 if is_double else 1
                    continue

                grid_slots.append({
                    "week": week,
                    "lesson_display": lesson_display,
                    "is_double": is_double,
                    "is_break": False,
                    "break_type": None,
                })
                lesson_num += 2 if is_double else 1

        content_slots = [s for s in grid_slots if not s["is_break"]]
        if not content_slots:
            raise HTTPException(
                status_code=400,
                detail="No teaching lessons available in this term — check total weeks, "
                       "lessons per week, and the breaks you've selected.",
            )

        total_items = len(curriculum_content)
        # Capacity counts a double slot as worth 2 items, since a double
        # lesson merges two lessons' worth of content into one extended
        # session rather than stretching one lesson's content across the
        # extra time.
        capacity_items = sum(2 if s["is_double"] else 1 for s in content_slots)

        # A duplicate lesson (round-robin pacing repeating an SLO, or a
        # genuine duplicate curriculum record) is shown as itself, twice,
        # with its real content — never collapsed and replaced with a
        # generic Marudio placeholder. Marudio only ever fills time that
        # has no selected content at all (see the deficit calculation in
        # MODE A below); it never stands in for content that does exist,
        # duplicated or not.
        working_content = curriculum_content

        # ---- Pass 2: assign curriculum_content items to content_slots ----
        # item_groups[i] = the list of content items rendered as row i.
        # len(item_groups) always equals len(content_slots).
        item_groups: List[List[Dict[str, Any]]] = []

        if total_items <= capacity_items:
            # MODE A — fits without compression (possibly only after
            # dropping duplicates above). Each single slot takes one item;
            # each double slot takes two (a genuine merge of two lessons'
            # content, not just a wider label on one lesson's content). If
            # content is SHORTER than capacity, the leftover time is filled
            # with revision/consolidation rows rather than repeating
            # earlier lessons verbatim or leaving trailing weeks blank —
            # spread out (inserted right after each strand finishes) rather
            # than dumped in one block at the end, since that's closer to
            # how revision actually gets used in a classroom.
            deficit = capacity_items - total_items

            # Group working_content into contiguous runs sharing the same
            # strand. Carry-over topics are scheduled as their own block
            # ahead of the term's own content (see the ordering above), so a
            # strand that has both carry-over and this-term substrands can
            # legitimately appear as two separate segments here — that's
            # correct, not a bug: each run gets its own revision top-up when
            # it finishes.
            segments: List[List[Dict[str, Any]]] = []
            for c in working_content:
                if segments and segments[-1][0]["strand"] == c["strand"]:
                    segments[-1].append(c)
                else:
                    segments.append([c])

            augmented_items: List[Dict[str, Any]]
            if deficit <= 0 or not segments:
                augmented_items = list(working_content)
            else:
                # Largest-remainder apportionment of `deficit` revision slots
                # across segments, weighted by each segment's own size, so a
                # substantial strand gets proportionally more revision time
                # than a one-lesson strand rather than an equal split.
                quotas = [deficit * len(seg) / total_items for seg in segments]
                floors = [int(q) for q in quotas]
                remaining = deficit - sum(floors)
                remainder_order = sorted(
                    range(len(segments)),
                    key=lambda i: quotas[i] - floors[i],
                    reverse=True,
                )
                revision_counts = list(floors)
                for i in remainder_order[:remaining]:
                    revision_counts[i] += 1

                augmented_items = []
                for seg, rev_count in zip(segments, revision_counts):
                    augmented_items.extend(seg)
                    strand_name = seg[0]["strand"]
                    for _ in range(rev_count):
                        augmented_items.append(_build_revision_content(strand_name, is_kiswahili))

            # augmented_items now has exactly capacity_items entries (real
            # content plus however many revision rows were apportioned), so
            # a straightforward single/double walk exhausts it exactly —
            # no wraparound or stop-early branch needed any more.
            content_index = 0
            for slot in content_slots:
                want = 2 if slot["is_double"] else 1
                group = augmented_items[content_index: content_index + want]
                content_index += len(group)
                item_groups.append(group)
        else:
            # MODE B — compression. More content than the term can hold
            # even after dropping duplicates and with doubles merging two
            # lessons each. Nothing gets dropped from here on: the
            # single/double distinction is set aside for grouping purposes
            # and the full (deduped) content list is split evenly,
            # largest-remainder first, across the actual number of rows
            # available (content_slots) so the term fills exactly with no
            # row left empty and no item left unscheduled.
            n_slots = len(content_slots)
            base, remainder = divmod(total_items, n_slots)
            idx = 0
            for i in range(n_slots):
                size = base + (1 if i < remainder else 0)
                item_groups.append(working_content[idx: idx + size])
                idx += size

        # ---- Assemble the final lessons list: breaks in their original
        # grid position, content rows built (and merged, where a row holds
        # more than one item) from item_groups ----
        lessons = []
        content_slot_idx = 0
        for slot in grid_slots:
            if slot["is_break"]:
                lessons.append({
                    "week": slot["week"],
                    "lesson": slot["lesson_display"],
                    "isBreak": True,
                    "isDouble": slot["is_double"],
                    "breakType": slot["break_type"],
                })
                continue

            items = item_groups[content_slot_idx]
            content_slot_idx += 1
            if not items:
                continue

            fields = _merge_lesson_items(items, is_kiswahili)
            lessons.append({
                "week": slot["week"],
                "lesson": slot["lesson_display"],
                "isDouble": slot["is_double"],
                **fields,
            })

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
            "carryOverTopics": request.carryOverTopics,
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
            "carryOverTopics": request.carryOverTopics,
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
