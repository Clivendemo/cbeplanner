import pdfplumber
import os
import re
import json
import hashlib
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime

# =========================
# CONFIG
# =========================

MONGO_URI = "mongodb+srv://clive_db_admin:n1ruhu5u@cbeplanner.jtshzub.mongodb.net/cbeplanner?retryWrites=true&w=majority&appName=cbeplanner
DB_NAME	cbeplanner"
DB_NAME = "cbeplanner"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PDF_DIR = os.path.join(BASE_DIR, "pdfs")
PROCESSED_DIR = os.path.join(BASE_DIR, "pdfs_processed")
TRACK_FILE = os.path.join(BASE_DIR, "curriculum_data", "processed_files.json")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(TRACK_FILE), exist_ok=True)

client = MongoClient(mongodb+srv://clive_db_admin:n1ruhu5u@cbeplanner.jtshzub.mongodb.net/cbeplanner?retryWrites=true&w=majority&appName=cbeplanner
DB_NAME	cbeplanner)
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
# SMART METADATA DETECTION
# =========================

def extract_metadata(file_path):

    grade = None
    subject = None

    # 1. Try folder name
    parts = file_path.lower().split(os.sep)
    for part in parts:
        if "grade" in part:
            grade = re.findall(r"\d+", part)
            if grade:
                grade = grade[0]

    # 2. Try filename
    filename = os.path.basename(file_path).lower().replace(".pdf", "")
    subject = filename.replace("_", " ").strip()

    return grade, subject


def extract_metadata_from_pdf(file_path):

    grade = None
    subject = None

    try:
        with pdfplumber.open(file_path) as pdf:
            first_page = pdf.pages[0].extract_text()

            if first_page:
                first_page = first_page.lower()

                # detect grade
                g = re.search(r"grade\s*(\d+)", first_page)
                if g:
                    grade = g.group(1)

                # detect subject
                s = re.search(r"\n([a-z\s]+)\n", first_page)
                if s:
                    subject = s.group(1).strip()

    except:
        pass

    return grade, subject

# =========================
# HELPERS
# =========================

def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()

def extract_slos(text):
    return re.findall(r"[a-d]\)\s*(.*)", text)

def extract_bullets(text):
    return re.findall(r"[●•]\s*(.*)", text)

def split_activities(items):
    if not items:
        return [], [], [], []

    intro = items[:2]
    dev = items[2:-2] if len(items) > 4 else items
    concl = items[-2:-1] if len(items) > 3 else []
    ext = items[-1:] if len(items) > 3 else []

    return intro, dev, concl, ext

# =========================
# UPSERTS
# =========================

def upsert_grade(name, order):
    result = db.grades.find_one_and_update(
        {"name": name},
        {"$set": {"order": order}},
        upsert=True,
        return_document=True
    )
    return result["_id"]

def upsert_subject(name, grade_id):
    result = db.subjects.find_one_and_update(
        {"name": name},
        {"$set": {"gradeIds": [str(grade_id)]}},
        upsert=True,
        return_document=True
    )
    return result["_id"]

def upsert_strand(name, subject_id):
    result = db.strands.find_one_and_update(
        {"name": name, "subjectId": str(subject_id)},
        {"$set": {}},
        upsert=True,
        return_document=True
    )
    return result["_id"]

def insert_substrand(name, strand_id):
    doc = {
        "_id": ObjectId(),
        "name": name,
        "strandId": str(strand_id)
    }
    db.substrands.insert_one(doc)
    return doc["_id"]

def upsert_slo(name, substrand_id):
    result = db.slos.find_one_and_update(
        {
            "name": name,
            "substrandId": str(substrand_id)
        },
        {"$set": {"description": name}},
        upsert=True,
        return_document=True
    )
    return result["_id"]

def upsert_mapping(slo_id):
    db.slo_mappings.update_one(
        {"sloId": str(slo_id)},
        {"$set": {
            "competencyIds": [],
            "valueIds": [],
            "pciIds": [],
            "assessmentIds": []
        }},
        upsert=True
    )

def replace_learning_activities(substrand_id, data):
    db.learning_activities.delete_many({"substrandId": substrand_id})
    data["substrandId"] = substrand_id
    db.learning_activities.insert_one(data)

# =========================
# CORE PROCESSOR
# =========================

def process_pdf(file_path):

    filename = os.path.basename(file_path)

    print(f"\n📄 Processing: {filename}")

    # FIRST: folder/filename metadata
    grade, subject = extract_metadata(file_path)

    # FALLBACK: PDF content
    if not grade or not subject:
        g2, s2 = extract_metadata_from_pdf(file_path)
        grade = grade or g2
        subject = subject or s2

    # FINAL DEFAULT (safety)
    grade = grade or "10"
    subject = subject or "English"

    grade_name = f"Grade {grade}"
    subject_name = subject.title()

    print(f"   🎯 Detected → {grade_name} | {subject_name}")

    grade_id = upsert_grade(grade_name, int(grade))
    subject_id = upsert_subject(subject_name, grade_id)

    current_strand = None
    current_substrand = None

    with pdfplumber.open(file_path) as pdf:

        for i, page in enumerate(pdf.pages):

            text = clean(page.extract_text())

            if not text:
                continue

            print(f"   ➤ Page {i+1}")

            # STRAND
            strand_match = re.search(r"\d\.\d\s+([A-Za-z\s]+)", text)
            if strand_match:
                name = clean(strand_match.group(1))
                current_strand = upsert_strand(name, subject_id)

            # SUBSTRAND
            substrand_match = re.search(r"\d\.\d\.\d\s+([A-Za-z\s:/\-]+)", text)
            if substrand_match:
                name = clean(substrand_match.group(1))
                current_substrand = insert_substrand(name, current_strand)

            # SLOS
            if "By the end of the sub strand" in text:
                for item in extract_slos(text):
                    slo_id = upsert_slo(clean(item), current_substrand)
                    upsert_mapping(slo_id)

            # ACTIVITIES
            if "The learner is guided to" in text:
                bullets = extract_bullets(text)
                intro, dev, concl, ext = split_activities(bullets)

                replace_learning_activities(current_substrand, {
                    "_id": ObjectId(),
                    "introduction_activities": intro,
                    "development_activities": dev,
                    "conclusion_activities": concl,
                    "extended_activities": ext,
                    "learning_resources": [],
                    "assessment_methods": []
                })

    print(f"✅ Finished: {filename}")

# =========================
# RUNNER
# =========================

def run():

    print("\n🚀 Starting Smart Curriculum Pipeline...\n")

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

            print(f"📦 Moved to processed: {file}")

    save_tracking(tracking)

    print("\n🎉 ALL DONE — Smart Pipeline Complete")

# =========================

if __name__ == "__main__":
    run()
