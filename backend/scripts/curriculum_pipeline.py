import pdfplumber
import os
import re
from bson import ObjectId
from bson.json_util import dumps

# =========================
# PATH CONFIG
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "data", "pdfs")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# GLOBAL STORAGE
# =========================

grades = []
subjects = []
strands = []
substrands = []
slos = []
slo_mappings = []
learning_activities = []

# =========================
# LOOKUP CACHE (PREVENT DUPLICATES)
# =========================

grade_map = {}
subject_map = {}
strand_map = {}
substrand_map = {}

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
# CORE PROCESSOR
# =========================

def process_pdf(file_path):

    print(f"📄 Processing: {file_path}")

    grade_name = "Grade 10"
    subject_name = "English"

    # GRADE
    if grade_name not in grade_map:
        gid = ObjectId()
        grade_map[grade_name] = gid
        grades.append({
            "_id": gid,
            "name": grade_name,
            "order": 10
        })

    # SUBJECT
    if subject_name not in subject_map:
        sid = ObjectId()
        subject_map[subject_name] = sid
        subjects.append({
            "_id": sid,
            "name": subject_name,
            "gradeIds": [str(grade_map[grade_name])]
        })

    current_strand = None
    current_substrand = None

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:
            text = clean(page.extract_text())

            if not text:
                continue

            # STRAND DETECTION
            strand_match = re.search(r"\d\.\d\s+([A-Za-z\s]+)", text)
            if strand_match:
                name = clean(strand_match.group(1))

                if name not in strand_map:
                    sid = ObjectId()
                    strand_map[name] = sid

                    strands.append({
                        "_id": sid,
                        "name": name,
                        "subjectId": str(subject_map[subject_name])
                    })

                current_strand = strand_map[name]

            # SUBSTRAND DETECTION
            substrand_match = re.search(r"\d\.\d\.\d\s+([A-Za-z\s:/\-]+)", text)
            if substrand_match:
                name = clean(substrand_match.group(1))

                # IMPORTANT: allow duplicates (order matters)
                sid = ObjectId()

                substrands.append({
                    "_id": sid,
                    "name": name,
                    "strandId": str(current_strand)
                })

                current_substrand = sid

            # SLOS
            if "By the end of the sub strand" in text:
                extracted = extract_slos(text)

                for item in extracted:
                    sid = ObjectId()

                    slos.append({
                        "_id": sid,
                        "name": clean(item),
                        "description": clean(item),
                        "substrandId": str(current_substrand)
                    })

                    slo_mappings.append({
                        "_id": ObjectId(),
                        "sloId": str(sid),
                        "competencyIds": [],
                        "valueIds": [],
                        "pciIds": [],
                        "assessmentIds": []
                    })

            # ACTIVITIES
            if "The learner is guided to" in text:
                bullets = extract_bullets(text)

                intro, dev, concl, ext = split_activities(bullets)

                learning_activities.append({
                    "_id": ObjectId(),
                    "substrandId": current_substrand,  # ObjectId
                    "introduction_activities": intro,
                    "development_activities": dev,
                    "conclusion_activities": concl,
                    "extended_activities": ext,
                    "learning_resources": [],
                    "assessment_methods": []
                })

# =========================
# SAVE
# =========================

def save_all():

    collections = {
        "grades.json": grades,
        "subjects.json": subjects,
        "strands.json": strands,
        "substrands.json": substrands,
        "slos.json": slos,
        "slo_mappings.json": slo_mappings,
        "learning_activities.json": learning_activities
    }

    for name, data in collections.items():
        path = os.path.join(OUTPUT_DIR, name)
        with open(path, "w") as f:
            f.write(dumps(data, indent=2))

    print("✅ All files saved to:", OUTPUT_DIR)

# =========================
# RUN ALL PDFs
# =========================

def run():
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".pdf"):
            process_pdf(os.path.join(INPUT_DIR, file))

    save_all()

if __name__ == "__main__":
    run()
