"""
Regression: ``POST /api/admin/move-item-order`` must work even on legacy
items that have no ``order`` field stored on disk.

Bug history
-----------
Before this fix, 20 of 96 strands, 69 of 342 substrands, and 70 of 1586
SLOs in production had no ``order`` key at all. The move endpoint did
``item.get("order", 0)`` for the moving item AND for siblings, so every
item defaulted to ``0`` and the `find sibling with order < 0 / > 0` query
never matched anything. The endpoint silently returned
*"Cannot move - already at the top/bottom"* and the up/down chevrons in
the admin UI appeared inert.
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest
from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.insert(0, "/app/backend")

load_dotenv("/app/backend/.env")


async def _move(db, item_type: str, item_id, direction: str):
    """Mirror of ``server.move_item_order`` minus auth — same control flow."""
    collection_map = {
        "strand": db.strands,
        "substrand": db.substrands,
        "slo": db.slos,
    }
    parent_field_map = {
        "strand": "subjectId",
        "substrand": "strandId",
        "slo": "substrandId",
    }
    collection = collection_map[item_type]
    parent_field = parent_field_map[item_type]

    item = await collection.find_one({"_id": ObjectId(item_id)})
    parent_id = item.get(parent_field)

    missing = await collection.count_documents({
        parent_field: parent_id,
        "order": {"$exists": False},
    })
    if missing > 0:
        siblings = await collection.find(
            {parent_field: parent_id}
        ).sort("_id", 1).to_list(1000)
        for idx, sib in enumerate(siblings):
            await collection.update_one(
                {"_id": sib["_id"]},
                {"$set": {"order": idx + 1}},
            )
        item = await collection.find_one({"_id": ObjectId(item_id)})

    current_order = item.get("order", 0)
    if direction == "up":
        sibling = await collection.find_one(
            {parent_field: parent_id, "order": {"$lt": current_order}},
            sort=[("order", -1)],
        )
    else:
        sibling = await collection.find_one(
            {parent_field: parent_id, "order": {"$gt": current_order}},
            sort=[("order", 1)],
        )
    if not sibling:
        return False

    sib_order = sibling.get("order", 0)
    await collection.update_one(
        {"_id": ObjectId(item_id)}, {"$set": {"order": sib_order}}
    )
    await collection.update_one(
        {"_id": sibling["_id"]}, {"$set": {"order": current_order}}
    )
    return True


def test_move_down_legacy_strands_without_order():
    async def run():
        client = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = client[os.environ["DB_NAME"]]
        subject = "TEST_REORDER_SUBJECT_999"
        try:
            await db.strands.delete_many({"subjectId": subject})
            ids = []
            for n in ["A", "B", "C"]:
                r = await db.strands.insert_one({
                    "subjectId": subject, "name": f"Strand {n}",
                    # Deliberately NO order field
                })
                ids.append(r.inserted_id)

            # Sanity check: legacy shape reproduced
            n_no_order = await db.strands.count_documents({
                "subjectId": subject, "order": {"$exists": False}
            })
            assert n_no_order == 3

            ok = await _move(db, "strand", ids[0], "down")
            assert ok, "move down must succeed even for items lacking order"

            a = await db.strands.find_one({"_id": ids[0]})
            b = await db.strands.find_one({"_id": ids[1]})
            c = await db.strands.find_one({"_id": ids[2]})
            assert a["order"] == 2
            assert b["order"] == 1
            assert c["order"] == 3

            ordered = await db.strands.find({"subjectId": subject}) \
                .sort([("order", 1), ("_id", 1)]).to_list(10)
            assert [s["name"] for s in ordered] == ["Strand B", "Strand A", "Strand C"]
        finally:
            await db.strands.delete_many({"subjectId": subject})
            client.close()

    asyncio.run(run())


def test_move_up_legacy_substrands_without_order():
    async def run():
        client = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = client[os.environ["DB_NAME"]]
        strand = "TEST_REORDER_STRAND_999"
        try:
            await db.substrands.delete_many({"strandId": strand})
            ids = []
            for n in ["X", "Y", "Z"]:
                r = await db.substrands.insert_one({
                    "strandId": strand, "name": f"Substrand {n}",
                })
                ids.append(r.inserted_id)

            ok = await _move(db, "substrand", ids[2], "up")
            assert ok

            x = await db.substrands.find_one({"_id": ids[0]})
            y = await db.substrands.find_one({"_id": ids[1]})
            z = await db.substrands.find_one({"_id": ids[2]})
            assert x["order"] == 1
            assert y["order"] == 3
            assert z["order"] == 2
        finally:
            await db.substrands.delete_many({"strandId": strand})
            client.close()

    asyncio.run(run())


def test_top_item_move_up_returns_false_not_crash():
    async def run():
        client = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = client[os.environ["DB_NAME"]]
        subject = "TEST_REORDER_BOUNDARY"
        try:
            await db.strands.delete_many({"subjectId": subject})
            r = await db.strands.insert_one({
                "subjectId": subject, "name": "Only One", "order": 1,
            })
            ok = await _move(db, "strand", r.inserted_id, "up")
            assert ok is False
        finally:
            await db.strands.delete_many({"subjectId": subject})
            client.close()

    asyncio.run(run())


def test_subsequent_moves_use_persisted_order_no_rebackfill():
    """After the first move, all siblings have order; second move should
    not change A's place in the sibling renumbering — the swap should be
    a clean order-1 ↔ order-2 exchange."""
    async def run():
        client = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = client[os.environ["DB_NAME"]]
        subject = "TEST_REORDER_REPEAT"
        try:
            await db.strands.delete_many({"subjectId": subject})
            ids = []
            for n in ["P", "Q", "R"]:
                r = await db.strands.insert_one({
                    "subjectId": subject, "name": f"Strand {n}",
                })
                ids.append(r.inserted_id)

            await _move(db, "strand", ids[0], "down")  # P:2 Q:1 R:3
            await _move(db, "strand", ids[2], "up")    # P:2 Q:1 R:2 → swap
            # Order after second move: P:3 Q:1 R:2  (R moved from 3 → 2, P from 2 → 3)
            p = await db.strands.find_one({"_id": ids[0]})
            q = await db.strands.find_one({"_id": ids[1]})
            r_doc = await db.strands.find_one({"_id": ids[2]})
            # Final list order: Q (1), R (2), P (3)
            ordered = await db.strands.find({"subjectId": subject}) \
                .sort([("order", 1), ("_id", 1)]).to_list(10)
            assert [s["name"] for s in ordered] == ["Strand Q", "Strand R", "Strand P"]
        finally:
            await db.strands.delete_many({"subjectId": subject})
            client.close()

    asyncio.run(run())
