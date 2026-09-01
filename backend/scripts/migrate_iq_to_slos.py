"""
One-off migration: move Key Inquiry Questions from per-substrand storage
(`learning_activities.inquiry_questions[]`) onto each per-lesson SLO
(`slos.key_inquiry_questions[]`).

Distribution rule (Option C, agreed with the user):
    Every SLO under a substrand inherits the FULL list of substrand-level
    inquiry_questions. The scheme generator picks element 0; the admin can
    later edit any specific SLO's array via the Lesson SLOs UI.

Idempotent — SLOs that already have a non-empty key_inquiry_questions array
are skipped (run as many times as you like).

Usage:
    cd /app/backend && python scripts/migrate_iq_to_slos.py            # dry-run
    cd /app/backend && python scripts/migrate_iq_to_slos.py --apply    # commit
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Make /app/backend importable when invoked from anywhere
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from motor.motor_asyncio import AsyncIOMotorClient


async def migrate(apply: bool) -> dict:
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    # Build a substrandId → inquiry_questions[] lookup
    la_cursor = db.learning_activities.find(
        {"inquiry_questions": {"$exists": True, "$ne": []}},
        {"_id": 0, "substrandId": 1, "inquiry_questions": 1},
    )
    iq_by_ss: dict[str, list[str]] = {}
    async for la in la_cursor:
        ss_id = la.get("substrandId")
        # substrandId may be ObjectId or string in legacy rows — normalise to str
        key = str(ss_id) if ss_id else None
        iqs = [q for q in (la.get("inquiry_questions") or []) if isinstance(q, str) and q.strip()]
        if key and iqs:
            iq_by_ss[key] = iqs

    # Walk every SLO; copy the full array onto any SLO whose field is empty.
    total_slos = 0
    will_update = 0
    skipped_already = 0
    skipped_no_source = 0

    cursor = db.slos.find({}, {"_id": 1, "substrandId": 1, "key_inquiry_questions": 1})
    pending_writes = []  # bulk
    async for slo in cursor:
        total_slos += 1
        existing = slo.get("key_inquiry_questions") or []
        if existing:
            skipped_already += 1
            continue
        ss_id = str(slo.get("substrandId") or "")
        iqs = iq_by_ss.get(ss_id) or []
        if not iqs:
            skipped_no_source += 1
            continue
        will_update += 1
        if apply:
            pending_writes.append((slo["_id"], iqs))
            if len(pending_writes) >= 200:
                await _flush(db, pending_writes)
                pending_writes.clear()

    if apply and pending_writes:
        await _flush(db, pending_writes)

    return {
        "total_slos": total_slos,
        "would_update": will_update,
        "skipped_already_has_iq": skipped_already,
        "skipped_no_source_iq_for_substrand": skipped_no_source,
        "applied": apply,
    }


async def _flush(db, batch: list[tuple]) -> None:
    """Bulk-update a batch of (slo_id, iqs) pairs."""
    from pymongo import UpdateOne
    ops = [
        UpdateOne({"_id": _id}, {"$set": {"key_inquiry_questions": iqs}})
        for _id, iqs in batch
    ]
    if ops:
        await db.slos.bulk_write(ops, ordered=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Actually write changes (default is dry-run)")
    args = parser.parse_args()

    summary = asyncio.run(migrate(apply=args.apply))
    print("\n=== migrate_iq_to_slos.py ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    if not args.apply:
        print("\n[dry-run] Re-run with --apply to commit the writes shown above.")


if __name__ == "__main__":
    main()
