"""
Calendar routes — admin-controlled Upcoming Events and Term Calendar.

Public (authenticated) endpoints for teachers:
- GET /api/calendar/events    — list events
- GET /api/calendar/terms     — list terms (with embedded activities)

Admin-only CRUD:
- POST   /api/admin/calendar/events             — create
- PUT    /api/admin/calendar/events/{id}        — update
- DELETE /api/admin/calendar/events/{id}        — delete
- POST   /api/admin/calendar/terms              — create
- PUT    /api/admin/calendar/terms/{id}         — update
- DELETE /api/admin/calendar/terms/{id}         — delete
- POST   /api/admin/calendar/seed               — one-shot seed with hardcoded defaults

Events are ISO-dated (YYYY-MM-DD) and tagged with a category that drives palette.
Clients derive display strings ("May 5", "Mon") from the ISO date.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

from app.deps import (
    api_router, db,
    verify_admin,
    serialize_doc, validate_object_id,
)

# ==================== CATEGORY PALETTE ====================

CATEGORY_PALETTE = {
    'academic':     {'bg': '#EEF2FF', 'tc': '#3730A3', 'dot': '#5B5BD6'},
    'cocurricular': {'bg': '#F0FDF4', 'tc': '#166534', 'dot': '#16A34A'},
    'exam':         {'bg': '#FFF7ED', 'tc': '#9A3412', 'dot': '#EA580C'},
}
VALID_CATEGORIES = set(CATEGORY_PALETTE.keys())
VALID_TERM_STATUSES = {'past', 'current', 'upcoming'}


def _palette_for(category: str) -> dict:
    return CATEGORY_PALETTE.get(category, CATEGORY_PALETTE['academic'])


# ==================== MODELS ====================

class CalendarEventIn(BaseModel):
    date: str = Field(..., description="ISO date YYYY-MM-DD")
    title: str
    category: str  # academic | cocurricular | exam
    order: int = 0


class CalendarEventOut(CalendarEventIn):
    id: str
    palette: dict


class TermActivity(BaseModel):
    label: str
    date: str  # display string e.g. "Feb 21–28" or "Jan 6"


class TermIn(BaseModel):
    name: str
    period: str
    status: str  # past | current | upcoming
    year: int
    academic: List[TermActivity] = []
    cocurricular: List[TermActivity] = []
    order: int = 0


class TermOut(TermIn):
    id: str
    palette: dict


# ==================== HELPERS ====================

def _event_out(doc) -> dict:
    d = serialize_doc(doc)
    d['palette'] = _palette_for(d.get('category', 'academic'))
    return d


def _term_out(doc) -> dict:
    d = serialize_doc(doc)
    status = d.get('status', 'upcoming')
    palette_key = {'past': 'academic', 'current': 'academic', 'upcoming': 'cocurricular'}
    # Give a per-status palette for the header
    status_palette = {
        'past':     {'headerBg': '#F3F4F6', 'headerText': '#9CA3AF', 'badgeBorder': '#E5E7EB'},
        'current':  {'headerBg': '#EEF2FF', 'headerText': '#3730A3', 'badgeBorder': '#C7D2FE'},
        'upcoming': {'headerBg': '#F0FDF4', 'headerText': '#166534', 'badgeBorder': '#BBF7D0'},
    }
    d['palette'] = status_palette.get(status, status_palette['upcoming'])
    return d


def _validate_event(payload: CalendarEventIn):
    # ISO date
    try:
        datetime.strptime(payload.date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="date must be in YYYY-MM-DD format")
    if payload.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"category must be one of: {', '.join(sorted(VALID_CATEGORIES))}"
        )
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is required")


def _validate_term(payload: TermIn):
    if payload.status not in VALID_TERM_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of: {', '.join(sorted(VALID_TERM_STATUSES))}"
        )
    if not payload.name.strip() or not payload.period.strip():
        raise HTTPException(status_code=400, detail="name and period are required")


# ==================== PUBLIC READS (unauthenticated) ====================
# Landing page + post-login widgets both consume these; keeping them public
# avoids double-fetch logic and lets anonymous visitors see the calendar.

@api_router.get("/calendar/events")
async def list_events():
    cursor = db.calendar_events.find({}, {'_id': 1, 'date': 1, 'title': 1, 'category': 1, 'order': 1})
    docs = await cursor.to_list(length=500)
    docs.sort(key=lambda d: (d.get('date', ''), d.get('order', 0)))
    return {"events": [_event_out(d) for d in docs]}


@api_router.get("/calendar/terms")
async def list_terms():
    cursor = db.term_calendars.find({})
    docs = await cursor.to_list(length=50)
    docs.sort(key=lambda d: (d.get('year', 0), d.get('order', 0)))
    return {"terms": [_term_out(d) for d in docs]}


# ==================== ADMIN CRUD — EVENTS ====================

@api_router.post("/admin/calendar/events")
async def create_event(payload: CalendarEventIn, admin: dict = Depends(verify_admin)):
    _validate_event(payload)
    doc = payload.dict()
    doc['createdAt'] = datetime.utcnow()
    doc['updatedAt'] = datetime.utcnow()
    res = await db.calendar_events.insert_one(doc)
    saved = await db.calendar_events.find_one({"_id": res.inserted_id})
    return _event_out(saved)


@api_router.put("/admin/calendar/events/{event_id}")
async def update_event(event_id: str, payload: CalendarEventIn, admin: dict = Depends(verify_admin)):
    _validate_event(payload)
    oid = validate_object_id(event_id, "event ID")
    update = payload.dict()
    update['updatedAt'] = datetime.utcnow()
    res = await db.calendar_events.update_one({"_id": oid}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    saved = await db.calendar_events.find_one({"_id": oid})
    return _event_out(saved)


@api_router.delete("/admin/calendar/events/{event_id}")
async def delete_event(event_id: str, admin: dict = Depends(verify_admin)):
    oid = validate_object_id(event_id, "event ID")
    res = await db.calendar_events.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"success": True}


# ==================== ADMIN CRUD — TERMS ====================

@api_router.post("/admin/calendar/terms")
async def create_term(payload: TermIn, admin: dict = Depends(verify_admin)):
    _validate_term(payload)
    doc = payload.dict()
    doc['createdAt'] = datetime.utcnow()
    doc['updatedAt'] = datetime.utcnow()
    res = await db.term_calendars.insert_one(doc)
    saved = await db.term_calendars.find_one({"_id": res.inserted_id})
    return _term_out(saved)


@api_router.put("/admin/calendar/terms/{term_id}")
async def update_term(term_id: str, payload: TermIn, admin: dict = Depends(verify_admin)):
    _validate_term(payload)
    oid = validate_object_id(term_id, "term ID")
    update = payload.dict()
    update['updatedAt'] = datetime.utcnow()
    res = await db.term_calendars.update_one({"_id": oid}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Term not found")
    saved = await db.term_calendars.find_one({"_id": oid})
    return _term_out(saved)


@api_router.delete("/admin/calendar/terms/{term_id}")
async def delete_term(term_id: str, admin: dict = Depends(verify_admin)):
    oid = validate_object_id(term_id, "term ID")
    res = await db.term_calendars.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Term not found")
    return {"success": True}


# ==================== SEED (idempotent) ====================

_SEED_EVENTS = [
    # year, iso date, title, category, order
    (2026, '2026-05-05', 'Term 2 Opens',              'academic',     1),
    (2026, '2026-05-12', 'Mid-Term CATs Begin',       'academic',     2),
    (2026, '2026-05-16', 'Inter-School Athletics',    'cocurricular', 3),
    (2026, '2026-05-23', 'Drama Festival — Zonal',    'cocurricular', 4),
    (2026, '2026-05-30', 'Mid-Term Break Starts',     'academic',     5),
    (2026, '2026-06-06', 'Schools Reopen',            'academic',     6),
    (2026, '2026-07-04', 'Term 2 Exams Start',        'exam',         7),
    (2026, '2026-08-01', 'Term 2 Closes',             'exam',         8),
    (2026, '2026-08-08', 'Music Festival — County',   'cocurricular', 9),
]

_SEED_TERMS = [
    {
        'name': 'Term 1', 'period': 'Jan 6 – Apr 4', 'status': 'past', 'year': 2026, 'order': 1,
        'academic': [
            {'label': 'Schools open', 'date': 'Jan 6'},
            {'label': 'Mid-term break', 'date': 'Feb 21–28'},
            {'label': 'End-term exams', 'date': 'Mar 24–28'},
            {'label': 'Schools close', 'date': 'Apr 4'},
        ],
        'cocurricular': [
            {'label': 'Debating — Zonal', 'date': 'Feb 14'},
            {'label': 'Athletics — Sub-county', 'date': 'Mar 7'},
            {'label': 'Music Festival — Zonal', 'date': 'Mar 21'},
        ],
    },
    {
        'name': 'Term 2', 'period': 'Apr 29 – Aug 1', 'status': 'current', 'year': 2026, 'order': 2,
        'academic': [
            {'label': 'Schools open', 'date': 'Apr 29'},
            {'label': 'Mid-term CATs', 'date': 'May 12–16'},
            {'label': 'Mid-term break', 'date': 'May 30–Jun 6'},
            {'label': 'End-term exams', 'date': 'Jul 21–25'},
            {'label': 'Schools close', 'date': 'Aug 1'},
        ],
        'cocurricular': [
            {'label': 'Athletics — County', 'date': 'May 16'},
            {'label': 'Drama — Zonal', 'date': 'May 23'},
            {'label': 'Games — Sub-county', 'date': 'Jun 20'},
            {'label': 'Music — County', 'date': 'Aug 8'},
        ],
    },
    {
        'name': 'Term 3', 'period': 'Aug 26 – Oct 31', 'status': 'upcoming', 'year': 2026, 'order': 3,
        'academic': [
            {'label': 'Schools open', 'date': 'Aug 26'},
            {'label': 'Mid-term break', 'date': 'Sep 26–Oct 3'},
            {'label': 'End-term exams', 'date': 'Oct 20–24'},
            {'label': 'Schools close', 'date': 'Oct 31'},
        ],
        'cocurricular': [
            {'label': 'Drama — National', 'date': 'Sep 5'},
            {'label': 'Athletics — National', 'date': 'Sep 19'},
            {'label': 'Music — National', 'date': 'Oct 10'},
            {'label': 'Science Congress', 'date': 'Oct 17'},
        ],
    },
]


async def seed_calendar_if_empty():
    """Called on startup — inserts defaults only if collections are empty."""
    ev_count = await db.calendar_events.count_documents({})
    if ev_count == 0:
        now = datetime.utcnow()
        docs = [{
            'date': iso, 'title': title, 'category': cat, 'order': order,
            'year': year, 'createdAt': now, 'updatedAt': now,
        } for year, iso, title, cat, order in _SEED_EVENTS]
        await db.calendar_events.insert_many(docs)

    term_count = await db.term_calendars.count_documents({})
    if term_count == 0:
        now = datetime.utcnow()
        docs = [{**t, 'createdAt': now, 'updatedAt': now} for t in _SEED_TERMS]
        await db.term_calendars.insert_many(docs)


@api_router.post("/admin/calendar/seed")
async def admin_seed(admin: dict = Depends(verify_admin)):
    """Force-seed defaults. Only inserts if the relevant collection is empty."""
    await seed_calendar_if_empty()
    ev = await db.calendar_events.count_documents({})
    tm = await db.term_calendars.count_documents({})
    return {"success": True, "events": ev, "terms": tm}
