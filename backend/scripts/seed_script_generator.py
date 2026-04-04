"""
Seed Script Generator
Takes extracted curriculum JSON and generates a complete Python seed script
identical in format to seed_grade10_complete_part1.py.
"""

import json
import os
from datetime import datetime


def generate_seed_script(extracted_data: dict, output_path: str) -> str:
    """Generate a complete Python seed script from extracted curriculum data.
    
    Args:
        extracted_data: Dict with grade, subject_name, strands (from AI extractor)
        output_path: Where to save the generated .py file
    
    Returns:
        Path to the generated script
    """
    grade = extracted_data.get("grade", "Grade 10")
    subject_name = extracted_data.get("subject_name", "Unknown Subject")
    strands = extracted_data.get("strands", [])

    # Build the data literal as a Python dict string
    data_str = _format_subject_data(subject_name, strands)

    script = f'''"""
Auto-generated Curriculum Seed Script
Subject: {subject_name}
Grade: {grade}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Strands: {len(strands)}
Substrands: {sum(len(s.get("substrands", [])) for s in strands)}
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "cbeplanner-oregon")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# ============================================================================
# {subject_name.upper()} — COMPLETE DATA
# ============================================================================

SUBJECT_DATA = {data_str}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_or_create_grade(name):
    """Get existing grade or create new one."""
    grade_num = "".join(filter(str.isdigit, name)) or "10"
    existing = await db.grades.find_one({{"name": name}})
    if existing:
        return existing["_id"]
    result = await db.grades.insert_one({{"name": name, "order": int(grade_num)}})
    return result.inserted_id


async def create_default_slo_mapping(slo_id):
    """Create default SLO mapping with empty arrays."""
    await db.slo_mappings.insert_one({{
        "sloId": str(slo_id),
        "competencyIds": [],
        "valueIds": [],
        "pciIds": [],
        "assessmentIds": []
    }})


async def seed_subject(grade_id):
    """Seed {subject_name} data."""
    grade_id_str = str(grade_id)
    subject_name = SUBJECT_DATA["name"]

    print(f"\\n{{'=' * 60}}")
    print(f"Seeding {{subject_name}}...")
    print(f"{{'=' * 60}}")

    # Delete existing data for this subject under this grade
    existing_subject = await db.subjects.find_one({{"name": subject_name, "gradeIds": grade_id_str}})
    if existing_subject:
        subject_id_str = str(existing_subject["_id"])
        print(f"  Deleting existing data for {{subject_name}}...")

        # Delete all related data
        strands = await db.strands.find({{"subjectId": subject_id_str}}).to_list(100)
        for strand in strands:
            strand_id_str = str(strand["_id"])
            substrands = await db.substrands.find({{"strandId": strand_id_str}}).to_list(200)
            for ss in substrands:
                ss_id_str = str(ss["_id"])
                ss_id_obj = ss["_id"]
                # Delete SLOs and mappings
                slos = await db.slos.find({{"substrandId": ss_id_str}}).to_list(500)
                for slo in slos:
                    await db.slo_mappings.delete_many({{"sloId": str(slo["_id"])}})
                await db.slos.delete_many({{"substrandId": ss_id_str}})
                # Delete activities
                await db.learning_activities.delete_many({{"substrandId": ss_id_obj}})
                await db.learning_activities.delete_many({{"substrandId": ss_id_str}})
            await db.substrands.delete_many({{"strandId": strand_id_str}})
        await db.strands.delete_many({{"subjectId": subject_id_str}})
        await db.subjects.delete_one({{"_id": existing_subject["_id"]}})
        print(f"    Deleted existing {{subject_name}} data")

    # Create subject
    subject_result = await db.subjects.insert_one({{
        "name": subject_name,
        "gradeIds": grade_id_str
    }})
    subject_id = str(subject_result.inserted_id)
    print(f"  Subject ID: {{subject_id}}")

    total_strands = 0
    total_substrands = 0
    total_slos = 0
    total_activities = 0
    total_mappings = 0

    for strand_data in SUBJECT_DATA["strands"]:
        strand_result = await db.strands.insert_one({{
            "name": strand_data["name"],
            "subjectId": subject_id
        }})
        strand_id = str(strand_result.inserted_id)
        total_strands += 1
        print(f"    Strand: {{strand_data['name']}}")

        for ss_data in strand_data.get("substrands", []):
            ss_result = await db.substrands.insert_one({{
                "name": ss_data["name"],
                "strandId": strand_id
            }})
            ss_id = str(ss_result.inserted_id)
            total_substrands += 1
            lessons = ss_data.get("lessons", 10)
            print(f"      Substrand: {{ss_data['name']}} ({{lessons}} lessons)")

            # Insert SLOs
            for slo_data in ss_data.get("slos", []):
                slo_result = await db.slos.insert_one({{
                    "name": slo_data["name"],
                    "description": slo_data.get("description", slo_data["name"]),
                    "substrandId": ss_id
                }})
                await create_default_slo_mapping(slo_result.inserted_id)
                total_slos += 1
                total_mappings += 1

            # Insert learning activities
            la = ss_data.get("learning_activities", {{}})
            intro = la.get("introduction", "")
            dev = la.get("development", "")
            concl = la.get("conclusion", "")
            ext = la.get("extended", "")

            await db.learning_activities.insert_one({{
                "substrandId": ObjectId(ss_id),
                "introduction_activities": [intro] if isinstance(intro, str) and intro else (intro if isinstance(intro, list) else []),
                "development_activities": [dev] if isinstance(dev, str) and dev else (dev if isinstance(dev, list) else []),
                "conclusion_activities": [concl] if isinstance(concl, str) and concl else (concl if isinstance(concl, list) else []),
                "extended_activities": [ext] if isinstance(ext, str) and ext else (ext if isinstance(ext, list) else []),
            }})
            total_activities += 1

    print(f"\\n  Summary for {{subject_name}}:")
    print(f"    Strands: {{total_strands}}")
    print(f"    Substrands: {{total_substrands}}")
    print(f"    SLOs: {{total_slos}}")
    print(f"    Learning Activities: {{total_activities}}")
    print(f"    SLO Mappings: {{total_mappings}}")

    return {{
        "strands": total_strands,
        "substrands": total_substrands,
        "slos": total_slos,
        "activities": total_activities,
        "mappings": total_mappings
    }}


async def main():
    print("{{'=' * 60}}")
    print(f"Curriculum Seed: {subject_name}")
    print(f"Grade: {grade}")
    print("{{'=' * 60}}")

    grade_id = await get_or_create_grade("{grade}")
    print(f"\\n{grade} ID: {{grade_id}}")

    stats = await seed_subject(grade_id)

    print(f"\\n{{'=' * 60}}")
    print("COMPLETED")
    print(f"  Strands: {{stats['strands']}}")
    print(f"  Substrands: {{stats['substrands']}}")
    print(f"  SLOs: {{stats['slos']}}")
    print(f"  Activities: {{stats['activities']}}")
    print(f"  Mappings: {{stats['mappings']}}")
    print(f"{{'=' * 60}}")


if __name__ == "__main__":
    asyncio.run(main())
'''

    # Write the script
    with open(output_path, "w") as f:
        f.write(script)

    print(f"  Seed script saved to: {output_path}")
    return output_path


def _format_subject_data(subject_name: str, strands: list) -> str:
    """Format subject data as a Python dict literal string."""
    lines = ["{"]
    lines.append(f'    "name": {json.dumps(subject_name)},')
    lines.append('    "strands": [')

    for si, strand in enumerate(strands):
        lines.append("        {")
        lines.append(f'            "name": {json.dumps(strand["name"])},')
        lines.append('            "substrands": [')

        for ssi, ss in enumerate(strand.get("substrands", [])):
            lines.append("                {")
            lines.append(f'                    "name": {json.dumps(ss["name"])},')
            lines.append(f'                    "lessons": {ss.get("lessons", 10)},')

            # SLOs
            lines.append('                    "slos": [')
            for sloi, slo in enumerate(ss.get("slos", [])):
                comma = "," if sloi < len(ss.get("slos", [])) - 1 else ""
                lines.append(f'                        {{"name": {json.dumps(slo["name"])}, "description": {json.dumps(slo.get("description", slo["name"]))}}}{comma}')
            lines.append("                    ],")

            # Learning activities
            la = ss.get("learning_activities", {})
            lines.append('                    "learning_activities": {')
            lines.append(f'                        "introduction": {json.dumps(la.get("introduction", ""))},')
            lines.append(f'                        "development": {json.dumps(la.get("development", ""))},')
            lines.append(f'                        "conclusion": {json.dumps(la.get("conclusion", ""))},')
            lines.append(f'                        "extended": {json.dumps(la.get("extended", ""))},')
            lines.append(f'                        "resources": {json.dumps(la.get("resources", []))},')
            lines.append(f'                        "assessment": {json.dumps(la.get("assessment", []))}')
            lines.append("                    },")

            # Competencies, values, PCIs
            lines.append(f'                    "competencies": {json.dumps(ss.get("competencies", []))},')
            lines.append(f'                    "values": {json.dumps(ss.get("values", []))},')
            lines.append(f'                    "pcis": {json.dumps(ss.get("pcis", []))}')

            comma = "," if ssi < len(strand.get("substrands", [])) - 1 else ""
            lines.append(f"                }}{comma}")

        lines.append("            ]")
        comma = "," if si < len(strands) - 1 else ""
        lines.append(f"        }}{comma}")

    lines.append("    ]")
    lines.append("}")

    return "\n".join(lines)
