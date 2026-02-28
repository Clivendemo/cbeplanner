#!/usr/bin/env python3
"""
Seed SLO mappings for the 5 new subjects.
Links each SLO to appropriate core competencies, core values, and PCIs.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('.env')

mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Mapping of subject to relevant competencies, values, and PCIs
SUBJECT_MAPPINGS = {
    "Business Studies": {
        "competencies": [
            "Critical Thinking and Problem Solving",
            "Communication and Collaboration",
            "Creativity and Imagination",
            "Digital Literacy"
        ],
        "values": [
            "Integrity",
            "Responsibility",
            "Respect",
            "Social Justice"
        ],
        "pcis": [
            "Financial Literacy",
            "Citizenship",
            "Life Skills",
            "Digital Citizenship"
        ]
    },
    "Christian Religious Education": {
        "competencies": [
            "Communication and Collaboration",
            "Critical Thinking and Problem Solving",
            "Self-Efficacy",
            "Citizenship"
        ],
        "values": [
            "Love",
            "Peace",
            "Respect",
            "Integrity",
            "Unity",
            "Social Justice"
        ],
        "pcis": [
            "Citizenship",
            "Life Skills",
            "Social Cohesion",
            "Citizenship Education"
        ]
    },
    "Electrical Technology": {
        "competencies": [
            "Critical Thinking and Problem Solving",
            "Creativity and Imagination",
            "Digital Literacy",
            "Learning to Learn"
        ],
        "values": [
            "Responsibility",
            "Integrity",
            "Respect"
        ],
        "pcis": [
            "Safety and Security",
            "Environmental Conservation",
            "Life Skills",
            "Education for Sustainable Development"
        ]
    },
    "Fine Arts": {
        "competencies": [
            "Creativity and Imagination",
            "Communication and Collaboration",
            "Self-Efficacy",
            "Learning to Learn"
        ],
        "values": [
            "Respect",
            "Love",
            "Unity",
            "Patriotism"
        ],
        "pcis": [
            "Life Skills",
            "Environmental Conservation",
            "Citizenship Education",
            "Social Cohesion"
        ]
    },
    "French": {
        "competencies": [
            "Communication and Collaboration",
            "Critical Thinking and Problem Solving",
            "Learning to Learn",
            "Digital Literacy"
        ],
        "values": [
            "Respect",
            "Unity",
            "Peace",
            "Love"
        ],
        "pcis": [
            "Life Skills",
            "Citizenship",
            "Social Cohesion",
            "Digital Citizenship"
        ]
    }
}


async def get_id_by_name(collection_name, name):
    """Get document ID by name"""
    doc = await db[collection_name].find_one({"name": name})
    if doc:
        return str(doc["_id"])
    return None


async def seed_slo_mappings():
    """Create SLO mappings for all new subjects"""
    print("=" * 70)
    print("SEEDING SLO MAPPINGS FOR NEW SUBJECTS")
    print("=" * 70)
    
    total_created = 0
    total_skipped = 0
    
    for subject_name, mapping_config in SUBJECT_MAPPINGS.items():
        print(f"\n--- Processing {subject_name} ---")
        
        # Get competency IDs
        competency_ids = []
        for comp_name in mapping_config["competencies"]:
            comp_id = await get_id_by_name("competencies", comp_name)
            if comp_id:
                competency_ids.append(comp_id)
        
        # Get value IDs
        value_ids = []
        for val_name in mapping_config["values"]:
            val_id = await get_id_by_name("values", val_name)
            if val_id:
                value_ids.append(val_id)
        
        # Get PCI IDs
        pci_ids = []
        for pci_name in mapping_config["pcis"]:
            pci_id = await get_id_by_name("pcis", pci_name)
            if pci_id:
                pci_ids.append(pci_id)
        
        print(f"  Found: {len(competency_ids)} competencies, {len(value_ids)} values, {len(pci_ids)} PCIs")
        
        # Get subject and its SLOs
        subject = await db.subjects.find_one({"name": subject_name})
        if not subject:
            print(f"  [ERROR] Subject not found: {subject_name}")
            continue
        
        subject_id = str(subject["_id"])
        strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
        
        subject_slo_count = 0
        subject_created = 0
        
        for strand in strands:
            substrands = await db.substrands.find({"strandId": str(strand["_id"])}).to_list(100)
            
            for substrand in substrands:
                slos = await db.slos.find({"substrandId": str(substrand["_id"])}).to_list(100)
                
                for slo in slos:
                    slo_id = str(slo["_id"])
                    subject_slo_count += 1
                    
                    # Check if mapping already exists
                    existing = await db.slo_mappings.find_one({"sloId": slo_id})
                    if existing:
                        total_skipped += 1
                        continue
                    
                    # Create mapping
                    mapping_doc = {
                        "sloId": slo_id,
                        "competencyIds": competency_ids,
                        "valueIds": value_ids,
                        "pciIds": pci_ids,
                        "assessmentIds": []
                    }
                    
                    await db.slo_mappings.insert_one(mapping_doc)
                    subject_created += 1
                    total_created += 1
        
        print(f"  Total SLOs: {subject_slo_count}")
        print(f"  Mappings created: {subject_created}")
    
    print("\n" + "=" * 70)
    print("SEEDING COMPLETE")
    print("=" * 70)
    print(f"Total mappings created: {total_created}")
    print(f"Total skipped (already existed): {total_skipped}")
    
    # Verify totals
    total_mappings = await db.slo_mappings.count_documents({})
    print(f"\nTotal SLO mappings in database: {total_mappings}")


if __name__ == "__main__":
    asyncio.run(seed_slo_mappings())
