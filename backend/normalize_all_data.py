#!/usr/bin/env python3
"""
Database Normalization Script
=============================
This script:
1. Removes duplicate strands (keeping the one with more complete data)
2. Normalizes all foreign key references to use ObjectId
3. Ensures data consistency across all curriculum collections
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
db_name = os.environ.get('DB_NAME', 'cbeplanner')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


async def remove_duplicate_strands():
    """Remove duplicate strands, keeping the one with the most substrands."""
    print("\n=== REMOVING DUPLICATE STRANDS ===")
    
    # Get all subjects
    subjects = await db.subjects.find().to_list(1000)
    
    total_removed = 0
    
    for subject in subjects:
        subject_id = subject['_id']
        subject_id_str = str(subject_id)
        
        # Get strands for this subject (both ObjectId and string)
        strands_oid = await db.strands.find({"subjectId": subject_id}).to_list(100)
        strands_str = await db.strands.find({"subjectId": subject_id_str}).to_list(100)
        
        all_strands = strands_oid + strands_str
        
        # Group strands by name
        strands_by_name = {}
        for strand in all_strands:
            name = strand.get("name", "").strip()
            if name not in strands_by_name:
                strands_by_name[name] = []
            strands_by_name[name].append(strand)
        
        # For each group with duplicates, keep the one with more substrands
        for name, strand_list in strands_by_name.items():
            if len(strand_list) > 1:
                # Count substrands for each
                best_strand = None
                best_count = -1
                
                for strand in strand_list:
                    strand_id = strand['_id']
                    # Count substrands (check both ObjectId and string)
                    count_oid = await db.substrands.count_documents({"strandId": strand_id})
                    count_str = await db.substrands.count_documents({"strandId": str(strand_id)})
                    total_count = count_oid + count_str
                    
                    if total_count > best_count:
                        best_count = total_count
                        best_strand = strand
                
                # Delete all but the best strand
                for strand in strand_list:
                    if strand['_id'] != best_strand['_id']:
                        strand_id = strand['_id']
                        
                        # Delete associated substrands
                        substrands = await db.substrands.find({"$or": [
                            {"strandId": strand_id},
                            {"strandId": str(strand_id)}
                        ]}).to_list(1000)
                        
                        for substrand in substrands:
                            sub_id = substrand['_id']
                            # Delete SLOs
                            slos = await db.slos.find({"$or": [
                                {"substrandId": sub_id},
                                {"substrandId": str(sub_id)}
                            ]}).to_list(1000)
                            
                            for slo in slos:
                                # Delete learning activities
                                await db.learning_activities.delete_many({"$or": [
                                    {"sloId": slo['_id']},
                                    {"sloId": str(slo['_id'])}
                                ]})
                            
                            await db.slos.delete_many({"$or": [
                                {"substrandId": sub_id},
                                {"substrandId": str(sub_id)}
                            ]})
                        
                        await db.substrands.delete_many({"$or": [
                            {"strandId": strand_id},
                            {"strandId": str(strand_id)}
                        ]})
                        
                        await db.strands.delete_one({"_id": strand_id})
                        total_removed += 1
                        print(f"  Removed duplicate strand: {name} from {subject['name']}")
    
    print(f"\nTotal duplicate strands removed: {total_removed}")
    return total_removed


async def normalize_foreign_keys():
    """Convert all string foreign keys to ObjectId."""
    print("\n=== NORMALIZING FOREIGN KEYS ===")
    
    # Normalize strands.subjectId
    strands = await db.strands.find({"subjectId": {"$type": "string"}}).to_list(10000)
    print(f"Found {len(strands)} strands with string subjectId")
    for strand in strands:
        try:
            new_id = ObjectId(strand['subjectId'])
            await db.strands.update_one(
                {"_id": strand['_id']},
                {"$set": {"subjectId": new_id}}
            )
        except:
            pass
    
    # Normalize substrands.strandId
    substrands = await db.substrands.find({"strandId": {"$type": "string"}}).to_list(10000)
    print(f"Found {len(substrands)} substrands with string strandId")
    for substrand in substrands:
        try:
            new_id = ObjectId(substrand['strandId'])
            await db.substrands.update_one(
                {"_id": substrand['_id']},
                {"$set": {"strandId": new_id}}
            )
        except:
            pass
    
    # Normalize slos.substrandId
    slos = await db.slos.find({"substrandId": {"$type": "string"}}).to_list(10000)
    print(f"Found {len(slos)} SLOs with string substrandId")
    for slo in slos:
        try:
            new_id = ObjectId(slo['substrandId'])
            await db.slos.update_one(
                {"_id": slo['_id']},
                {"$set": {"substrandId": new_id}}
            )
        except:
            pass
    
    # Normalize learning_activities.sloId
    activities = await db.learning_activities.find({"sloId": {"$type": "string"}}).to_list(10000)
    print(f"Found {len(activities)} learning activities with string sloId")
    for activity in activities:
        try:
            new_id = ObjectId(activity['sloId'])
            await db.learning_activities.update_one(
                {"_id": activity['_id']},
                {"$set": {"sloId": new_id}}
            )
        except:
            pass
    
    # Normalize learning_activities.substrandId if present
    activities = await db.learning_activities.find({"substrandId": {"$type": "string"}}).to_list(10000)
    print(f"Found {len(activities)} learning activities with string substrandId")
    for activity in activities:
        try:
            new_id = ObjectId(activity['substrandId'])
            await db.learning_activities.update_one(
                {"_id": activity['_id']},
                {"$set": {"substrandId": new_id}}
            )
        except:
            pass
    
    print("Foreign key normalization complete!")


async def verify_data_integrity():
    """Verify that all data is properly linked."""
    print("\n=== DATA INTEGRITY CHECK ===")
    
    # Check strands
    strands = await db.strands.find().to_list(10000)
    orphan_strands = 0
    for strand in strands:
        subject_id = strand.get('subjectId')
        if isinstance(subject_id, str):
            try:
                subject_id = ObjectId(subject_id)
            except:
                pass
        subject = await db.subjects.find_one({"_id": subject_id})
        if not subject:
            orphan_strands += 1
    print(f"Orphan strands (no matching subject): {orphan_strands}")
    
    # Check substrands
    substrands = await db.substrands.find().to_list(10000)
    orphan_substrands = 0
    for substrand in substrands:
        strand_id = substrand.get('strandId')
        if isinstance(strand_id, str):
            try:
                strand_id = ObjectId(strand_id)
            except:
                pass
        strand = await db.strands.find_one({"_id": strand_id})
        if not strand:
            orphan_substrands += 1
    print(f"Orphan substrands (no matching strand): {orphan_substrands}")
    
    # Summary
    total_strands = await db.strands.count_documents({})
    total_substrands = await db.substrands.count_documents({})
    total_slos = await db.slos.count_documents({})
    total_activities = await db.learning_activities.count_documents({})
    
    print(f"\nFinal counts:")
    print(f"  Strands: {total_strands}")
    print(f"  Substrands: {total_substrands}")
    print(f"  SLOs: {total_slos}")
    print(f"  Learning Activities: {total_activities}")


async def main():
    print("="*70)
    print("DATABASE NORMALIZATION AND CLEANUP")
    print("="*70)
    
    # Step 1: Remove duplicates
    await remove_duplicate_strands()
    
    # Step 2: Normalize foreign keys
    await normalize_foreign_keys()
    
    # Step 3: Verify integrity
    await verify_data_integrity()
    
    print("\n" + "="*70)
    print("NORMALIZATION COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
