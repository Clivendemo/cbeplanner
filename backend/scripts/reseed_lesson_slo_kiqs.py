"""
One-shot migration: rewrite lesson_slos.keyInquiryQuestions from the parent
SLO row's `slos.key_inquiry_questions` array.

Background
----------
Up to this point, every auto-generated `lesson_slos` row carried a KIQ that
was synthesised algorithmically from its `outcome` text (e.g. "What do we
understand about identify common shapes…?"). We've removed that algorithm —
KIQs now come exclusively from the curriculum extractor, which writes them
to `slos.key_inquiry_questions[]`.

This script back-fills existing rows so the DB matches the new contract.

Rules
-----
- Rows where `isDraft == False` are admin-edited and are NEVER touched.
- Rows whose parent SLO has no extracted KIQs receive `keyInquiryQuestions: []`
  (blank — the curriculum editor will let admins backfill these).
- Idempotent: running the script multiple times produces the same result.

Usage
-----
    cd /app/backend && python -m scripts.reseed_lesson_slo_kiqs
"""

import asyncio
import os
from typing import Any, Dict, List

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


async def reseed_lesson_slo_kiqs(db) -> Dict[str, int]:
    stats = {
        "scanned": 0,
        "updated": 0,
        "blanked": 0,
        "skipped_admin_edited": 0,
        "skipped_no_parent": 0,
    }

    # Pre-load every SLO's key_inquiry_questions into memory keyed by str(_id).
    # Curriculum extractor stores the array verbatim; we copy it as-is.
    slo_kiq_by_id: Dict[str, List[str]] = {}
    async for slo in db.slos.find({}, {"key_inquiry_questions": 1}):
        kiqs = slo.get("key_inquiry_questions") or []
        slo_kiq_by_id[str(slo["_id"])] = list(kiqs)

    cursor = db.lesson_slos.find({})
    async for row in cursor:
        stats["scanned"] += 1

        # Never overwrite admin-edited rows.
        if row.get("isDraft") is False:
            stats["skipped_admin_edited"] += 1
            continue

        parent_id = row.get("parentSloId")
        if not parent_id:
            stats["skipped_no_parent"] += 1
            continue

        new_kiqs = slo_kiq_by_id.get(str(parent_id), [])
        current_kiqs = row.get("keyInquiryQuestions") or []

        # Skip when nothing would change (idempotent).
        if list(current_kiqs) == list(new_kiqs):
            continue

        await db.lesson_slos.update_one(
            {"_id": row["_id"]},
            {"$set": {"keyInquiryQuestions": new_kiqs}},
        )
        stats["updated"] += 1
        if not new_kiqs:
            stats["blanked"] += 1

    return stats


async def main():
    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ["DB_NAME"]
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    try:
        stats = await reseed_lesson_slo_kiqs(db)
    finally:
        client.close()

    print("Lesson SLO KIQ re-seed complete:")
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    asyncio.run(main())
