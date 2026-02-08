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
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Firebase project configuration
FIREBASE_PROJECT_ID = "cbeplanner"
FIREBASE_API_KEY = "AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8"

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
    schoolName: str = ""  # Default empty if not provided
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
    teacherName: str
    schoolName: str
    duration: int  # 40 or 80 minutes
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
    # SLOs classified by domain
    knowledge: List[str] = []
    skills: List[str] = []
    attitudes: List[str] = []
    # Learning resources
    learningResources: List[str] = []
    # Core components
    competencies: List[Dict[str, str]] = []
    values: List[Dict[str, str]] = []
    pcis: List[Dict[str, str]] = []
    # Lesson body structure
    introduction: str = ""
    lessonDevelopment: str = ""
    extendedActivity: str = ""  # Only for 80 minutes
    conclusion: str = ""
    assessment: str = ""
    createdAt: datetime = Field(default_factory=datetime.utcnow)

# Request models
class TokenVerifyRequest(BaseModel):
    idToken: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    schoolName: Optional[str] = None

class GenerateLessonRequest(BaseModel):
    duration: int  # 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80
    gradeId: str
    subjectId: str
    strandId: str
    substrandId: str
    sloId: str

class GenerateNotesRequest(BaseModel):
    duration: int  # 25-80 minutes
    gradeId: str
    subjectId: str
    strandId: str
    substrandId: str

class CreateAdminRequest(BaseModel):
    email: EmailStr
    password: str

class Notes(BaseModel):
    id: Optional[str] = None
    teacherId: str
    teacherName: str
    schoolName: str
    duration: int
    gradeId: str
    gradeName: str
    subjectId: str
    subjectName: str
    strandId: str
    strandName: str
    substrandId: str
    substrandName: str
    content: str
    keyPoints: List[str] = []
    examples: List[str] = []
    activities: List[str] = []
    summary: str = ""
    createdAt: datetime = Field(default_factory=datetime.utcnow)

# Schemes of Work Models
class BreakInput(BaseModel):
    breakType: str  # Assessment, Half-Term, Examination, Holiday, Custom
    startWeek: int
    startLesson: Optional[int] = None  # Optional, for mid-week breaks
    durationType: str  # lessons, fraction, weeks
    durationValue: float
    description: Optional[str] = None

class SchemeOfWorkRequest(BaseModel):
    subjectId: str
    gradeId: str
    term: int  # 1, 2, or 3
    year: int
    school: str
    teacherName: str
    curriculumStandard: str = "KICD CBC"
    totalWeeks: int
    lessonsPerWeek: int
    breaks: List[BreakInput] = []

class SchemeLesson(BaseModel):
    week: int
    lessonNumber: int
    isBreak: bool = False
    breakType: Optional[str] = None
    breakDescription: Optional[str] = None
    strand: Optional[str] = None
    substrand: Optional[str] = None
    slo: Optional[str] = None
    keyInquiryQuestions: List[str] = []
    learningExperiences: List[str] = []
    learningResources: List[str] = []
    assessmentMethods: List[str] = []
    reflection: str = ""

class SchemeOfWork(BaseModel):
    id: Optional[str] = None
    teacherId: str
    teacherName: str
    school: str
    subjectId: str
    subjectName: str
    gradeId: str
    gradeName: str
    term: int
    year: int
    curriculumStandard: str
    totalWeeks: int
    lessonsPerWeek: int
    lessons: List[Dict[str, Any]] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)

# ==================== AUTHENTICATION ====================

async def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split("Bearer ")[1]
    try:
        # Verify token using Google's public keys
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={FIREBASE_API_KEY}",
                json={"idToken": token}
            )
            
            if response.status_code != 200:
                error_detail = response.json() if response.text else "Invalid token"
                raise HTTPException(status_code=401, detail=f"Token validation failed: {error_detail}")
            
            data = response.json()
            if "users" not in data or len(data["users"]) == 0:
                raise HTTPException(status_code=401, detail="No user found for token")
            
            user_data = data["users"][0]
            uid = user_data["localId"]
            email = user_data.get("email", "")
        
        # Get or create user
        user = await db.users.find_one({"firebaseUid": uid})
        if not user:
            new_user = {
                "firebaseUid": uid,
                "email": email,
                "firstName": "",
                "lastName": "",
                "schoolName": "",
                "role": "teacher",
                "walletBalance": 0.0,
                "freeLessonUsed": False,
                "freeNotesUsed": False,
                "createdAt": datetime.utcnow()
            }
            result = await db.users.insert_one(new_user)
            user = await db.users.find_one({"_id": result.inserted_id})
        
        return serialize_doc(user)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=401, detail=f"Network error during token verification: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification error: {str(e)}")

async def verify_admin(authorization: Optional[str] = Header(None)):
    user = await verify_token(authorization)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/verify")
async def verify_user_token(request: TokenVerifyRequest):
    try:
        # Verify token using Google's Identity Toolkit API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={FIREBASE_API_KEY}",
                json={"idToken": request.idToken}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            data = response.json()
            if "users" not in data or len(data["users"]) == 0:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_data = data["users"][0]
            uid = user_data["localId"]
            email = user_data.get("email", "")
        
        user = await db.users.find_one({"firebaseUid": uid})
        if not user:
            # Create new user with firstName, lastName, and schoolName
            new_user = {
                "firebaseUid": uid,
                "email": email,
                "firstName": request.firstName or "",
                "lastName": request.lastName or "",
                "schoolName": request.schoolName or "",
                "role": "teacher",
                "walletBalance": 0.0,
                "freeLessonUsed": False,
                "freeNotesUsed": False,
                "createdAt": datetime.utcnow()
            }
            result = await db.users.insert_one(new_user)
            user = await db.users.find_one({"_id": result.inserted_id})
        
        return {"success": True, "user": serialize_doc(user)}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@api_router.post("/auth/initialize-admin")
async def initialize_default_admin():
    """Initialize default admin account - requires manual Firebase user creation"""
    try:
        # Check if admin already exists
        existing_admin = await db.users.find_one({"role": "admin"})
        if existing_admin:
            return {"success": True, "message": "Admin already exists", "exists": True}
        
        # Check if user with admin email exists in database
        default_email = "admin@cbeplanner.com"
        admin_user = await db.users.find_one({"email": default_email})
        
        if admin_user:
            # Update role to admin
            await db.users.update_one(
                {"_id": admin_user["_id"]},
                {"$set": {"role": "admin"}}
            )
            return {"success": True, "message": "User promoted to admin"}
        
        return {
            "success": False,
            "message": "Please create Firebase user with email: admin@cbeplanner.com and login first",
            "exists": False
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== TEACHER ENDPOINTS ====================

@api_router.get("/profile")
async def get_profile(user: dict = Depends(verify_token)):
    return {"success": True, "user": user}

@api_router.post("/profile/reset-free-trial")
async def reset_free_trial(user: dict = Depends(verify_token)):
    """Reset user's free lesson/notes trial for testing"""
    await db.users.update_one(
        {"_id": ObjectId(user["id"])},
        {"$set": {"freeLessonUsed": False, "freeNotesUsed": False, "walletBalance": 100.0}}
    )
    return {"success": True, "message": "Free trial reset and 100 KES added to wallet"}

@api_router.post("/profile/become-admin")
async def become_admin(user: dict = Depends(verify_token)):
    """Promote current user to admin (for testing only)"""
    await db.users.update_one(
        {"_id": ObjectId(user["id"])},
        {"$set": {"role": "admin"}}
    )
    return {"success": True, "message": "You are now an admin. Please refresh the app."}

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
        await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": {"freeLessonUsed": True}}
        )
    else:
        lesson_price = 10.0
        if user["walletBalance"] < lesson_price:
            raise HTTPException(status_code=402, detail="Insufficient wallet balance")
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
        if mapping.get("competencyIds"):
            comp_docs = await db.competencies.find({
                "_id": {"$in": [ObjectId(cid) for cid in mapping["competencyIds"]]}
            }).to_list(100)
            competencies = [{"name": c["name"], "description": c["description"]} for c in comp_docs]
        
        if mapping.get("valueIds"):
            val_docs = await db.values.find({
                "_id": {"$in": [ObjectId(vid) for vid in mapping["valueIds"]]}
            }).to_list(100)
            values = [{"name": v["name"], "description": v["description"]} for v in val_docs]
        
        if mapping.get("pciIds"):
            pci_docs = await db.pcis.find({
                "_id": {"$in": [ObjectId(pid) for pid in mapping["pciIds"]]}
            }).to_list(100)
            pcis = [{"name": p["name"], "description": p["description"]} for p in pci_docs]
        
        if mapping.get("assessmentIds"):
            assess_docs = await db.assessments.find({
                "_id": {"$in": [ObjectId(aid) for aid in mapping["assessmentIds"]]}
            }).to_list(100)
            assessments = [{"name": a["name"], "description": a["description"]} for a in assess_docs]
    
    # Duration-aware content generation
    duration = request.duration
    
    # Classify SLOs by domain
    knowledge = [f"Understand {slo['name']}", f"Recall key concepts of {substrand['name']}"]
    skills = [f"Apply {substrand['name']} concepts", f"Demonstrate understanding of {slo['name']}"]
    attitudes = ["Show curiosity and interest", "Develop positive learning habits"]
    
    # Learning resources
    learning_resources = ["Textbooks", "Charts and diagrams", "Real objects/models", "Digital resources"]
    
    # Duration-based content depth
    if duration <= 40:
        # Short lesson (25-40 min): Brief, focused
        intro_time = 5
        dev_time = duration - 15
        conclusion_time = 5
        assessment_time = 5
        
        introduction = f"Teacher introduces {substrand['name']} ({intro_time} min). Learners share what they know about the topic."
        lesson_development = f"Teacher explains {slo['name']} with examples ({dev_time} min). " + \
                           f"Learners participate in: {activities[0]['description'] if activities else 'guided practice'}."
        extended_activity = ""
        conclusion = f"Teacher summarizes key points ({conclusion_time} min). Learners reflect on learning."
        assessment_text = f"Quick assessment ({assessment_time} min): " + \
                        (assessments[0]['description'] if assessments else "Oral questions and observation")
    
    elif duration <= 60:
        # Medium lesson (45-60 min): Moderate depth
        intro_time = 7
        dev_time = int((duration - 20) * 0.6)
        ext_time = int((duration - 20) * 0.4)
        conclusion_time = 8
        assessment_time = 5
        
        introduction = f"Teacher introduces {substrand['name']} with real-life examples ({intro_time} min). " + \
                      "Learners brainstorm and share prior knowledge."
        lesson_development = f"Teacher explains {slo['name']} in detail ({dev_time} min). " + \
                           f"Learners engage in: {', '.join([a['description'] for a in activities[:2]]) if activities else 'guided activities'}."
        extended_activity = f"Group work ({ext_time} min): Learners work in small groups on practical tasks related to {substrand['name']}."
        conclusion = f"Class discussion and summary ({conclusion_time} min). Learners present findings and reflect."
        assessment_text = f"Assessment ({assessment_time} min): " + \
                        ('; '.join([a['description'] for a in assessments[:2]]) if assessments else "Oral questions, written tasks, and observation")
    
    else:
        # Long lesson (65-80 min): Comprehensive
        intro_time = 10
        dev_time = int((duration - 25) * 0.45)
        ext_time = int((duration - 25) * 0.35)
        conclusion_time = 10
        assessment_time = int((duration - 25) * 0.20)
        
        introduction = f"Comprehensive introduction to {substrand['name']} ({intro_time} min). " + \
                      "Teacher uses multimedia/real objects. Learners engage in discussion and pre-assessment."
        lesson_development = f"Detailed explanation of {slo['name']} with multiple examples ({dev_time} min). " + \
                           f"Learners participate in: {', '.join([a['description'] for a in activities[:3]]) if activities else 'various guided activities'}."
        extended_activity = f"Extended group work and differentiated activities ({ext_time} min): " + \
                          f"Learners explore {substrand['name']} through projects, experiments, or research. Teacher provides individualized support."
        conclusion = f"Comprehensive review and reflection ({conclusion_time} min). " + \
                    "Group presentations, peer feedback, and teacher summary."
        assessment_text = f"Comprehensive assessment ({assessment_time} min): " + \
                        ('; '.join([a['description'] for a in assessments]) if assessments else \
                         "Multiple methods - oral questions, written tasks, practical demonstrations, peer assessment")
    
    # Create lesson plan with teacher info from profile
    lesson_plan = {
        "teacherId": user["id"],
        "teacherName": f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
        "schoolName": user.get("schoolName", ""),
        "duration": duration,
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
        "knowledge": knowledge,
        "skills": skills,
        "attitudes": attitudes,
        "learningResources": learning_resources,
        "competencies": competencies,
        "values": values,
        "pcis": pcis,
        "introduction": introduction,
        "lessonDevelopment": lesson_development,
        "extendedActivity": extended_activity,
        "conclusion": conclusion,
        "assessment": assessment_text,
        "createdAt": datetime.utcnow()
    }
    
    result = await db.lesson_plans.insert_one(lesson_plan)
    # Remove MongoDB _id and add string id
    if "_id" in lesson_plan:
        del lesson_plan["_id"]
    lesson_plan["id"] = str(result.inserted_id)
    # Convert datetime to ISO string for JSON serialization
    lesson_plan["createdAt"] = lesson_plan["createdAt"].isoformat()
    
    return {"success": True, "lessonPlan": lesson_plan}

@api_router.get("/lesson-plans")
async def get_lesson_plans(user: dict = Depends(verify_token)):
    plans = await db.lesson_plans.find({"teacherId": user["id"]}).sort("createdAt", -1).to_list(100)
    return {"success": True, "lessonPlans": [serialize_doc(p) for p in plans]}

@api_router.post("/notes/generate")
async def generate_notes(request: GenerateNotesRequest, user: dict = Depends(verify_token)):
    # Check if user has free notes or wallet balance
    if not user["freeNotesUsed"]:
        await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": {"freeNotesUsed": True}}
        )
    else:
        notes_price = 5.0
        if user["walletBalance"] < notes_price:
            raise HTTPException(status_code=402, detail="Insufficient wallet balance")
        await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$inc": {"walletBalance": -notes_price}}
        )
    
    # Fetch all related data
    grade = await db.grades.find_one({"_id": ObjectId(request.gradeId)})
    subject = await db.subjects.find_one({"_id": ObjectId(request.subjectId)})
    strand = await db.strands.find_one({"_id": ObjectId(request.strandId)})
    substrand = await db.substrands.find_one({"_id": ObjectId(request.substrandId)})
    
    if not all([grade, subject, strand, substrand]):
        raise HTTPException(status_code=404, detail="Invalid selection")
    
    # Get activities
    activities = await db.activities.find({
        "strandId": request.strandId,
        "substrandId": request.substrandId
    }).to_list(100)
    
    # Duration-aware content generation
    duration = request.duration
    
    if duration <= 40:
        # Short notes: Brief, bullet points
        content = f"# {substrand['name']}\n\n" + \
                 f"## Key Points\n" + \
                 f"- Understanding {substrand['name']} concepts\n" + \
                 f"- Basic principles and applications\n" + \
                 f"- Real-world examples\n\n" + \
                 f"## Summary\n" + \
                 f"Brief explanation of {substrand['name']} within {strand['name']}."
    elif duration <= 60:
        # Medium notes: Moderate detail
        content = f"# {substrand['name']}\n\n" + \
                 f"## Introduction\n" + \
                 f"{substrand['name']} is an important concept in {strand['name']}.\n\n" + \
                 f"## Key Concepts\n" + \
                 f"- Definition and explanation\n" + \
                 f"- Core principles\n" + \
                 f"- Practical applications\n" + \
                 f"- Examples and illustrations\n\n" + \
                 f"## Important Points\n" + \
                 f"Detailed explanation of concepts with examples."
    else:
        # Comprehensive notes: Full detail
        content = f"# {substrand['name']}\n\n" + \
                 f"## Introduction\n" + \
                 f"{substrand['name']} is a fundamental topic in {strand['name']} that forms the basis for further learning.\n\n" + \
                 f"## Detailed Explanation\n" + \
                 f"- Comprehensive overview of concepts\n" + \
                 f"- Theoretical foundations\n" + \
                 f"- Practical applications and real-world relevance\n" + \
                 f"- Multiple examples and case studies\n" + \
                 f"- Common misconceptions and clarifications\n\n" + \
                 f"## Learning Activities\n" + \
                 f"Students can engage in various activities to deepen understanding.\n\n" + \
                 f"## Review Questions\n" + \
                 f"Key questions for self-assessment and revision."
    
    # Create notes
    notes = {
        "teacherId": user["id"],
        "teacherName": f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
        "schoolName": user.get("schoolName", ""),
        "duration": duration,
        "gradeId": request.gradeId,
        "gradeName": grade["name"],
        "subjectId": request.subjectId,
        "subjectName": subject["name"],
        "strandId": request.strandId,
        "strandName": strand["name"],
        "substrandId": request.substrandId,
        "substrandName": substrand["name"],
        "content": content,
        "activities": [a["description"] for a in activities],
        "createdAt": datetime.utcnow()
    }
    
    result = await db.notes.insert_one(notes)
    # Remove MongoDB _id and add string id
    if "_id" in notes:
        del notes["_id"]
    notes["id"] = str(result.inserted_id)
    # Convert datetime to ISO string for JSON serialization
    notes["createdAt"] = notes["createdAt"].isoformat()
    
    return {"success": True, "notes": notes}

@api_router.get("/notes")
async def get_notes(user: dict = Depends(verify_token)):
    notes = await db.notes.find({"teacherId": user["id"]}).sort("createdAt", -1).to_list(100)
    return {"success": True, "notes": [serialize_doc(n) for n in notes]}

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

@api_router.post("/admin/seed")
async def seed_public():
    """Public endpoint to seed sample data for testing"""
    return await seed_sample_data_internal()

@api_router.post("/admin/seed-data")
async def seed_sample_data(user: dict = Depends(verify_admin)):
    """Seed comprehensive sample curriculum data (admin only)"""
    return await seed_sample_data_internal()

async def seed_sample_data_internal():
    """Internal function to seed comprehensive sample curriculum data"""
    
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
    
    # ==================== CREATE GRADES ====================
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
    
    # ==================== CREATE SUBJECTS ====================
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
    
    # Extract subject IDs for easier reference
    math_subject_id = subject_ids[4]  # Mathematics for Grade 4-6
    english_subject_id = subject_ids[3]  # English for Grade 4-6
    science_subject_id = subject_ids[5]  # Science for Grade 4-6
    
    # ==================== CREATE STRANDS ====================
    
    # Mathematics Strands
    math_strands = [
        {"name": "Numbers", "subjectId": math_subject_id},
        {"name": "Algebra", "subjectId": math_subject_id},
        {"name": "Geometry", "subjectId": math_subject_id},
        {"name": "Measurement", "subjectId": math_subject_id}
    ]
    math_strands_result = await db.strands.insert_many(math_strands)
    math_strand_ids = [str(id) for id in math_strands_result.inserted_ids]
    
    # English Strands
    english_strands = [
        {"name": "Listening and Speaking", "subjectId": english_subject_id},
        {"name": "Reading", "subjectId": english_subject_id},
        {"name": "Writing", "subjectId": english_subject_id},
        {"name": "Language Structure", "subjectId": english_subject_id}
    ]
    english_strands_result = await db.strands.insert_many(english_strands)
    english_strand_ids = [str(id) for id in english_strands_result.inserted_ids]
    
    # Science Strands
    science_strands = [
        {"name": "Living Things", "subjectId": science_subject_id},
        {"name": "Energy", "subjectId": science_subject_id},
        {"name": "Materials", "subjectId": science_subject_id}
    ]
    science_strands_result = await db.strands.insert_many(science_strands)
    science_strand_ids = [str(id) for id in science_strands_result.inserted_ids]
    
    # ==================== CREATE SUB-STRANDS ====================
    
    # Math - Numbers sub-strands
    numbers_substrands = [
        {"name": "Whole Numbers", "strandId": math_strand_ids[0]},
        {"name": "Fractions", "strandId": math_strand_ids[0]},
        {"name": "Decimals", "strandId": math_strand_ids[0]},
        {"name": "Percentages", "strandId": math_strand_ids[0]}
    ]
    numbers_substrands_result = await db.substrands.insert_many(numbers_substrands)
    numbers_substrand_ids = [str(id) for id in numbers_substrands_result.inserted_ids]
    
    # Math - Geometry sub-strands
    geometry_substrands = [
        {"name": "2D Shapes", "strandId": math_strand_ids[2]},
        {"name": "3D Shapes", "strandId": math_strand_ids[2]},
        {"name": "Angles", "strandId": math_strand_ids[2]}
    ]
    geometry_substrands_result = await db.substrands.insert_many(geometry_substrands)
    geometry_substrand_ids = [str(id) for id in geometry_substrands_result.inserted_ids]
    
    # English - Reading sub-strands
    reading_substrands = [
        {"name": "Comprehension", "strandId": english_strand_ids[1]},
        {"name": "Vocabulary", "strandId": english_strand_ids[1]},
        {"name": "Fluency", "strandId": english_strand_ids[1]}
    ]
    reading_substrands_result = await db.substrands.insert_many(reading_substrands)
    reading_substrand_ids = [str(id) for id in reading_substrands_result.inserted_ids]
    
    # Science - Living Things sub-strands
    living_things_substrands = [
        {"name": "Plants", "strandId": science_strand_ids[0]},
        {"name": "Animals", "strandId": science_strand_ids[0]},
        {"name": "Human Body", "strandId": science_strand_ids[0]}
    ]
    living_things_substrands_result = await db.substrands.insert_many(living_things_substrands)
    living_things_substrand_ids = [str(id) for id in living_things_substrands_result.inserted_ids]
    
    # ==================== CREATE SLOs ====================
    
    # Math - Whole Numbers SLOs
    whole_numbers_slos = [
        {
            "name": "Read and write numbers up to 10,000",
            "description": "By the end of the sub-strand, the learner should be able to read and write numbers up to 10,000 in numerals and words",
            "substrandId": numbers_substrand_ids[0]
        },
        {
            "name": "Compare and order numbers up to 10,000",
            "description": "By the end of the sub-strand, the learner should be able to compare and order numbers up to 10,000 using greater than, less than and equal to",
            "substrandId": numbers_substrand_ids[0]
        },
        {
            "name": "Add and subtract numbers up to 10,000",
            "description": "By the end of the sub-strand, the learner should be able to add and subtract whole numbers up to 10,000",
            "substrandId": numbers_substrand_ids[0]
        }
    ]
    whole_numbers_slos_result = await db.slos.insert_many(whole_numbers_slos)
    whole_numbers_slo_ids = [str(id) for id in whole_numbers_slos_result.inserted_ids]
    
    # Math - 2D Shapes SLOs
    shapes_slos = [
        {
            "name": "Identify and name 2D shapes",
            "description": "By the end of the sub-strand, the learner should be able to identify and name common 2D shapes including triangles, squares, rectangles, and circles",
            "substrandId": geometry_substrand_ids[0]
        },
        {
            "name": "Draw 2D shapes",
            "description": "By the end of the sub-strand, the learner should be able to draw and construct basic 2D shapes using appropriate tools",
            "substrandId": geometry_substrand_ids[0]
        }
    ]
    shapes_slos_result = await db.slos.insert_many(shapes_slos)
    shapes_slo_ids = [str(id) for id in shapes_slos_result.inserted_ids]
    
    # English - Reading Comprehension SLOs
    reading_slos = [
        {
            "name": "Read and understand short stories",
            "description": "By the end of the sub-strand, the learner should be able to read and comprehend short stories, identifying main ideas and characters",
            "substrandId": reading_substrand_ids[0]
        },
        {
            "name": "Answer questions about texts",
            "description": "By the end of the sub-strand, the learner should be able to answer literal and inferential questions about texts read",
            "substrandId": reading_substrand_ids[0]
        }
    ]
    reading_slos_result = await db.slos.insert_many(reading_slos)
    reading_slo_ids = [str(id) for id in reading_slos_result.inserted_ids]
    
    # Science - Plants SLOs
    plants_slos = [
        {
            "name": "Identify parts of a plant",
            "description": "By the end of the sub-strand, the learner should be able to identify and name the main parts of a flowering plant",
            "substrandId": living_things_substrand_ids[0]
        },
        {
            "name": "Describe plant growth",
            "description": "By the end of the sub-strand, the learner should be able to describe the life cycle and growth process of plants",
            "substrandId": living_things_substrand_ids[0]
        }
    ]
    plants_slos_result = await db.slos.insert_many(plants_slos)
    plants_slo_ids = [str(id) for id in plants_slos_result.inserted_ids]
    
    # ==================== CREATE ACTIVITIES ====================
    activities_data = [
        # Math - Whole Numbers
        {"description": "Use number cards to practice reading and writing numbers", "strandId": math_strand_ids[0], "substrandId": numbers_substrand_ids[0]},
        {"description": "Play number ordering games using place value charts", "strandId": math_strand_ids[0], "substrandId": numbers_substrand_ids[0]},
        {"description": "Count objects in groups and write the corresponding numerals", "strandId": math_strand_ids[0], "substrandId": numbers_substrand_ids[0]},
        {"description": "Practice addition and subtraction using counters and number lines", "strandId": math_strand_ids[0], "substrandId": numbers_substrand_ids[0]},
        # Math - Shapes
        {"description": "Identify 2D shapes in the classroom environment", "strandId": math_strand_ids[2], "substrandId": geometry_substrand_ids[0]},
        {"description": "Draw shapes using rulers and geometric tools", "strandId": math_strand_ids[2], "substrandId": geometry_substrand_ids[0]},
        {"description": "Create shape patterns and designs", "strandId": math_strand_ids[2], "substrandId": geometry_substrand_ids[0]},
        # English - Reading
        {"description": "Read short passages aloud and discuss main ideas", "strandId": english_strand_ids[1], "substrandId": reading_substrand_ids[0]},
        {"description": "Answer comprehension questions in pairs", "strandId": english_strand_ids[1], "substrandId": reading_substrand_ids[0]},
        {"description": "Identify and list new vocabulary from texts", "strandId": english_strand_ids[1], "substrandId": reading_substrand_ids[0]},
        # Science - Plants
        {"description": "Observe and label parts of real plants", "strandId": science_strand_ids[0], "substrandId": living_things_substrand_ids[0]},
        {"description": "Plant seeds and observe their growth over time", "strandId": science_strand_ids[0], "substrandId": living_things_substrand_ids[0]},
        {"description": "Draw and label the life cycle of a plant", "strandId": science_strand_ids[0], "substrandId": living_things_substrand_ids[0]}
    ]
    await db.activities.insert_many(activities_data)
    
    # ==================== CREATE CORE COMPETENCIES ====================
    competencies_data = [
        {"name": "Communication and Collaboration", "description": "Learners work together effectively and share ideas clearly"},
        {"name": "Critical Thinking and Problem Solving", "description": "Learners analyze situations and develop creative solutions"},
        {"name": "Creativity and Imagination", "description": "Learners explore different approaches and think innovatively"},
        {"name": "Digital Literacy", "description": "Learners use digital tools and resources effectively"},
        {"name": "Learning to Learn", "description": "Learners take responsibility for their own learning"},
        {"name": "Self-Efficacy", "description": "Learners develop confidence in their abilities"}
    ]
    competencies_result = await db.competencies.insert_many(competencies_data)
    competency_ids = [str(id) for id in competencies_result.inserted_ids]
    
    # ==================== CREATE CORE VALUES ====================
    values_data = [
        {"name": "Respect", "description": "Learners show respect for others, ideas, and diversity"},
        {"name": "Integrity", "description": "Learners demonstrate honesty and ethical behavior"},
        {"name": "Responsibility", "description": "Learners take ownership of their actions and learning"},
        {"name": "Unity", "description": "Learners work together harmoniously and support each other"},
        {"name": "Peace", "description": "Learners promote peaceful coexistence and conflict resolution"},
        {"name": "Love", "description": "Learners show care and compassion for others"},
        {"name": "Patriotism", "description": "Learners appreciate and contribute to their nation"}
    ]
    values_result = await db.values.insert_many(values_data)
    value_ids = [str(id) for id in values_result.inserted_ids]
    
    # ==================== CREATE PCIs ====================
    pcis_data = [
        {"name": "Financial Literacy", "description": "Understanding the value and responsible use of money"},
        {"name": "Education for Sustainable Development", "description": "Learning about environmental conservation and sustainability"},
        {"name": "Safety and Security", "description": "Understanding personal and community safety"},
        {"name": "Health Education", "description": "Promoting healthy lifestyles and wellbeing"},
        {"name": "Citizenship", "description": "Understanding rights, responsibilities, and civic engagement"},
        {"name": "Social Cohesion", "description": "Promoting unity and harmony in diverse communities"}
    ]
    pcis_result = await db.pcis.insert_many(pcis_data)
    pci_ids = [str(id) for id in pcis_result.inserted_ids]
    
    # ==================== CREATE ASSESSMENTS ====================
    assessments_data = [
        {"name": "Oral Questions", "description": "Ask learners questions to assess understanding verbally"},
        {"name": "Written Exercise", "description": "Provide written tasks and worksheets to complete"},
        {"name": "Group Activity Observation", "description": "Observe learners working collaboratively in groups"},
        {"name": "Practical Task", "description": "Give hands-on activities to demonstrate understanding"},
        {"name": "Peer Assessment", "description": "Learners assess each other's work and provide feedback"},
        {"name": "Self-Assessment", "description": "Learners reflect on their own learning and progress"},
        {"name": "Projects and Presentations", "description": "Learners create and present work on topics learned"}
    ]
    assessments_result = await db.assessments.insert_many(assessments_data)
    assessment_ids = [str(id) for id in assessments_result.inserted_ids]
    
    # ==================== CREATE SLO MAPPINGS ====================
    all_slo_ids = whole_numbers_slo_ids + shapes_slo_ids + reading_slo_ids + plants_slo_ids
    
    # Create mappings for each SLO
    mappings_data = []
    for idx, slo_id in enumerate(all_slo_ids):
        mapping = {
            "sloId": slo_id,
            "competencyIds": [competency_ids[idx % len(competency_ids)], competency_ids[(idx + 1) % len(competency_ids)]],
            "valueIds": [value_ids[idx % len(value_ids)], value_ids[(idx + 2) % len(value_ids)]],
            "pciIds": [pci_ids[idx % len(pci_ids)]],
            "assessmentIds": [assessment_ids[idx % len(assessment_ids)], assessment_ids[(idx + 1) % len(assessment_ids)]]
        }
        mappings_data.append(mapping)
    
    await db.slo_mappings.insert_many(mappings_data)
    
    return {
        "success": True, 
        "message": "Comprehensive sample data seeded successfully",
        "summary": {
            "grades": len(grade_ids),
            "subjects": len(subject_ids),
            "strands": len(math_strand_ids) + len(english_strand_ids) + len(science_strand_ids),
            "substrands": len(numbers_substrand_ids) + len(geometry_substrand_ids) + len(reading_substrand_ids) + len(living_things_substrand_ids),
            "slos": len(all_slo_ids),
            "activities": len(activities_data),
            "competencies": len(competency_ids),
            "values": len(value_ids),
            "pcis": len(pci_ids),
            "assessments": len(assessment_ids),
            "slo_mappings": len(mappings_data)
        }
    }

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
