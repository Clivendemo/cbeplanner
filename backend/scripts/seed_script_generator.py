"""
Seed Script Generator (v2)
Takes extracted curriculum JSON and generates a complete Python seed script
with full relational linking: learning activities, competencies, values,
PCIs, assessments, and properly populated SLO mappings.
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
Auto-generated Curriculum Seed Script (v2)
Subject: {subject_name}
Grade: {grade}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Strands: {len(strands)}
Substrands: {sum(len(s.get("substrands", [])) for s in strands)}

Features:
- Full relational linking (competencies, values, PCIs, assessments)
- Populated SLO mappings (not empty)
- Learning activities with resources and assessment methods
- get_or_create helpers to prevent duplicate buildup
- Consistent string IDs throughout
- Safe reseeding (deletes only subject-scoped data)
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
# HELPER FUNCTIONS — get_or_create (prevent duplicate buildup)
# ============================================================================

async def get_or_create_grade(name):
    """Get existing grade or create new one."""
    grade_num = "".join(filter(str.isdigit, name)) or "10"
    existing = await db.grades.find_one({{"name": name}})
    if existing:
        return existing["_id"]
    result = await db.grades.insert_one({{"name": name, "order": int(grade_num)}})
    return result.inserted_id


async def get_or_create_competency(name):
    """Get existing competency by name (case-insensitive) or create new one.
    Returns string ID. Never creates duplicates."""
    name = name.strip()
    if not name:
        return None
    existing = await db.competencies.find_one(
        {{"name": {{"$regex": f"^{{name}}$", "$options": "i"}}}}
    )
    if existing:
        return str(existing["_id"])
    result = await db.competencies.insert_one({{
        "name": name,
        "description": name,
        "createdAt": datetime.utcnow()
    }})
    return str(result.inserted_id)


async def get_or_create_value(name):
    """Get existing value by name (case-insensitive) or create new one.
    Returns string ID."""
    name = name.strip()
    if not name:
        return None
    existing = await db.values.find_one(
        {{"name": {{"$regex": f"^{{name}}$", "$options": "i"}}}}
    )
    if existing:
        return str(existing["_id"])
    result = await db.values.insert_one({{
        "name": name,
        "description": name,
        "createdAt": datetime.utcnow()
    }})
    return str(result.inserted_id)


async def get_or_create_pci(name):
    """Get existing PCI by name (case-insensitive) or create new one.
    Returns string ID."""
    name = name.strip()
    if not name:
        return None
    existing = await db.pcis.find_one(
        {{"name": {{"$regex": f"^{{name}}$", "$options": "i"}}}}
    )
    if existing:
        return str(existing["_id"])
    result = await db.pcis.insert_one({{
        "name": name,
        "description": name,
        "createdAt": datetime.utcnow()
    }})
    return str(result.inserted_id)


async def get_or_create_assessment(name):
    """Get existing assessment method by name (case-insensitive) or create new one.
    Returns string ID."""
    name = name.strip()
    if not name:
        return None
    existing = await db.assessment_methods.find_one(
        {{"name": {{"$regex": f"^{{name}}$", "$options": "i"}}}}
    )
    if existing:
        return str(existing["_id"])
    result = await db.assessment_methods.insert_one({{
        "name": name,
        "description": name,
        "createdAt": datetime.utcnow()
    }})
    return str(result.inserted_id)


def ensure_list(val):
    """Safely convert a value to a list of strings."""
    if not val:
        return []
    if isinstance(val, str):
        return [val] if val.strip() else []
    if isinstance(val, list):
        return [str(v).strip() for v in val if str(v).strip()]
    return []


# ============================================================================
# MAIN SEED FUNCTION
# ============================================================================

async def seed_subject(grade_id):
    """Seed {subject_name} with full relational linking."""
    grade_id_str = str(grade_id)
    subject_name = SUBJECT_DATA["name"]

    print(f"\\n{{'=' * 60}}")
    print(f"Seeding {{subject_name}}...")
    print(f"{{'=' * 60}}")

    # ── Safe reseeding: delete ONLY subject-scoped data ──
    # (competencies, values, PCIs, assessments are GLOBAL — never deleted here)
    existing_subject = await db.subjects.find_one({{
        "name": subject_name,
        "gradeIds": {{"$in": [grade_id_str, [grade_id_str]]}}
    }})
    if not existing_subject:
        # Also check if gradeIds is a string (legacy)
        existing_subject = await db.subjects.find_one({{
            "name": subject_name, "gradeIds": grade_id_str
        }})

    if existing_subject:
        subject_id_str = str(existing_subject["_id"])
        print(f"  Deleting existing data for {{subject_name}} (subject-scoped only)...")

        strands = await db.strands.find({{"subjectId": subject_id_str}}).to_list(200)
        for strand in strands:
            strand_id_str = str(strand["_id"])
            substrands = await db.substrands.find({{"strandId": strand_id_str}}).to_list(500)
            for ss in substrands:
                ss_id_str = str(ss["_id"])
                # Delete SLO mappings linked to this substrand's SLOs
                slos = await db.slos.find({{"substrandId": ss_id_str}}).to_list(500)
                for slo in slos:
                    await db.slo_mappings.delete_many({{"sloId": str(slo["_id"])}})
                await db.slos.delete_many({{"substrandId": ss_id_str}})
                # Delete learning activities (both string and ObjectId substrandId)
                await db.learning_activities.delete_many({{"substrandId": ss_id_str}})
                try:
                    await db.learning_activities.delete_many({{"substrandId": ObjectId(ss_id_str)}})
                except Exception:
                    pass
                # Delete lesson_slos
                await db.lesson_slos.delete_many({{"substrandId": ss_id_str}})
            await db.substrands.delete_many({{"strandId": strand_id_str}})
        await db.strands.delete_many({{"subjectId": subject_id_str}})
        await db.subjects.delete_one({{"_id": existing_subject["_id"]}})
        print(f"    Deleted existing {{subject_name}} data")

    # ── Create subject (gradeIds as a proper list) ──
    subject_result = await db.subjects.insert_one({{
        "name": subject_name,
        "gradeIds": [grade_id_str],
        "createdAt": datetime.utcnow()
    }})
    subject_id = str(subject_result.inserted_id)
    print(f"  Subject ID: {{subject_id}}")

    stats = {{"strands": 0, "substrands": 0, "slos": 0,
             "activities": 0, "mappings": 0,
             "competencies_linked": 0, "values_linked": 0, "pcis_linked": 0}}

    for strand_data in SUBJECT_DATA["strands"]:
        strand_result = await db.strands.insert_one({{
            "name": strand_data["name"],
            "subjectId": subject_id,
            "createdAt": datetime.utcnow()
        }})
        strand_id = str(strand_result.inserted_id)
        stats["strands"] += 1
        print(f"    Strand: {{strand_data['name']}}")

        for ss_data in strand_data.get("substrands", []):
            # number_of_lessons as integer
            num_lessons = ss_data.get("lessons")
            if num_lessons is not None:
                try:
                    num_lessons = int(num_lessons)
                except (ValueError, TypeError):
                    num_lessons = None

            ss_result = await db.substrands.insert_one({{
                "name": ss_data["name"],
                "strandId": strand_id,
                "number_of_lessons": num_lessons,
                "createdAt": datetime.utcnow()
            }})
            ss_id = str(ss_result.inserted_id)
            stats["substrands"] += 1
            print(f"      Substrand: {{ss_data['name']}} ({{num_lessons or '?'}} lessons)")

            # ── Resolve competencies, values, PCIs for this substrand's SLOs ──
            ss_competency_ids = []
            for c in ensure_list(ss_data.get("competencies")):
                cid = await get_or_create_competency(c)
                if cid:
                    ss_competency_ids.append(cid)
                    stats["competencies_linked"] += 1

            ss_value_ids = []
            for v in ensure_list(ss_data.get("values")):
                vid = await get_or_create_value(v)
                if vid:
                    ss_value_ids.append(vid)
                    stats["values_linked"] += 1

            ss_pci_ids = []
            for p in ensure_list(ss_data.get("pcis")):
                pid = await get_or_create_pci(p)
                if pid:
                    ss_pci_ids.append(pid)
                    stats["pcis_linked"] += 1

            # ── Resolve assessment methods from learning_activities ──
            la = ss_data.get("learning_activities", {{}})
            ss_assessment_ids = []
            for a in ensure_list(la.get("assessment")):
                aid = await get_or_create_assessment(a)
                if aid:
                    ss_assessment_ids.append(aid)

            # ── Insert SLOs with populated mappings ──
            for slo_idx, slo_data in enumerate(ss_data.get("slos", [])):
                slo_name = slo_data.get("name", "")
                slo_desc = slo_data.get("description", slo_name)

                slo_result = await db.slos.insert_one({{
                    "name": slo_name,
                    "description": slo_desc,
                    "substrandId": ss_id,
                    "order": slo_idx + 1,
                    "createdAt": datetime.utcnow()
                }})
                slo_id_str = str(slo_result.inserted_id)
                stats["slos"] += 1

                # ── SLO-level overrides (if extractor provided them) ──
                slo_comp_ids = ss_competency_ids[:]
                slo_val_ids = ss_value_ids[:]
                slo_pci_ids = ss_pci_ids[:]
                slo_assess_ids = ss_assessment_ids[:]

                for c in ensure_list(slo_data.get("competencies")):
                    cid = await get_or_create_competency(c)
                    if cid and cid not in slo_comp_ids:
                        slo_comp_ids.append(cid)
                for v in ensure_list(slo_data.get("values")):
                    vid = await get_or_create_value(v)
                    if vid and vid not in slo_val_ids:
                        slo_val_ids.append(vid)
                for p in ensure_list(slo_data.get("pcis")):
                    pid = await get_or_create_pci(p)
                    if pid and pid not in slo_pci_ids:
                        slo_pci_ids.append(pid)
                for a in ensure_list(slo_data.get("assessments")):
                    aid = await get_or_create_assessment(a)
                    if aid and aid not in slo_assess_ids:
                        slo_assess_ids.append(aid)

                # ── Create POPULATED SLO mapping ──
                await db.slo_mappings.insert_one({{
                    "sloId": slo_id_str,
                    "competencyIds": slo_comp_ids,
                    "valueIds": slo_val_ids,
                    "pciIds": slo_pci_ids,
                    "assessmentIds": slo_assess_ids,
                    "createdAt": datetime.utcnow()
                }})
                stats["mappings"] += 1

            # ── Insert learning activities (string substrandId for consistency) ──
            resources = ensure_list(la.get("resources"))

            await db.learning_activities.insert_one({{
                "name": f"{{ss_data['name']}} Activities",
                "substrandId": ss_id,
                "introduction_activities": ensure_list(la.get("introduction")),
                "development_activities": ensure_list(la.get("development")),
                "conclusion_activities": ensure_list(la.get("conclusion")),
                "extended_activities": ensure_list(la.get("extended")),
                "learning_resources": resources,
                "assessment_methods": ensure_list(la.get("assessment")),
                "createdAt": datetime.utcnow()
            }})
            stats["activities"] += 1

    print(f"\\n  Summary for {{subject_name}}:")
    for k, v in stats.items():
        print(f"    {{k}}: {{v}}")

    return stats


async def main():
    print("{{'=' * 60}}")
    print(f"Curriculum Seed v2: {subject_name}")
    print(f"Grade: {grade}")
    print("{{'=' * 60}}")

    grade_id = await get_or_create_grade("{grade}")
    print(f"\\n{grade} ID: {{grade_id}}")

    stats = await seed_subject(grade_id)

    print(f"\\n{{'=' * 60}}")
    print("COMPLETED")
    for k, v in stats.items():
        print(f"  {{k}}: {{v}}")
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
    """Format subject data as a Python dict literal string.

    Uses json.dumps for ALL values to prevent f-string injection
    and ensure valid Python output.
    """
    lines = ["{"]
    lines.append(f'    "name": {json.dumps(subject_name)},')
    lines.append('    "strands": [')

    for si, strand in enumerate(strands):
        lines.append("        {")
        lines.append(f'            "name": {json.dumps(strand.get("name", ""))},')
        lines.append('            "substrands": [')

        for ssi, ss in enumerate(strand.get("substrands", [])):
            lines.append("                {")
            lines.append(f'                    "name": {json.dumps(ss.get("name", ""))},')

            # Lessons as integer
            lessons = ss.get("lessons", 10)
            try:
                lessons = int(lessons)
            except (ValueError, TypeError):
                lessons = 10
            lines.append(f'                    "lessons": {lessons},')

            # SLOs — with per-SLO competencies/values/pcis/assessments
            lines.append('                    "slos": [')
            slos = ss.get("slos", [])
            for sloi, slo in enumerate(slos):
                slo_obj = {
                    "name": slo.get("name", ""),
                    "description": slo.get("description", slo.get("name", "")),
                }
                # Include SLO-level overrides if present
                for field in ["competencies", "values", "pcis", "assessments"]:
                    val = slo.get(field)
                    if val:
                        slo_obj[field] = val if isinstance(val, list) else [val]

                comma = "," if sloi < len(slos) - 1 else ""
                lines.append(f'                        {json.dumps(slo_obj)}{comma}')
            lines.append("                    ],")

            # Learning activities (with resources and assessment)
            la = ss.get("learning_activities", {})
            la_obj = {
                "introduction": la.get("introduction", ""),
                "development": la.get("development", ""),
                "conclusion": la.get("conclusion", ""),
                "extended": la.get("extended", ""),
                "resources": la.get("resources", []),
                "assessment": la.get("assessment", []),
            }
            lines.append(f'                    "learning_activities": {json.dumps(la_obj)},')

            # Competencies, values, PCIs at substrand level
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
