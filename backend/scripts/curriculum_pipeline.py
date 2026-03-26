import pdfplumber
import os
import json
import hashlib
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from scripts.ai_extractor import extract_with_ai

# =========================
# CONFIG
# =========================

MONGO_URI = "mongodb+srv://clive_db_admin:n1ruhu5u@cbeplanner.jtshzub.mongodb.net/cbeplanner?retryWrites=true&w=majority&appName=cbeplanner"
DB_NAME = "cbeplanner"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PDF_DIR = os.path.join(BASE_DIR, "pdfs")
PROCESSED_DIR = os.path.join(BASE_DIR, "pdfs_processed")
TRACK_FILE = os.path.join(BASE_DIR, "curriculum_data", "processed_files.json")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(TRACK_FILE), exist_ok=True)

client = MongoClient("mongodb+srv://clive_db_admin:n1ruhu5u@cbeplanner.jtshzub.mongodb.net/cbeplanner?retryWrites=true&w=majority&appName=cbeplanner")
db = client[cbeplanner]

# =========================
# TRACKING
# =========================

def load_tracking():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tracking(data):
    with open(TRACK_FILE, "w") as f:
        json.dump(data, f, indent=2)

def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

tracking = load_tracking()

# =========================
# UPSERTS
# =========================

def upsert_grade(name, order):
    return db.grades.find_one_and_update(
        {"name": name},
        {"$set": {"order": order}},
        upsert=True,
        return_document=True
    )["_id"]

def upsert_subject(name, grade_id):
    return db.subjects.find_one_and_update(
        {"name": name},
        {"$set": {"gradeIds": [str(grade_id)]}},
        upsert=True,
        return_document=True
    )["_id"]

def upsert_strand(name, subject_id):
    return db.strands.find_one_and_update(
        {"name": name, "subjectId": str(subject_id)},
        {"$set": {}},
        upsert=True,
        return_document=True
    )["_id"]

def insert_substrand(name, strand_id):
    doc = {
        "_id": ObjectId(),
        "name": name,
        "strandId": str(strand_id)
    }
    db.substrands.insert_one(doc)
    return doc["_id"]

def insert_slo(slo, substrand_id):
    doc = {
        "_id": ObjectId(),
        "name": slo["name"],
        "description": slo["description"],
        "substrandId": str(substrand_id)
    }
    db.slos.insert_one(doc)
    return doc["_id"]

def insert_mapping(slo_id):
    db.slo_mappings.insert_one({
        "_id": ObjectId(),
        "sloId": str(slo_id),
        "competencyIds": [],
        "valueIds": [],
        "pciIds": [],
        "assessmentIds": []
    })

def insert_activities(substrand_id, activities):
    db.learning_activities.insert_one({
        "_id": ObjectId(),
        "substrandId": substrand_id,
        "introduction_activities": activities.get("introduction", []),
        "development_activities": activities.get("development", []),
        "conclusion_activities": activities.get("conclusion", []),
        "extended_activities": activities.get("extended", []),
        "learning_resources": [],
        "assessment_methods": []
    })

# =========================
# METADATA
# =========================

def extract_metadata(path):
    parts = path.lower().split(os.sep)
    grade = next((p for p in parts if "grade" in p), "grade10")
    grade_num = ''.join(filter(str.isdigit, grade))
    subject = os.path.basename(path).replace(".pdf", "")
    return grade_num, subject

# =========================
# PROCESS
# =========================

def process_pdf(path):

    filename = os.path.basename(path)
    print(f"\n📄 Processing: {filename}")

    grade, subject = extract_metadata(path)

    grade_id = upsert_grade(f"Grade {grade}", int(grade))
    subject_id = upsert_subject(subject.title(), grade_id)

    with pdfplumber.open(path) as pdf:

        for i, page in enumerate(pdf.pages):

            text = page.extract_text()
            if not text:
                continue

            print(f"   ➤ Page {i+1}")

            ai_data = extract_with_ai(text)

            if not ai_data:
                continue

            strand_id = upsert_strand(ai_data["strand"], subject_id)
            substrand_id = insert_substrand(ai_data["substrand"], strand_id)

            for slo in ai_data.get("slos", []):
                slo_id = insert_slo(slo, substrand_id)
                insert_mapping(slo_id)

            insert_activities(substrand_id, ai_data.get("activities", {}))

    print(f"✅ Finished: {filename}")

# =========================
# RUNNER
# =========================

def run():

    print("\n🚀 AI Curriculum Pipeline Starting...\n")

    for root, _, files in os.walk(PDF_DIR):

        for file in files:

            if not file.endswith(".pdf"):
                continue

            path = os.path.join(root, file)
            h = file_hash(path)

            if h in tracking:
                print(f"⏭ Skipping duplicate: {file}")
                continue

            process_pdf(path)

            tracking[h] = {
                "file": file,
                "processed_at": str(datetime.now())
            }

            os.rename(path, os.path.join(PROCESSED_DIR, file))

    save_tracking(tracking)

    print("\n🎉 DONE — AI Pipeline Complete")

if __name__ == "__main__":
    run()
