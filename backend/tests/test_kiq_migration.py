"""
Regression: the migration script `migrate_iq_to_slos.py` must move
`learning_activities.inquiry_questions[]` (substrand-level) onto every
`slos.key_inquiry_questions[]` (per-lesson) under that substrand, using
Option-C distribution (every SLO inherits the full array).
"""
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) \
        if asyncio.get_event_loop().is_running() else asyncio.run(coro)


def _setup_db_and_run(db_name: str, work_async):
    """Spin up an isolated test DB, hand it to `work_async`, then drop it."""
    from motor.motor_asyncio import AsyncIOMotorClient

    async def runner():
        client = AsyncIOMotorClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
        db = client[db_name]
        try:
            await work_async(db, db_name)
        finally:
            await client.drop_database(db_name)
    asyncio.run(runner())


def test_migration_distributes_full_array_to_every_slo(monkeypatch):
    """2 SLOs under a substrand whose learning_activities.inquiry_questions=[Q1, Q2].
    After migration: BOTH SLOs carry [Q1, Q2] verbatim."""
    async def work(db, db_name):
        ss_id = "test-substrand-id"
        await db.learning_activities.insert_one({
            "substrandId": ss_id,
            "inquiry_questions": ["Q1?", "Q2?"],
        })
        a = await db.slos.insert_one({"name": "A", "substrandId": ss_id})
        b = await db.slos.insert_one({"name": "B", "substrandId": ss_id})

        monkeypatch.setenv("MONGO_URL", os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
        monkeypatch.setenv("DB_NAME", db_name)
        sys.modules.pop("migrate_iq_to_slos", None)
        from migrate_iq_to_slos import migrate
        summary = await migrate(apply=True)

        assert summary["would_update"] == 2
        assert summary["skipped_already_has_iq"] == 0

        doc_a = await db.slos.find_one({"_id": a.inserted_id})
        doc_b = await db.slos.find_one({"_id": b.inserted_id})
        assert doc_a["key_inquiry_questions"] == ["Q1?", "Q2?"]
        assert doc_b["key_inquiry_questions"] == ["Q1?", "Q2?"]

    _setup_db_and_run("__test_kiq_migration", work)


def test_migration_is_idempotent(monkeypatch):
    async def work(db, db_name):
        ss_id = "ss-2"
        await db.learning_activities.insert_one({"substrandId": ss_id, "inquiry_questions": ["Q1?"]})
        await db.slos.insert_one({"name": "A", "substrandId": ss_id})

        monkeypatch.setenv("MONGO_URL", os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
        monkeypatch.setenv("DB_NAME", db_name)
        sys.modules.pop("migrate_iq_to_slos", None)
        from migrate_iq_to_slos import migrate

        first = await migrate(apply=True)
        second = await migrate(apply=True)
        assert first["would_update"] == 1
        assert second["would_update"] == 0
        assert second["skipped_already_has_iq"] == 1

    _setup_db_and_run("__test_kiq_migration_idem", work)


def test_migration_skips_slo_when_substrand_has_no_source(monkeypatch):
    """SLOs whose substrand never had inquiry_questions are skipped (no field
    is created, no error)."""
    async def work(db, db_name):
        ss_id = "ss-3"
        slo = await db.slos.insert_one({"name": "Lonely SLO", "substrandId": ss_id})

        monkeypatch.setenv("MONGO_URL", os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
        monkeypatch.setenv("DB_NAME", db_name)
        sys.modules.pop("migrate_iq_to_slos", None)
        from migrate_iq_to_slos import migrate

        summary = await migrate(apply=True)
        assert summary["would_update"] == 0
        assert summary["skipped_no_source_iq_for_substrand"] == 1

        doc = await db.slos.find_one({"_id": slo.inserted_id})
        assert "key_inquiry_questions" not in doc

    _setup_db_and_run("__test_kiq_migration_skip", work)
