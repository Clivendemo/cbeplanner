"""
News announcements routes — admin-controlled content for the marquee news strip.

- GET  /api/news                    — public; used by the NewsStrip
- POST /api/admin/news              — admin create
- PUT  /api/admin/news/{id}         — admin update
- DELETE /api/admin/news/{id}       — admin delete

Announcements let admins push non-event messages (policy changes, feature releases,
CBC reform updates) to the top-of-page strip without polluting the calendar.
"""
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

from app.deps import (
    api_router, db,
    verify_admin,
    serialize_doc, validate_object_id,
)


class NewsIn(BaseModel):
    tag: str = Field(..., description="Short label e.g. 'MoE', 'KNEC', 'Update'")
    text: str = Field(..., description="Announcement body shown on the marquee")
    active: bool = True
    order: int = 0


# ==================== PUBLIC ====================

@api_router.get("/news")
async def list_news():
    cursor = db.news_announcements.find({'active': True})
    docs = await cursor.to_list(length=50)
    docs.sort(key=lambda d: (d.get('order', 0), d.get('_id')))
    return {"news": [serialize_doc(d) for d in docs]}


# ==================== ADMIN ====================

@api_router.get("/admin/news")
async def admin_list_news(admin: dict = Depends(verify_admin)):
    """Admin list — includes inactive items so admins can toggle them."""
    cursor = db.news_announcements.find({})
    docs = await cursor.to_list(length=200)
    docs.sort(key=lambda d: (d.get('order', 0), d.get('_id')))
    return {"news": [serialize_doc(d) for d in docs]}


def _validate_news(payload: NewsIn):
    if not payload.tag.strip():
        raise HTTPException(status_code=400, detail="tag is required")
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="text is required")


@api_router.post("/admin/news")
async def create_news(payload: NewsIn, admin: dict = Depends(verify_admin)):
    _validate_news(payload)
    doc = payload.dict()
    doc['createdAt'] = datetime.utcnow()
    doc['updatedAt'] = datetime.utcnow()
    res = await db.news_announcements.insert_one(doc)
    saved = await db.news_announcements.find_one({"_id": res.inserted_id})
    return serialize_doc(saved)


@api_router.put("/admin/news/{news_id}")
async def update_news(news_id: str, payload: NewsIn, admin: dict = Depends(verify_admin)):
    _validate_news(payload)
    oid = validate_object_id(news_id, "news ID")
    update = payload.dict()
    update['updatedAt'] = datetime.utcnow()
    res = await db.news_announcements.update_one({"_id": oid}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="News item not found")
    saved = await db.news_announcements.find_one({"_id": oid})
    return serialize_doc(saved)


@api_router.delete("/admin/news/{news_id}")
async def delete_news(news_id: str, admin: dict = Depends(verify_admin)):
    oid = validate_object_id(news_id, "news ID")
    res = await db.news_announcements.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="News item not found")
    return {"success": True}
