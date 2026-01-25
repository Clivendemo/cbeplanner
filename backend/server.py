from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize Firebase Admin (for token verification)
# Note: Firebase Admin SDK doesn't need explicit credentials for token verification
# It only needs the project ID which is extracted from the token
if not firebase_admin._apps:
    firebase_admin.initialize_app()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Helper to convert ObjectId to string
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# ==================== MODELS ====================

class User(BaseModel):
    id: Optional[str] = None
    firebaseUid: str
    email: EmailStr
    firstName: str
    lastName: str
    role: str = "teacher"  # teacher or admin
    walletBalance: float = 0.0
    freeLessonUsed: bool = False
    freeNotesUsed: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class Grade(BaseModel):
    id: Optional[str] = None
    name: str
    order: int

class Subject(BaseModel):
    id: Optional[str] = None
    name: str
    gradeIds: List[str]

class Strand(BaseModel):
    id: Optional[str] = None
    name: str
    subjectId: str

class SubStrand(BaseModel):
    id: Optional[str] = None
    name: str
    strandId: str

class SLO(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    substrandId: str

class Competency(BaseModel):
    id: Optional[str] = None
    name: str
    description: str

class Value(BaseModel):
    id: Optional[str] = None
    name: str
    description: str

class PCI(BaseModel):
    id: Optional[str] = None
    name: str
    description: str

class Activity(BaseModel):
    id: Optional[str] = None
    description: str
    strandId: str
    substrandId: str

class Assessment(BaseModel):
    id: Optional[str] = None
    name: str
    description: str

class SLOMapping(BaseModel):
    id: Optional[str] = None
    sloId: str
    competencyIds: List[str] = []
    valueIds: List[str] = []
    pciIds: List[str] = []
    assessmentIds: List[str] = []

class LessonPlan(BaseModel):
    id: Optional[str] = None
    teacherId: str
    gradeId: str
    gradeName: str
    subjectId: str
    subjectName: str
    strandId: str
    strandName: str
    substrandId: str
    substrandName: str
    sloId: str
    sloName: str
    sloDescription: str
    activities: List[str] = []
    competencies: List[Dict[str, str]] = []
    values: List[Dict[str, str]] = []
    pcis: List[Dict[str, str]] = []
    assessments: List[Dict[str, str]] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)

# Request models
class TokenVerifyRequest(BaseModel):
    idToken: str

class GenerateLessonRequest(BaseModel):
    gradeId: str
    subjectId: str
    strandId: str
    substrandId: str
    sloId: str

class CreateAdminRequest(BaseModel):
    email: EmailStr
    password: str

# ==================== AUTHENTICATION ====================

async def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split("Bearer ")[1]
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Get or create user
        user = await db.users.find_one({"firebaseUid": uid})
        if not user:
            new_user = {
                "firebaseUid": uid,
                "email": email,
                "role": "teacher",
                "walletBalance": 0.0,
                "freeLessonUsed": False,
                "createdAt": datetime.utcnow()
            }
            result = await db.users.insert_one(new_user)
            user = await db.users.find_one({"_id": result.inserted_id})
        
        return serialize_doc(user)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

async def verify_admin(authorization: Optional[str] = Header(None)):
    user = await verify_token(authorization)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/verify")
async def verify_user_token(request: TokenVerifyRequest):
    try:
        decoded_token = firebase_auth.verify_id_token(request.idToken)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        user = await db.users.find_one({"firebaseUid": uid})
        if not user:
            new_user = {
                "firebaseUid": uid,
                "email": email,
                "role": "teacher",
                "walletBalance": 0.0,
                "freeLessonUsed": False,
                "createdAt": datetime.utcnow()
            }
            result = await db.users.insert_one(new_user)
            user = await db.users.find_one({"_id": result.inserted_id})
        
        return {"success": True, "user": serialize_doc(user)}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@api_router.post("/auth/set-admin")
async def set_user_as_admin(user: dict = Depends(verify_token)):
    """Set the current user as admin - for initial setup only"""
    try:
        await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": {"role": "admin"}}
        )
        return {"success": True, "message": "User set as admin successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== TEACHER ENDPOINTS ====================

@api_router.get("/profile")
async def get_profile(user: dict = Depends(verify_token)):
    return {"success": True, "user": user}

@api_router.get("/grades")
async def get_grades(user: dict = Depends(verify_token)):
    grades = await db.grades.find().sort("order", 1).to_list(100)
    return {"success": True, "grades": [serialize_doc(g) for g in grades]}

@api_router.get("/subjects")
async def get_subjects(gradeId: str, user: dict = Depends(verify_token)):
    subjects = await db.subjects.find({"gradeIds": gradeId}).to_list(100)
    return {"success": True, "subjects": [serialize_doc(s) for s in subjects]}

@api_router.get("/strands")
async def get_strands(subjectId: str, user: dict = Depends(verify_token)):
    strands = await db.strands.find({"subjectId": subjectId}).to_list(100)
    return {"success": True, "strands": [serialize_doc(s) for s in strands]}

@api_router.get("/substrands")
async def get_substrands(strandId: str, user: dict = Depends(verify_token)):
    substrands = await db.substrands.find({"strandId": strandId}).to_list(100)
    return {"success": True, "substrands": [serialize_doc(s) for s in substrands]}

@api_router.get("/slos")
async def get_slos(substrandId: str, user: dict = Depends(verify_token)):
    slos = await db.slos.find({"substrandId": substrandId}).to_list(100)
    return {"success": True, "slos": [serialize_doc(s) for s in slos]}

@api_router.post("/lesson-plans/generate")
async def generate_lesson_plan(request: GenerateLessonRequest, user: dict = Depends(verify_token)):
    # Check if user has free lesson or wallet balance
    if not user["freeLessonUsed"]:
        # Use free lesson
        await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": {"freeLessonUsed": True}}
        )
    else:
        # Check wallet balance (price per lesson = 10 KES, will be configurable)
        lesson_price = 10.0
        if user["walletBalance"] < lesson_price:
            raise HTTPException(status_code=402, detail="Insufficient wallet balance")
        
        # Deduct from wallet
        await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$inc": {"walletBalance": -lesson_price}}
        )
    
    # Fetch all related data
    grade = await db.grades.find_one({"_id": ObjectId(request.gradeId)})
    subject = await db.subjects.find_one({"_id": ObjectId(request.subjectId)})
    strand = await db.strands.find_one({"_id": ObjectId(request.strandId)})
    substrand = await db.substrands.find_one({"_id": ObjectId(request.substrandId)})
    slo = await db.slos.find_one({"_id": ObjectId(request.sloId)})
    
    if not all([grade, subject, strand, substrand, slo]):
        raise HTTPException(status_code=404, detail="Invalid selection")
    
    # Get activities for this strand/substrand
    activities = await db.activities.find({
        "strandId": request.strandId,
        "substrandId": request.substrandId
    }).to_list(100)
    
    # Get SLO mappings
    mapping = await db.slo_mappings.find_one({"sloId": request.sloId})
    
    competencies = []
    values = []
    pcis = []
    assessments = []
    
    if mapping:
        # Fetch competencies
        if mapping.get("competencyIds"):
            comp_docs = await db.competencies.find({
                "_id": {"$in": [ObjectId(cid) for cid in mapping["competencyIds"]]}
            }).to_list(100)
            competencies = [{"name": c["name"], "description": c["description"]} for c in comp_docs]
        
        # Fetch values
        if mapping.get("valueIds"):
            val_docs = await db.values.find({
                "_id": {"$in": [ObjectId(vid) for vid in mapping["valueIds"]]}
            }).to_list(100)
            values = [{"name": v["name"], "description": v["description"]} for v in val_docs]
        
        # Fetch PCIs
        if mapping.get("pciIds"):
            pci_docs = await db.pcis.find({
                "_id": {"$in": [ObjectId(pid) for pid in mapping["pciIds"]]}
            }).to_list(100)
            pcis = [{"name": p["name"], "description": p["description"]} for p in pci_docs]
        
        # Fetch assessments
        if mapping.get("assessmentIds"):
            assess_docs = await db.assessments.find({
                "_id": {"$in": [ObjectId(aid) for aid in mapping["assessmentIds"]]}
            }).to_list(100)
            assessments = [{"name": a["name"], "description": a["description"]} for a in assess_docs]
    
    # Create lesson plan
    lesson_plan = {
        "teacherId": user["id"],
        "gradeId": request.gradeId,
        "gradeName": grade["name"],
        "subjectId": request.subjectId,
        "subjectName": subject["name"],
        "strandId": request.strandId,
        "strandName": strand["name"],
        "substrandId": request.substrandId,
        "substrandName": substrand["name"],
        "sloId": request.sloId,
        "sloName": slo["name"],
        "sloDescription": slo["description"],
        "activities": [a["description"] for a in activities],
        "competencies": competencies,
        "values": values,
        "pcis": pcis,
        "assessments": assessments,
        "createdAt": datetime.utcnow()
    }
    
    result = await db.lesson_plans.insert_one(lesson_plan)
    lesson_plan["id"] = str(result.inserted_id)
    
    return {"success": True, "lessonPlan": lesson_plan}

@api_router.get("/lesson-plans")
async def get_lesson_plans(user: dict = Depends(verify_token)):
    plans = await db.lesson_plans.find({"teacherId": user["id"]}).sort("createdAt", -1).to_list(100)
    return {"success": True, "lessonPlans": [serialize_doc(p) for p in plans]}

# ==================== ADMIN ENDPOINTS ====================

# Grades
@api_router.get("/admin/grades")
async def admin_get_grades(user: dict = Depends(verify_admin)):
    grades = await db.grades.find().sort("order", 1).to_list(100)
    return {"success": True, "grades": [serialize_doc(g) for g in grades]}

@api_router.post("/admin/grades")
async def admin_create_grade(grade: Grade, user: dict = Depends(verify_admin)):
    result = await db.grades.insert_one(grade.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

@api_router.put("/admin/grades/{grade_id}")
async def admin_update_grade(grade_id: str, grade: Grade, user: dict = Depends(verify_admin)):
    await db.grades.update_one({"_id": ObjectId(grade_id)}, {"$set": grade.dict(exclude={"id"})})
    return {"success": True}

@api_router.delete("/admin/grades/{grade_id}")
async def admin_delete_grade(grade_id: str, user: dict = Depends(verify_admin)):
    await db.grades.delete_one({"_id": ObjectId(grade_id)})
    return {"success": True}

# Subjects
@api_router.get("/admin/subjects")
async def admin_get_subjects(user: dict = Depends(verify_admin)):
    subjects = await db.subjects.find().to_list(100)
    return {"success": True, "subjects": [serialize_doc(s) for s in subjects]}

@api_router.post("/admin/subjects")
async def admin_create_subject(subject: Subject, user: dict = Depends(verify_admin)):
    result = await db.subjects.insert_one(subject.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

@api_router.put("/admin/subjects/{subject_id}")
async def admin_update_subject(subject_id: str, subject: Subject, user: dict = Depends(verify_admin)):
    await db.subjects.update_one({"_id": ObjectId(subject_id)}, {"$set": subject.dict(exclude={"id"})})
    return {"success": True}

@api_router.delete("/admin/subjects/{subject_id}")
async def admin_delete_subject(subject_id: str, user: dict = Depends(verify_admin)):
    await db.subjects.delete_one({"_id": ObjectId(subject_id)})
    return {"success": True}

# Strands
@api_router.get("/admin/strands")
async def admin_get_strands(subjectId: Optional[str] = None, user: dict = Depends(verify_admin)):
    query = {"subjectId": subjectId} if subjectId else {}
    strands = await db.strands.find(query).to_list(100)
    return {"success": True, "strands": [serialize_doc(s) for s in strands]}

@api_router.post("/admin/strands")
async def admin_create_strand(strand: Strand, user: dict = Depends(verify_admin)):
    result = await db.strands.insert_one(strand.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

@api_router.put("/admin/strands/{strand_id}")
async def admin_update_strand(strand_id: str, strand: Strand, user: dict = Depends(verify_admin)):
    await db.strands.update_one({"_id": ObjectId(strand_id)}, {"$set": strand.dict(exclude={"id"})})
    return {"success": True}

@api_router.delete("/admin/strands/{strand_id}")
async def admin_delete_strand(strand_id: str, user: dict = Depends(verify_admin)):
    await db.strands.delete_one({"_id": ObjectId(strand_id)})
    return {"success": True}

# SubStrands
@api_router.get("/admin/substrands")
async def admin_get_substrands(strandId: Optional[str] = None, user: dict = Depends(verify_admin)):
    query = {"strandId": strandId} if strandId else {}
    substrands = await db.substrands.find(query).to_list(100)
    return {"success": True, "substrands": [serialize_doc(s) for s in substrands]}

@api_router.post("/admin/substrands")
async def admin_create_substrand(substrand: SubStrand, user: dict = Depends(verify_admin)):
    result = await db.substrands.insert_one(substrand.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

@api_router.put("/admin/substrands/{substrand_id}")
async def admin_update_substrand(substrand_id: str, substrand: SubStrand, user: dict = Depends(verify_admin)):
    await db.substrands.update_one({"_id": ObjectId(substrand_id)}, {"$set": substrand.dict(exclude={"id"})})
    return {"success": True}

@api_router.delete("/admin/substrands/{substrand_id}")
async def admin_delete_substrand(substrand_id: str, user: dict = Depends(verify_admin)):
    await db.substrands.delete_one({"_id": ObjectId(substrand_id)})
    return {"success": True}

# SLOs
@api_router.get("/admin/slos")
async def admin_get_slos(substrandId: Optional[str] = None, user: dict = Depends(verify_admin)):
    query = {"substrandId": substrandId} if substrandId else {}
    slos = await db.slos.find(query).to_list(100)
    return {"success": True, "slos": [serialize_doc(s) for s in slos]}

@api_router.post("/admin/slos")
async def admin_create_slo(slo: SLO, user: dict = Depends(verify_admin)):
    result = await db.slos.insert_one(slo.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

@api_router.put("/admin/slos/{slo_id}")
async def admin_update_slo(slo_id: str, slo: SLO, user: dict = Depends(verify_admin)):
    await db.slos.update_one({"_id": ObjectId(slo_id)}, {"$set": slo.dict(exclude={"id"})})
    return {"success": True}

@api_router.delete("/admin/slos/{slo_id}")
async def admin_delete_slo(slo_id: str, user: dict = Depends(verify_admin)):
    await db.slos.delete_one({"_id": ObjectId(slo_id)})
    return {"success": True}

# Activities
@api_router.get("/admin/activities")
async def admin_get_activities(user: dict = Depends(verify_admin)):
    activities = await db.activities.find().to_list(100)
    return {"success": True, "activities": [serialize_doc(a) for a in activities]}

@api_router.post("/admin/activities")
async def admin_create_activity(activity: Activity, user: dict = Depends(verify_admin)):
    result = await db.activities.insert_one(activity.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

@api_router.delete("/admin/activities/{activity_id}")
async def admin_delete_activity(activity_id: str, user: dict = Depends(verify_admin)):
    await db.activities.delete_one({"_id": ObjectId(activity_id)})
    return {"success": True}

# Competencies
@api_router.get("/admin/competencies")
async def admin_get_competencies(user: dict = Depends(verify_admin)):
    competencies = await db.competencies.find().to_list(100)
    return {"success": True, "competencies": [serialize_doc(c) for c in competencies]}

@api_router.post("/admin/competencies")
async def admin_create_competency(competency: Competency, user: dict = Depends(verify_admin)):
    result = await db.competencies.insert_one(competency.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

# Values
@api_router.get("/admin/values")
async def admin_get_values(user: dict = Depends(verify_admin)):
    values = await db.values.find().to_list(100)
    return {"success": True, "values": [serialize_doc(v) for v in values]}

@api_router.post("/admin/values")
async def admin_create_value(value: Value, user: dict = Depends(verify_admin)):
    result = await db.values.insert_one(value.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

# PCIs
@api_router.get("/admin/pcis")
async def admin_get_pcis(user: dict = Depends(verify_admin)):
    pcis = await db.pcis.find().to_list(100)
    return {"success": True, "pcis": [serialize_doc(p) for p in pcis]}

@api_router.post("/admin/pcis")
async def admin_create_pci(pci: PCI, user: dict = Depends(verify_admin)):
    result = await db.pcis.insert_one(pci.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

# Assessments
@api_router.get("/admin/assessments")
async def admin_get_assessments(user: dict = Depends(verify_admin)):
    assessments = await db.assessments.find().to_list(100)
    return {"success": True, "assessments": [serialize_doc(a) for a in assessments]}

@api_router.post("/admin/assessments")
async def admin_create_assessment(assessment: Assessment, user: dict = Depends(verify_admin)):
    result = await db.assessments.insert_one(assessment.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

# SLO Mappings
@api_router.get("/admin/slo-mappings/{slo_id}")
async def admin_get_slo_mapping(slo_id: str, user: dict = Depends(verify_admin)):
    mapping = await db.slo_mappings.find_one({"sloId": slo_id})
    if mapping:
        return {"success": True, "mapping": serialize_doc(mapping)}
    return {"success": True, "mapping": None}

@api_router.post("/admin/slo-mappings")
async def admin_create_slo_mapping(mapping: SLOMapping, user: dict = Depends(verify_admin)):
    # Check if mapping exists
    existing = await db.slo_mappings.find_one({"sloId": mapping.sloId})
    if existing:
        # Update
        await db.slo_mappings.update_one(
            {"sloId": mapping.sloId},
            {"$set": mapping.dict(exclude={"id"})}
        )
        return {"success": True, "message": "Mapping updated"}
    else:
        # Create
        result = await db.slo_mappings.insert_one(mapping.dict(exclude={"id"}))
        return {"success": True, "id": str(result.inserted_id)}

# ==================== SEED DATA ENDPOINT ====================

@api_router.post("/admin/seed-data")
async def seed_sample_data(user: dict = Depends(verify_admin)):
    """Seed sample curriculum data"""
    
    # Clear existing data
    await db.grades.delete_many({})
    await db.subjects.delete_many({})
    await db.strands.delete_many({})
    await db.substrands.delete_many({})
    await db.slos.delete_many({})
    await db.activities.delete_many({})
    await db.competencies.delete_many({})
    await db.values.delete_many({})
    await db.pcis.delete_many({})
    await db.assessments.delete_many({})
    await db.slo_mappings.delete_many({})
    
    # Create Grades
    grades_data = [
        {"name": "Grade 1", "order": 1},
        {"name": "Grade 2", "order": 2},
        {"name": "Grade 3", "order": 3},
        {"name": "Grade 4", "order": 4},
        {"name": "Grade 5", "order": 5},
        {"name": "Grade 6", "order": 6}
    ]
    grades_result = await db.grades.insert_many(grades_data)
    grade_ids = [str(id) for id in grades_result.inserted_ids]
    
    # Create Subjects (grade-specific)
    subjects_data = [
        # Lower Primary (Grades 1-3)
        {"name": "Literacy Activities", "gradeIds": grade_ids[0:3]},
        {"name": "Mathematical Activities", "gradeIds": grade_ids[0:3]},
        {"name": "Environmental Activities", "gradeIds": grade_ids[0:3]},
        # Upper Primary (Grades 4-6)
        {"name": "English", "gradeIds": grade_ids[3:6]},
        {"name": "Mathematics", "gradeIds": grade_ids[3:6]},
        {"name": "Science and Technology", "gradeIds": grade_ids[3:6]},
        {"name": "Social Studies", "gradeIds": grade_ids[3:6]}
    ]
    subjects_result = await db.subjects.insert_many(subjects_data)
    subject_ids = [str(id) for id in subjects_result.inserted_ids]
    
    # Create Strands for Mathematics (Grade 4-6)
    math_subject_id = subject_ids[4]
    strands_data = [
        {"name": "Numbers", "subjectId": math_subject_id},
        {"name": "Algebra", "subjectId": math_subject_id},
        {"name": "Geometry", "subjectId": math_subject_id},
        {"name": "Measurement", "subjectId": math_subject_id}
    ]
    strands_result = await db.strands.insert_many(strands_data)
    strand_ids = [str(id) for id in strands_result.inserted_ids]
    
    # Create Sub-strands for Numbers
    numbers_strand_id = strand_ids[0]
    substrands_data = [
        {"name": "Whole Numbers", "strandId": numbers_strand_id},
        {"name": "Fractions", "strandId": numbers_strand_id},
        {"name": "Decimals", "strandId": numbers_strand_id}
    ]
    substrands_result = await db.substrands.insert_many(substrands_data)
    substrand_ids = [str(id) for id in substrands_result.inserted_ids]
    
    # Create SLOs for Whole Numbers
    whole_numbers_substrand_id = substrand_ids[0]
    slos_data = [
        {
            "name": "Read and write numbers up to 10,000",
            "description": "By the end of the sub-strand, the learner should be able to read and write numbers up to 10,000 in numerals and words",
            "substrandId": whole_numbers_substrand_id
        },
        {
            "name": "Compare and order numbers",
            "description": "By the end of the sub-strand, the learner should be able to compare and order numbers up to 10,000",
            "substrandId": whole_numbers_substrand_id
        }
    ]
    slos_result = await db.slos.insert_many(slos_data)
    slo_ids = [str(id) for id in slos_result.inserted_ids]
    
    # Create Activities
    activities_data = [
        {
            "description": "Use number cards to practice reading and writing numbers",
            "strandId": numbers_strand_id,
            "substrandId": whole_numbers_substrand_id
        },
        {
            "description": "Play number ordering games using place value charts",
            "strandId": numbers_strand_id,
            "substrandId": whole_numbers_substrand_id
        },
        {
            "description": "Count objects in groups and write the corresponding numerals",
            "strandId": numbers_strand_id,
            "substrandId": whole_numbers_substrand_id
        }
    ]
    await db.activities.insert_many(activities_data)
    
    # Create Core Competencies
    competencies_data = [
        {"name": "Communication and Collaboration", "description": "Learners work together and share ideas"},
        {"name": "Critical Thinking and Problem Solving", "description": "Learners analyze and solve mathematical problems"},
        {"name": "Creativity and Imagination", "description": "Learners explore different ways to solve problems"},
        {"name": "Digital Literacy", "description": "Learners use digital tools for learning"}
    ]
    competencies_result = await db.competencies.insert_many(competencies_data)
    competency_ids = [str(id) for id in competencies_result.inserted_ids]
    
    # Create Core Values
    values_data = [
        {"name": "Respect", "description": "Learners show respect for others' ideas and contributions"},
        {"name": "Integrity", "description": "Learners demonstrate honesty in their work"},
        {"name": "Responsibility", "description": "Learners take responsibility for their learning"},
        {"name": "Unity", "description": "Learners work together harmoniously"}
    ]
    values_result = await db.values.insert_many(values_data)
    value_ids = [str(id) for id in values_result.inserted_ids]
    
    # Create PCIs
    pcis_data = [
        {"name": "Financial Literacy", "description": "Understanding the value and use of money"},
        {"name": "Education for Sustainable Development", "description": "Learning about conservation and sustainability"},
        {"name": "Safety and Security", "description": "Understanding safety in various contexts"}
    ]
    pcis_result = await db.pcis.insert_many(pcis_data)
    pci_ids = [str(id) for id in pcis_result.inserted_ids]
    
    # Create Assessments
    assessments_data = [
        {"name": "Oral Questions", "description": "Ask learners to read numbers aloud"},
        {"name": "Written Exercise", "description": "Provide worksheets with number writing tasks"},
        {"name": "Group Activity", "description": "Observe learners working in groups"},
        {"name": "Practical Task", "description": "Give real-world number problems to solve"}
    ]
    assessments_result = await db.assessments.insert_many(assessments_data)
    assessment_ids = [str(id) for id in assessments_result.inserted_ids]
    
    # Create SLO Mappings
    mappings_data = [
        {
            "sloId": slo_ids[0],
            "competencyIds": [competency_ids[0], competency_ids[1]],
            "valueIds": [value_ids[1], value_ids[2]],
            "pciIds": [pci_ids[0]],
            "assessmentIds": [assessment_ids[0], assessment_ids[1]]
        },
        {
            "sloId": slo_ids[1],
            "competencyIds": [competency_ids[1], competency_ids[2]],
            "valueIds": [value_ids[0], value_ids[3]],
            "pciIds": [pci_ids[0]],
            "assessmentIds": [assessment_ids[2], assessment_ids[3]]
        }
    ]
    await db.slo_mappings.insert_many(mappings_data)
    
    return {"success": True, "message": "Sample data seeded successfully"}

# Health check endpoint
@app.get("/api/")
async def health_check():
    return {"message": "CBE Lesson Planning System API is running", "status": "healthy"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
