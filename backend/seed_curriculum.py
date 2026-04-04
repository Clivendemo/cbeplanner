"""
Curriculum Database Seeding Script

This script imports curriculum data from extracted JSON files into the MongoDB database.
It creates grades, subjects, strands, sub-strands, SLOs, and learning activities.

Usage:
    python seed_curriculum.py [--file PATH] [--grade GRADE_NAME]
    
    By default, it will seed all available JSON files in the curriculum_data folder.
"""

import asyncio
import json
import os
import argparse
from datetime import datetime, timezone
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.getenv('MONGODB_URI') or os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.getenv('DB_NAME', 'cbeplanner-oregon')

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Statistics tracking
stats = {
    "grades_created": 0,
    "subjects_created": 0,
    "strands_created": 0,
    "substrands_created": 0,
    "slos_created": 0,
    "learning_activities_created": 0,
    "competencies_created": 0,
    "values_created": 0,
    "pcis_created": 0,
    "errors": []
}


async def get_or_create_grade(grade_name: str) -> str:
    """Get existing grade or create new one"""
    # Extract grade number for ordering
    grade_order = 0
    if "PP1" in grade_name:
        grade_order = -2
    elif "PP2" in grade_name:
        grade_order = -1
    else:
        import re
        match = re.search(r'(\d+)', grade_name)
        if match:
            grade_order = int(match.group(1))
    
    grade = await db.grades.find_one({"name": grade_name})
    if grade:
        return str(grade["_id"])
    
    result = await db.grades.insert_one({
        "name": grade_name,
        "order": grade_order
    })
    stats["grades_created"] += 1
    print(f"  Created grade: {grade_name}")
    return str(result.inserted_id)


async def get_or_create_subject(subject_name: str, grade_id: str) -> str:
    """Get existing subject or create new one, and link to grade"""
    subject = await db.subjects.find_one({"name": subject_name})
    
    if subject:
        # Add grade to gradeIds if not already there
        if grade_id not in subject.get("gradeIds", []):
            await db.subjects.update_one(
                {"_id": subject["_id"]},
                {"$addToSet": {"gradeIds": grade_id}}
            )
        return str(subject["_id"])
    
    result = await db.subjects.insert_one({
        "name": subject_name,
        "gradeIds": [grade_id]
    })
    stats["subjects_created"] += 1
    print(f"    Created subject: {subject_name}")
    return str(result.inserted_id)


async def get_or_create_strand(strand_name: str, subject_id: str, order: int = 0) -> str:
    """Get existing strand or create new one"""
    strand = await db.strands.find_one({
        "name": strand_name,
        "subjectId": subject_id
    })
    
    if strand:
        return str(strand["_id"])
    
    result = await db.strands.insert_one({
        "name": strand_name,
        "subjectId": subject_id,
        "order": order
    })
    stats["strands_created"] += 1
    return str(result.inserted_id)


async def get_or_create_substrand(substrand_name: str, strand_id: str, order: int = 0) -> str:
    """Get existing substrand or create new one"""
    substrand = await db.substrands.find_one({
        "name": substrand_name,
        "strandId": strand_id
    })
    
    if substrand:
        return str(substrand["_id"])
    
    result = await db.substrands.insert_one({
        "name": substrand_name,
        "strandId": strand_id,
        "order": order
    })
    stats["substrands_created"] += 1
    return str(result.inserted_id)


async def create_slo(slo_name: str, description: str, substrand_id: str, order: int = 0) -> str:
    """Create a new SLO"""
    # Clean up the SLO name
    slo_name = slo_name.strip()
    if slo_name.startswith(('a)', 'b)', 'c)', 'd)', 'e)', 'f)', 'g)', 'h)')):
        slo_name = slo_name[2:].strip()
    
    result = await db.slos.insert_one({
        "name": slo_name,
        "description": description or slo_name,
        "substrandId": substrand_id,
        "order": order
    })
    stats["slos_created"] += 1
    return str(result.inserted_id)


async def create_learning_activities(substrand_id: str, activities_data: dict) -> str:
    """Create or update learning activities for a substrand"""
    existing = await db.learning_activities.find_one({"substrandId": substrand_id})
    
    activity_doc = {
        "substrandId": substrand_id,
        "introduction_activities": activities_data.get("introduction_activities", []),
        "development_activities": activities_data.get("development_activities", []),
        "conclusion_activities": activities_data.get("conclusion_activities", []),
        "extended_activities": activities_data.get("extended_activities", []),
        "learning_resources": activities_data.get("learning_resources", []),
        "assessment_methods": activities_data.get("assessment_methods", []),
        "core_competencies": activities_data.get("core_competencies", []),
        "values": activities_data.get("values", []),
        "pci": activities_data.get("pcis", []),
        "inquiry_questions": activities_data.get("inquiry_questions", [])
    }
    
    if existing:
        await db.learning_activities.update_one(
            {"_id": existing["_id"]},
            {"$set": activity_doc}
        )
        return str(existing["_id"])
    
    result = await db.learning_activities.insert_one(activity_doc)
    stats["learning_activities_created"] += 1
    return str(result.inserted_id)


async def get_or_create_competency(name: str) -> str:
    """Get or create a competency"""
    comp = await db.competencies.find_one({"name": name})
    if comp:
        return str(comp["_id"])
    
    result = await db.competencies.insert_one({
        "name": name,
        "description": name
    })
    stats["competencies_created"] += 1
    return str(result.inserted_id)


async def get_or_create_value(name: str) -> str:
    """Get or create a value"""
    val = await db.values.find_one({"name": name})
    if val:
        return str(val["_id"])
    
    result = await db.values.insert_one({
        "name": name,
        "description": name
    })
    stats["values_created"] += 1
    return str(result.inserted_id)


async def get_or_create_pci(name: str) -> str:
    """Get or create a PCI"""
    pci = await db.pcis.find_one({"name": name})
    if pci:
        return str(pci["_id"])
    
    result = await db.pcis.insert_one({
        "name": name,
        "description": name
    })
    stats["pcis_created"] += 1
    return str(result.inserted_id)


async def seed_grade1_format(data: dict):
    """Seed curriculum data in Grade 1 format"""
    grade_name = data.get("grade", "Unknown Grade")
    print(f"\nSeeding {grade_name} data...")
    
    grade_id = await get_or_create_grade(grade_name)
    
    for subject_data in data.get("subjects", []):
        subject_name = subject_data.get("subject_name", "Unknown Subject")
        subject_id = await get_or_create_subject(subject_name, grade_id)
        
        strand_order = 0
        for strand_data in subject_data.get("strands", []):
            strand_name = strand_data.get("strand_name", "")
            if strand_data.get("strand_number"):
                strand_name = f"{strand_data['strand_number']} {strand_name}"
            
            strand_id = await get_or_create_strand(strand_name.strip(), subject_id, strand_order)
            strand_order += 1
            
            substrand_order = 0
            for substrand_data in strand_data.get("sub_strands", []):
                substrand_name = substrand_data.get("sub_strand_name", "")
                if substrand_data.get("sub_strand_number"):
                    substrand_name = f"{substrand_data['sub_strand_number']} {substrand_name}"
                
                substrand_id = await get_or_create_substrand(substrand_name.strip(), strand_id, substrand_order)
                substrand_order += 1
                
                # Create SLOs
                slo_order = 0
                for slo in substrand_data.get("specific_learning_outcomes", []):
                    await create_slo(slo, slo, substrand_id, slo_order)
                    slo_order += 1
                
                # Create learning activities
                activities_data = {
                    "development_activities": substrand_data.get("suggested_learning_experiences", []),
                    "core_competencies": substrand_data.get("core_competencies", []),
                    "values": substrand_data.get("values", []),
                    "pcis": substrand_data.get("pcis", []),
                    "inquiry_questions": substrand_data.get("key_inquiry_questions", [])
                }
                
                # Handle assessment
                assessment = substrand_data.get("suggested_assessment", {})
                if isinstance(assessment, dict):
                    activities_data["assessment_methods"] = assessment.get("methods", [])
                
                await create_learning_activities(substrand_id, activities_data)
                
                # Create reference data
                for comp in substrand_data.get("core_competencies", []):
                    await get_or_create_competency(comp)
                for val in substrand_data.get("values", []):
                    await get_or_create_value(val)
                for pci in substrand_data.get("pcis", []):
                    await get_or_create_pci(pci)


async def seed_grade10_format(data: dict):
    """Seed curriculum data in Grade 10 format"""
    print("\nSeeding Grade 10+ curriculum data...")
    
    for subject_data in data.get("subjects", []):
        subject_name = subject_data.get("subject_name", "Unknown Subject")
        grade_name = subject_data.get("grade", "Grade 10")
        
        grade_id = await get_or_create_grade(grade_name)
        subject_id = await get_or_create_subject(subject_name, grade_id)
        
        strand_order = 0
        for strand_data in subject_data.get("strands", []):
            strand_name = strand_data.get("strand_name", "Unknown Strand")
            strand_id = await get_or_create_strand(strand_name, subject_id, strand_order)
            strand_order += 1
            
            substrand_order = 0
            for substrand_data in strand_data.get("sub_strands", []):
                substrand_name = substrand_data.get("sub_strand_name", "Unknown Sub-strand")
                substrand_id = await get_or_create_substrand(substrand_name, strand_id, substrand_order)
                substrand_order += 1
                
                # Create SLOs
                slo_order = 0
                for slo in substrand_data.get("specific_learning_outcomes", []):
                    await create_slo(slo, slo, substrand_id, slo_order)
                    slo_order += 1
                
                # Create learning activities
                competency_mappings = substrand_data.get("competency_mappings", {})
                
                # Parse competencies from mapping text
                core_competencies = []
                values = []
                pcis = []
                
                if isinstance(competency_mappings, dict):
                    cc_text = competency_mappings.get("core_competencies", "")
                    if "Creativity" in cc_text:
                        core_competencies.append("Creativity and Imagination")
                    if "Critical thinking" in cc_text.lower():
                        core_competencies.append("Critical Thinking and Problem Solving")
                    if "Communication" in cc_text:
                        core_competencies.append("Communication and Collaboration")
                    if "Self-efficacy" in cc_text:
                        core_competencies.append("Self-efficacy")
                    if "Learning to learn" in cc_text.lower():
                        core_competencies.append("Learning to Learn")
                    if "Digital" in cc_text:
                        core_competencies.append("Digital Literacy")
                    if "Citizenship" in cc_text:
                        core_competencies.append("Citizenship")
                    
                    val_text = competency_mappings.get("values", "")
                    for v in ["Unity", "Responsibility", "Respect", "Love", "Peace", "Patriotism", "Integrity", "Social Justice"]:
                        if v in val_text:
                            values.append(v)
                    
                    pci_text = competency_mappings.get("pcis", "")
                    for p in ["Diversity", "Self-esteem", "Social awareness", "Life skills", "Citizenship", "Creative", "Safety", "Environmental"]:
                        if p.lower() in pci_text.lower():
                            pcis.append(p)
                
                activities_data = {
                    "development_activities": substrand_data.get("learning_activities", []),
                    "core_competencies": core_competencies,
                    "values": values,
                    "pcis": pcis,
                    "inquiry_questions": substrand_data.get("key_inquiry_questions", [])
                }
                
                await create_learning_activities(substrand_id, activities_data)
                
                # Create reference data
                for comp in core_competencies:
                    await get_or_create_competency(comp)
                for val in values:
                    await get_or_create_value(val)
                for pci in pcis:
                    await get_or_create_pci(pci)


async def seed_from_file(file_path: str):
    """Seed database from a JSON file"""
    print(f"\nReading {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Detect format and seed appropriately
    if "subjects" in data and isinstance(data.get("subjects"), list):
        if data["subjects"] and "strands" in data["subjects"][0]:
            first_strand = data["subjects"][0].get("strands", [{}])[0]
            if "sub_strands" in first_strand:
                first_substrand = first_strand.get("sub_strands", [{}])[0]
                
                # Grade 1 format has "suggested_learning_experiences"
                if "suggested_learning_experiences" in first_substrand:
                    await seed_grade1_format(data)
                # Grade 10 format has "learning_activities"
                elif "learning_activities" in first_substrand:
                    await seed_grade10_format(data)
                else:
                    print(f"Unknown format in {file_path}")
    elif "grade" in data:
        await seed_grade1_format(data)
    else:
        print(f"Cannot determine format of {file_path}")


async def main():
    parser = argparse.ArgumentParser(description='Seed curriculum data into database')
    parser.add_argument('--file', type=str, help='Specific JSON file to seed')
    parser.add_argument('--all', action='store_true', help='Seed all available JSON files')
    args = parser.parse_args()
    
    print("=" * 60)
    print("CBE Lesson Planner - Curriculum Database Seeding")
    print("=" * 60)
    
    if args.file:
        await seed_from_file(args.file)
    elif args.all:
        # Seed all JSON files
        json_files = [
            str(ROOT_DIR / "curriculum_data" / "grade1_curriculum_complete.json"),
            str(ROOT_DIR / "extracted_curriculum_grade10_languages_powermech.json"),
            str(ROOT_DIR / "extracted_grade10_missing_subjects.json"),
        ]
        
        for file_path in json_files:
            if os.path.exists(file_path):
                await seed_from_file(file_path)
            else:
                print(f"File not found: {file_path}")
    else:
        # Interactive mode
        print("\nAvailable curriculum files:")
        print("1. Grade 1 Curriculum (curriculum_data/grade1_curriculum_complete.json)")
        print("2. Grade 10 Languages & Power Mechanics (extracted_curriculum_grade10_languages_powermech.json)")
        print("3. All files")
        
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == "1":
            await seed_from_file(str(ROOT_DIR / "curriculum_data" / "grade1_curriculum_complete.json"))
        elif choice == "2":
            await seed_from_file(str(ROOT_DIR / "extracted_curriculum_grade10_languages_powermech.json"))
        elif choice == "3":
            await seed_from_file(str(ROOT_DIR / "curriculum_data" / "grade1_curriculum_complete.json"))
            await seed_from_file(str(ROOT_DIR / "extracted_curriculum_grade10_languages_powermech.json"))
        else:
            print("Invalid choice")
            return
    
    # Print statistics
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE - Statistics")
    print("=" * 60)
    print(f"Grades created: {stats['grades_created']}")
    print(f"Subjects created: {stats['subjects_created']}")
    print(f"Strands created: {stats['strands_created']}")
    print(f"Sub-strands created: {stats['substrands_created']}")
    print(f"SLOs created: {stats['slos_created']}")
    print(f"Learning activities created: {stats['learning_activities_created']}")
    print(f"Competencies created: {stats['competencies_created']}")
    print(f"Values created: {stats['values_created']}")
    print(f"PCIs created: {stats['pcis_created']}")
    
    if stats["errors"]:
        print(f"\nErrors: {len(stats['errors'])}")
        for error in stats["errors"][:10]:
            print(f"  - {error}")


if __name__ == "__main__":
    asyncio.run(main())
