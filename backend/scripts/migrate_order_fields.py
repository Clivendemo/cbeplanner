#!/usr/bin/env python3
"""
One-time migration script to add order fields to strands, substrands, and SLOs.
Run this manually: python scripts/migrate_order_fields.py
"""

import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "cbe_lesson_planner")

async def migrate():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("Starting order field migration...")
    
    # Migrate strands
    print("Migrating strands...")
    subjects = await db.subjects.find().to_list(None)
    strand_count = 0
    for subject in subjects:
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(None)
        for idx, strand in enumerate(strands):
            if "order" not in strand:
                await db.strands.update_one(
                    {"_id": strand["_id"]},
                    {"$set": {"order": idx}}
                )
                strand_count += 1
    print(f"  Updated {strand_count} strands")
    
    # Migrate substrands
    print("Migrating substrands...")
    strands = await db.strands.find().to_list(None)
    substrand_count = 0
    for strand in strands:
        strand_id = str(strand["_id"])
        substrands = await db.substrands.find({"strandId": strand_id}).to_list(None)
        for idx, substrand in enumerate(substrands):
            if "order" not in substrand:
                await db.substrands.update_one(
                    {"_id": substrand["_id"]},
                    {"$set": {"order": idx}}
                )
                substrand_count += 1
    print(f"  Updated {substrand_count} substrands")
    
    # Migrate SLOs
    print("Migrating SLOs...")
    substrands = await db.substrands.find().to_list(None)
    slo_count = 0
    for substrand in substrands:
        substrand_id = str(substrand["_id"])
        slos = await db.slos.find({"substrandId": substrand_id}).to_list(None)
        for idx, slo in enumerate(slos):
            if "order" not in slo:
                await db.slos.update_one(
                    {"_id": slo["_id"]},
                    {"$set": {"order": idx}}
                )
                slo_count += 1
    print(f"  Updated {slo_count} SLOs")
    
    print("Migration completed!")
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate())
