from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, Request, UploadFile, File
from fastapi.responses import JSONResponse, Response, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import time
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from bson.errors import InvalidId
import httpx
from io import BytesIO

# Import curriculum import utilities
from curriculum_import import (
    parse_csv_content, extract_curriculum_from_pdf, extract_curriculum_from_docx,
    generate_csv_template, rows_to_csv, CSV_TEMPLATE_HEADERS
)

# Import PDF generator
from pdf_generator import generate_lesson_plan_pdf

# Import Notes generator and PDF
from notes_generator import generate_notes_content
from notes_pdf import generate_notes_pdf

# Import Scheme of Work generator
from scheme_generator import (
    generate_scheme_pdf, get_lessons_per_week, get_assessment_for_slo,
    generate_inquiry_questions, generate_learning_experiences, generate_learning_resources
)

# Import lesson SLO service layer (legacy — kept for backward compat)
from lesson_slo_service import (
    sync_lesson_slos_for_substrand, regenerate_lesson_slos,
    get_active_lesson_slos, get_lesson_slo_for_slot, bootstrap_missing_lesson_slos,
)

# Import lesson SLO slot service (new — Phase 1-3)
from slot_service import (
    generate_slots_for_substrand, get_slots_for_substrand,
    get_slot, update_slot, clear_slot, get_slot_for_scheme,
    format_resource_display,
)

# Import production utilities
from app.production_utils import (
    ProductionLogger, IdempotencyManager, InputValidator, 
    RateLimiter, TransactionLock, get_user_error, SECURITY_HEADERS,
    SAFARICOM_IPS, MPESA_RESULT_CODES, get_mpesa_result_message,
    is_safaricom_ip, get_client_ip, RateLimitManager, RequestLogger,
    get_cors_origins, PRODUCTION_CORS_ORIGINS, DEVELOPMENT_CORS_ORIGINS
)

# ===========================================
# ENVIRONMENT CONFIGURATION
# ===========================================
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

# MongoDB connection - Support both naming conventions for flexibility
# MONGODB_URI is the standard name for external deployment (Railway, Render)
# MONGO_URL is the legacy name for local development
mongo_url = os.getenv('MONGODB_URI') or os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.getenv('DB_NAME', 'cbeplanner-oregon')

# Atlas requires certifi CA bundle for SSL; local MongoDB doesn't
import certifi
if 'mongodb+srv' in mongo_url or 'mongodb.net' in mongo_url:
    client = AsyncIOMotorClient(mongo_url, tlsCAFile=certifi.where())
else:
    client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Firebase project configuration from environment variables
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'cbeplanner')
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
if not FIREBASE_API_KEY:
    if os.getenv('ENVIRONMENT', 'development') == 'production':
        raise RuntimeError("FIREBASE_API_KEY environment variable is required")
    else:
        FIREBASE_API_KEY = 'AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8'  # dev-only fallback

# JWT Secret for additional security
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    if os.getenv('ENVIRONMENT', 'development') == 'production':
        raise RuntimeError("JWT_SECRET environment variable is required")
    else:
        JWT_SECRET = 'default-secret-change-in-production'  # dev-only fallback

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# ===========================================
# CORS CONFIGURATION
# ===========================================
# Get allowed origins from environment variable
cors_origins_str = os.getenv('CORS_ORIGINS', '')
if cors_origins_str:
    CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]
else:
    # Default origins for development
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:19006",
        "http://localhost:19000",
        "https://*.vercel.app",
        "https://magical-shannon-6.preview.emergentagent.com"
    ]

# ===========================================
# FASTAPI APPLICATION SETUP
# ===========================================
# FastAPI app with OpenAPI documentation
# Docs available at /api/docs (Swagger) and /api/redoc
ENABLE_DOCS = os.getenv('ENABLE_API_DOCS', 'true').lower() == 'true'

app = FastAPI(
    title="CBE Lesson Planner API",
    description="Competency-Based Education Lesson Planning System for Kenyan Teachers. \n\n"
                "## Features\n"
                "- User Authentication (Firebase)\n"
                "- Curriculum Management (Grades, Subjects, Strands, SLOs)\n"
                "- Lesson Plan Generation\n"
                "- M-Pesa Wallet Integration\n"
                "- Admin Panel\n\n"
                "## Authentication\n"
                "Most endpoints require Firebase ID token in the Authorization header:\n"
                "`Authorization: Bearer <firebase_id_token>`",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ===========================================
# PRODUCTION MIDDLEWARE
# ===========================================
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Add security headers
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)
        
        client_ip = get_client_ip(request)
        
        # Determine endpoint type for rate limit config
        path = request.url.path
        if "/auth/" in path:
            endpoint_type = "auth"
        elif "/payments/" in path:
            endpoint_type = "payment"
        elif "/admin/" in path:
            endpoint_type = "admin"
        else:
            endpoint_type = "default"
        
        # Check rate limit
        if RateLimitManager.is_rate_limited(client_ip, endpoint_type):
            retry_after = RateLimitManager.get_retry_after(client_ip, endpoint_type)
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": get_user_error("rate_limited"),
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        return await call_next(request)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests for monitoring"""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log if not excluded
        if RequestLogger.should_log(request.url.path):
            RequestLogger.log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                ip=get_client_ip(request)
            )
        
        return response

class GlobalErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler that catches unhandled exceptions
    and returns user-friendly error messages
    """
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            # Let FastAPI handle HTTP exceptions normally
            raise
        except Exception as e:
            # Log the actual error for debugging
            ProductionLogger.log_error(
                error_type="UNHANDLED_EXCEPTION",
                message=str(e),
                details={"path": str(request.url.path), "method": request.method}
            )
            # Return user-friendly error
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": get_user_error("server_error"),
                    "detail": "An unexpected error occurred. Please try again."
                }
            )

# Add custom middleware (order matters - first added = last executed)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(GlobalErrorHandlerMiddleware)

# Add CORS middleware with proper production origins
cors_origins = get_cors_origins(ENVIRONMENT) if ENVIRONMENT == "production" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# ===========================================
# HEALTH CHECK ENDPOINT
# ===========================================
@app.get("/health")
async def root_health_check():
    """Simple health check endpoint for Render"""
    return {"status": "ok"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for deployment platforms"""
    try:
        # Test database connection
        await client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "database": db_status,
        "version": "1.0.0"
    }

logger.info(f"Server starting in {ENVIRONMENT} mode")
logger.info(f"CORS origins: {CORS_ORIGINS if ENVIRONMENT == 'production' else 'All origins (development)'}")

# Helper to convert ObjectId to string
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

def validate_object_id(id_value: str, field_name: str = "ID") -> ObjectId:
    """Convert string to ObjectId, raising a clean 400 if invalid."""
    try:
        return ObjectId(id_value)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format. Please try again."
        )

def api_error(status_code: int, message: str, code: str = None) -> HTTPException:
    """Standardized API error response."""
    return HTTPException(
        status_code=status_code,
        detail={"success": False, "error": message, "code": code or "ERROR"}
    )

# ==================== MODELS ====================

# Lesson plan pricing constants
LESSON_PLAN_COST_KES = 2
NOTES_DOWNLOAD_COST_KES = 1
FREE_LESSONS_ON_SIGNUP = 5

class User(BaseModel):
    id: Optional[str] = None
    firebaseUid: str
    email: EmailStr
    firstName: str
    lastName: str
    schoolName: str = ""
    role: str = "teacher"  # teacher or admin or ADMIN
    walletBalance: float = 0.0
    freeLessonsRemaining: int = FREE_LESSONS_ON_SIGNUP  # New: 5 free lessons on signup
    freeLessonUsed: bool = False  # Legacy support
    freeNotesUsed: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class Wallet(BaseModel):
    """One wallet per user - stores current balance"""
    id: Optional[str] = None
    userId: str
    balance: float = 0.0
    currency: str = "KES"
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class WalletLedgerEntry(BaseModel):
    """Source of truth for all wallet transactions"""
    id: Optional[str] = None
    userId: str
    type: str  # CREDIT or DEBIT
    amount: float
    reference: str  # UNIQUE - prevents duplicate processing
    source: str  # MPESA, SYSTEM, LESSON_PLAN, etc.
    description: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class Payment(BaseModel):
    """Payment records with raw callback storage"""
    id: Optional[str] = None
    userId: str
    provider: str = "MPESA"
    providerRef: Optional[str] = None  # MpesaReceiptNumber or CheckoutRequestID
    amount: float
    currency: str = "KES"
    status: str = "PENDING"  # PENDING, SUCCESS, FAILED
    rawCallback: Optional[Dict[str, Any]] = None  # Store raw payload for auditing
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

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
    number_of_lessons: Optional[int] = None

class SubstrandLesson(BaseModel):
    id: Optional[str] = None
    substrand_id: str
    lesson_number: int
    specific_outcomes: List[str] = []

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

class LearningActivities(BaseModel):
    """Learning activities for a substrand - used in lesson plan generation"""
    id: Optional[str] = None
    substrandId: str
    introduction_activities: List[str] = []
    development_activities: List[str] = []
    conclusion_activities: List[str] = []
    extended_activities: List[str] = []
    learning_resources: List[str] = []
    assessment_methods: List[str] = []

class BulkCreateItem(BaseModel):
    name: str
    description: Optional[str] = None

class BulkCreateRequest(BaseModel):
    items: List[BulkCreateItem]
    parentId: str

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

# ==================== WALLET & M-PESA MODELS ====================

class WalletTransaction(BaseModel):
    """Wallet transaction ledger entry"""
    id: Optional[str] = None
    userId: str
    tx_ref: str  # Unique transaction reference
    mpesaReceiptNumber: Optional[str] = None
    checkoutRequestID: Optional[str] = None
    merchantRequestID: Optional[str] = None
    provider: str = "mpesa"
    type: str = "topup"  # topup, purchase, refund
    amount: float
    currency: str = "KES"
    phoneNumber: str
    status: str = "pending"  # pending, successful, failed
    resultCode: Optional[str] = None
    resultDesc: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class InitiatePaymentRequest(BaseModel):
    """Request to initiate M-Pesa STK Push"""
    phoneNumber: str
    amount: int  # Amount in KES (minimum 50)

class PaymentCallbackData(BaseModel):
    """M-Pesa callback data structure"""
    Body: Dict[str, Any]

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
                "freeLessonsRemaining": FREE_LESSONS_ON_SIGNUP,
                "freeLessonUsed": False,
                "freeNotesUsed": False,
                "createdAt": datetime.utcnow()
            }
            result = await db.users.insert_one(new_user)
            # Also create wallet entry
            await db.wallets.insert_one({
                "userId": str(result.inserted_id),
                "balance": 0.0,
                "currency": "KES",
                "updatedAt": datetime.utcnow()
            })
            user = await db.users.find_one({"_id": result.inserted_id})
        
        return serialize_doc(user)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=401, detail=f"Network error during token verification: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification error: {str(e)}")

# Admin emails from environment (comma-separated)
_admin_emails_env = os.getenv('ADMIN_EMAILS', 'mail2clive@gmail.com,testadmin2026@gmail.com')
ADMIN_EMAILS = {e.strip().lower() for e in _admin_emails_env.split(',') if e.strip()}

async def verify_admin(authorization: Optional[str] = Header(None)):
    """
    Verify that the user is the designated admin.
    This is enforced by email, not by role field.
    """
    user = await verify_token(authorization)
    user_email = user.get("email", "").lower().strip()
    
    if user_email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=403, 
            detail="Admin access denied. This action is restricted to authorized administrators only."
        )
    return user

# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/verify")
async def verify_user_token(request: TokenVerifyRequest):
    try:
        # Verify token using Google's Identity Toolkit API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={FIREBASE_API_KEY}",
                json={"idToken": request.idToken}
            )
            
            if response.status_code != 200:
                logger.error(f"Firebase verification failed: {response.status_code} - {response.text}")
                raise HTTPException(status_code=401, detail="Invalid token")
            
            data = response.json()
            if "users" not in data or len(data["users"]) == 0:
                logger.error(f"Firebase verification - no users in response: {data}")
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_data = data["users"][0]
            uid = user_data["localId"]
            email = user_data.get("email", "")
        
        is_new_user = False
        user = await db.users.find_one({"firebaseUid": uid})
        if not user:
            # Create new user with 5 FREE lessons on signup
            is_new_user = True
            new_user = {
                "firebaseUid": uid,
                "email": email,
                "firstName": request.firstName or "",
                "lastName": request.lastName or "",
                "schoolName": request.schoolName or "",
                "role": "teacher",
                "walletBalance": 0.0,
                "freeLessonsRemaining": FREE_LESSONS_ON_SIGNUP,
                "freeLessonUsed": False,
                "freeNotesUsed": False,
                "createdAt": datetime.utcnow()
            }
            result = await db.users.insert_one(new_user)
            user = await db.users.find_one({"_id": result.inserted_id})
            
            # Create wallet for new user
            wallet = {
                "userId": str(result.inserted_id),
                "balance": 0.0,
                "currency": "KES",
                "updatedAt": datetime.utcnow()
            }
            await db.wallets.insert_one(wallet)
            logger.info(f"New user created with {FREE_LESSONS_ON_SIGNUP} free lessons: {email}")
        else:
            # Ensure existing users have freeLessonsRemaining field
            if "freeLessonsRemaining" not in user:
                free_remaining = 0 if user.get("freeLessonUsed", True) else FREE_LESSONS_ON_SIGNUP
                await db.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"freeLessonsRemaining": free_remaining}}
                )
                user["freeLessonsRemaining"] = free_remaining
        
        return {"success": True, "user": serialize_doc(user), "isNewUser": is_new_user}
    except httpx.TimeoutException as e:
        logger.error(f"Firebase verification timeout: {str(e)}")
        raise HTTPException(status_code=504, detail="Token verification timed out. Please try again.")
    except httpx.HTTPError as e:
        logger.error(f"Firebase HTTP error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth verify error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))

@api_router.post("/auth/initialize-admin")
async def initialize_default_admin(request: Request):
    """Initialize default admin account — protected by bootstrap secret."""
    bootstrap_secret = os.getenv('ADMIN_BOOTSTRAP_SECRET', '')
    if not bootstrap_secret:
        raise HTTPException(status_code=503, detail="Admin initialization is disabled.")
    
    provided = request.headers.get('X-Bootstrap-Secret', '')
    if provided != bootstrap_secret:
        raise HTTPException(status_code=403, detail="Unauthorized.")
    
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

@api_router.get("/profile/is-admin")
async def check_is_admin(user: dict = Depends(verify_token)):
    """Check if current user is the designated admin"""
    user_email = user.get("email", "").lower().strip()
    is_admin = user_email in ADMIN_EMAILS
    return {"success": True, "isAdmin": is_admin}

# REMOVED: reset-free-trial endpoint - Free trial is one-time only on signup
# REMOVED: become-admin endpoint - Admin access is restricted to mail2clive@gmail.com only

# ===========================================
# M-PESA PAYMENT ENDPOINTS
# ===========================================

from mpesa_service import mpesa_service

@api_router.post("/payments/mpesa/initiate")
async def initiate_mpesa_payment(request: InitiatePaymentRequest, user: dict = Depends(verify_token)):
    """
    Initiate M-Pesa STK Push payment for wallet top-up
    
    - Rate limited to prevent abuse
    - Validates phone number and amount
    - Prevents duplicate requests using idempotency
    - Creates pending transaction in ledger
    - Sends STK Push to customer's phone
    - Returns checkout details for status polling
    """
    user_id = user["id"]
    
    # Rate limiting - max 5 payment initiations per minute per user
    rate_limit_key = f"mpesa_initiate:{user_id}"
    if not RateLimiter.check_rate_limit(rate_limit_key, max_requests=5, window_seconds=60):
        ProductionLogger.log_error("RATE_LIMIT", "Payment initiation rate limited", user_id)
        raise HTTPException(
            status_code=429, 
            detail=get_user_error("rate_limited")
        )
    
    # Validate phone number using InputValidator
    is_valid_phone, phone_result = InputValidator.validate_phone(request.phoneNumber)
    if not is_valid_phone:
        raise HTTPException(status_code=400, detail=phone_result)
    formatted_phone = phone_result
    
    # Validate amount using InputValidator
    is_valid_amount, amount_val, amount_error = InputValidator.validate_amount(
        request.amount, min_val=50, max_val=150000
    )
    if not is_valid_amount:
        raise HTTPException(status_code=400, detail=amount_error)
    
    # Idempotency check - prevent duplicate requests within 30 seconds
    idempotency_key = IdempotencyManager.generate_key(user_id, formatted_phone, request.amount, "initiate")
    if IdempotencyManager.check_and_mark(idempotency_key):
        ProductionLogger.log_error("DUPLICATE_REQUEST", "Duplicate payment initiation blocked", user_id)
        raise HTTPException(
            status_code=409, 
            detail=get_user_error("duplicate_action")
        )
    
    try:
        # Generate unique transaction reference
        tx_ref = mpesa_service.generate_tx_ref()
        
        # Log payment attempt
        ProductionLogger.log_payment_attempt(user_id, float(request.amount), formatted_phone, "INITIATING", tx_ref)
        
        # Create pending transaction in ledger FIRST (before calling M-Pesa)
        transaction = {
            "userId": user["id"],
            "tx_ref": tx_ref,
            "mpesaReceiptNumber": None,
            "checkoutRequestID": None,
            "merchantRequestID": None,
            "provider": "mpesa",
            "type": "topup",
            "amount": float(request.amount),
            "currency": "KES",
            "phoneNumber": formatted_phone,
            "status": "pending",
            "resultCode": None,
            "resultDesc": None,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert transaction
        result = await db.wallet_transactions.insert_one(transaction)
        transaction_id = str(result.inserted_id)
        
        logger.info(f"Created pending transaction {tx_ref} for user {user['id']}, amount: {request.amount}")
        
        # Now initiate STK Push
        try:
            stk_response = await mpesa_service.initiate_stk_push(
                phone_number=formatted_phone,
                amount=request.amount,
                account_reference=tx_ref,
                transaction_desc=f"CBE Planner Wallet Top Up"
            )
            
            if stk_response.get("success"):
                # Update transaction with M-Pesa response details
                await db.wallet_transactions.update_one(
                    {"_id": ObjectId(transaction_id)},
                    {
                        "$set": {
                            "checkoutRequestID": stk_response.get("checkoutRequestID"),
                            "merchantRequestID": stk_response.get("merchantRequestID"),
                            "updatedAt": datetime.utcnow()
                        }
                    }
                )
                
                return {
                    "success": True,
                    "message": "STK Push sent. Please enter your M-Pesa PIN.",
                    "transactionId": transaction_id,
                    "tx_ref": tx_ref,
                    "checkoutRequestID": stk_response.get("checkoutRequestID"),
                    "customerMessage": stk_response.get("customerMessage")
                }
            else:
                # Mark transaction as failed
                await db.wallet_transactions.update_one(
                    {"_id": ObjectId(transaction_id)},
                    {
                        "$set": {
                            "status": "failed",
                            "resultDesc": stk_response.get("error", "STK Push failed"),
                            "updatedAt": datetime.utcnow()
                        }
                    }
                )
                raise HTTPException(
                    status_code=400, 
                    detail=stk_response.get("error", "Failed to initiate payment")
                )
                
        except Exception as e:
            # Mark transaction as failed if STK Push fails
            await db.wallet_transactions.update_one(
                {"_id": ObjectId(transaction_id)},
                {
                    "$set": {
                        "status": "failed",
                        "resultDesc": str(e),
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            logger.error(f"STK Push failed for {tx_ref}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Payment initiation failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment system error. Please try again.")


@api_router.post("/payments/mpesa/callback")
async def mpesa_callback(request: Request, callback_data: PaymentCallbackData):
    """
    M-Pesa callback endpoint for payment confirmation
    
    - Validates shared secret (defense-in-depth)
    - Validates request comes from Safaricom IP
    - Receives payment result from M-Pesa
    - Stores raw callback payload for auditing
    - Verifies transaction exists and is pending
    - Updates transaction status
    - Creates wallet_ledger entry (source of truth)
    - Atomically updates wallet balance on success
    - Implements idempotency (ignores already processed transactions)
    """
    try:
        # Shared secret validation (defense-in-depth beyond IP check)
        callback_secret = os.getenv('MPESA_CALLBACK_SECRET', '')
        if callback_secret:
            provided_secret = request.headers.get('X-Callback-Secret', '')
            if provided_secret != callback_secret:
                logger.warning(f"M-Pesa callback rejected — invalid secret. IP: {get_client_ip(request)}")
                return {"ResultCode": 0, "ResultDesc": "Accepted"}
        
        # Get client IP and validate it's from Safaricom
        client_ip = get_client_ip(request)
        is_production = os.getenv('MPESA_ENV', 'sandbox') == 'production'
        
        if is_production and not is_safaricom_ip(client_ip):
            logger.warning(f"M-Pesa callback rejected - Invalid IP: {client_ip}")
            # Still return 200 to avoid retries, but log the rejection
            return {"ResultCode": 0, "ResultDesc": "Accepted"}
        
        logger.info(f"M-Pesa callback from IP: {client_ip}")
        
        body = callback_data.Body
        stk_callback = body.get("stkCallback", {})
        
        merchant_request_id = stk_callback.get("MerchantRequestID")
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")
        
        # Get user-friendly result message
        result_info = get_mpesa_result_message(result_code)
        
        logger.info(f"M-Pesa callback received: CheckoutRequestID={checkout_request_id}, ResultCode={result_code}, Status={result_info['status']}")
        
        # Find the transaction by checkoutRequestID
        transaction = await db.wallet_transactions.find_one({
            "checkoutRequestID": checkout_request_id
        })
        
        if not transaction:
            logger.warning(f"Transaction not found for CheckoutRequestID: {checkout_request_id}")
            return {"ResultCode": 0, "ResultDesc": "Accepted"}
        
        # Store raw callback for auditing
        await db.payments.insert_one({
            "userId": transaction["userId"],
            "provider": "MPESA",
            "providerRef": checkout_request_id,
            "amount": transaction["amount"],
            "currency": "KES",
            "status": "SUCCESS" if result_code == 0 else "FAILED",
            "resultCode": result_code,
            "resultStatus": result_info["status"],
            "resultMessage": result_info["message"],
            "rawCallback": body,  # Store full payload
            "clientIp": client_ip,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        })
        
        # Check if already processed (idempotency)
        if transaction.get("status") == "successful":
            logger.info(f"Transaction {transaction['tx_ref']} already processed, skipping")
            return {"ResultCode": 0, "ResultDesc": "Accepted"}
        
        if result_code == 0:
            # Payment successful - extract callback metadata
            callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            
            mpesa_receipt = None
            amount = None
            phone = None
            
            for item in callback_metadata:
                name = item.get("Name")
                value = item.get("Value")
                if name == "MpesaReceiptNumber":
                    mpesa_receipt = value
                elif name == "Amount":
                    amount = float(value)
                elif name == "PhoneNumber":
                    phone = str(value)
            
            # Create UNIQUE ledger reference
            ledger_ref = f"MPESA-{mpesa_receipt or checkout_request_id}"
            
            # Check if ledger entry already exists (idempotency)
            existing_ledger = await db.wallet_ledger.find_one({"reference": ledger_ref})
            if existing_ledger:
                logger.info(f"Ledger entry {ledger_ref} already exists, skipping")
                return {"ResultCode": 0, "ResultDesc": "Accepted"}
            
            # ATOMIC: Update transaction status to successful FIRST
            update_result = await db.wallet_transactions.update_one(
                {
                    "_id": transaction["_id"],
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "successful",
                        "mpesaReceiptNumber": mpesa_receipt,
                        "resultCode": str(result_code),
                        "resultDesc": result_desc,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            
            # Only create ledger entry and update wallet if transaction was updated
            if update_result.modified_count > 0:
                # Create wallet_ledger entry (SOURCE OF TRUTH)
                try:
                    await db.wallet_ledger.insert_one({
                        "userId": transaction["userId"],
                        "type": "CREDIT",
                        "amount": transaction["amount"],
                        "reference": ledger_ref,
                        "source": "MPESA",
                        "description": f"M-Pesa top-up. Receipt: {mpesa_receipt}",
                        "createdAt": datetime.utcnow()
                    })
                except Exception as e:
                    # Duplicate reference - already processed
                    logger.warning(f"Ledger entry already exists: {ledger_ref}")
                    return {"ResultCode": 0, "ResultDesc": "Accepted"}
                
                # Atomically increment wallet balance
                await db.users.update_one(
                    {"_id": ObjectId(transaction["userId"])},
                    {"$inc": {"walletBalance": transaction["amount"]}}
                )
                
                # Also update wallets collection
                await db.wallets.update_one(
                    {"userId": transaction["userId"]},
                    {
                        "$inc": {"balance": transaction["amount"]},
                        "$set": {"updatedAt": datetime.utcnow()}
                    },
                    upsert=True
                )
                
                logger.info(f"Wallet credited {transaction['amount']} KES for user {transaction['userId']}, receipt: {mpesa_receipt}")
            else:
                logger.info(f"Transaction {transaction['tx_ref']} already processed (concurrent request)")
        else:
            # Payment failed or cancelled - store detailed result info
            await db.wallet_transactions.update_one(
                {"_id": transaction["_id"]},
                {
                    "$set": {
                        "status": "failed",
                        "resultCode": str(result_code),
                        "resultDesc": result_desc,
                        "resultStatus": result_info["status"],
                        "resultMessage": result_info["message"],
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            logger.info(f"Transaction {transaction['tx_ref']} {result_info['status']}: {result_info['message']} (Code: {result_code})")
        
        return {"ResultCode": 0, "ResultDesc": "Accepted"}
        
    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"ResultCode": 0, "ResultDesc": "Accepted"}


@api_router.get("/payments/mpesa/status/{checkout_request_id}")
async def check_payment_status(checkout_request_id: str, user: dict = Depends(verify_token)):
    """
    Check payment status by polling M-Pesa or local database
    
    - First checks local database for status
    - If still pending, queries M-Pesa for status
    - Updates local status if M-Pesa confirms success
    """
    try:
        # First check our database
        transaction = await db.wallet_transactions.find_one({
            "checkoutRequestID": checkout_request_id,
            "userId": user["id"]
        })
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # If already processed, return status from database
        if transaction.get("status") in ["successful", "failed"]:
            return {
                "success": True,
                "status": transaction["status"],
                "tx_ref": transaction["tx_ref"],
                "amount": transaction["amount"],
                "mpesaReceiptNumber": transaction.get("mpesaReceiptNumber"),
                "resultDesc": transaction.get("resultDesc"),
                "message": "Payment successful!" if transaction["status"] == "successful" else transaction.get("resultDesc", "Payment failed")
            }
        
        # If pending, query M-Pesa for status
        try:
            query_result = await mpesa_service.query_stk_status(checkout_request_id)
            
            if query_result.get("status") == "successful":
                # Update transaction and wallet
                update_result = await db.wallet_transactions.update_one(
                    {
                        "_id": transaction["_id"],
                        "status": "pending"
                    },
                    {
                        "$set": {
                            "status": "successful",
                            "resultDesc": query_result.get("resultDesc"),
                            "updatedAt": datetime.utcnow()
                        }
                    }
                )
                
                if update_result.modified_count > 0:
                    await db.users.update_one(
                        {"_id": ObjectId(transaction["userId"])},
                        {"$inc": {"walletBalance": transaction["amount"]}}
                    )
                    logger.info(f"Wallet credited via query for {transaction['tx_ref']}")
                
                # Refresh user profile
                updated_user = await db.users.find_one({"_id": ObjectId(user["id"])})
                
                return {
                    "success": True,
                    "status": "successful",
                    "tx_ref": transaction["tx_ref"],
                    "amount": transaction["amount"],
                    "newBalance": updated_user.get("walletBalance", 0),
                    "message": "Payment successful! Wallet has been credited."
                }
                
            elif query_result.get("status") in ["failed", "cancelled", "timeout"]:
                await db.wallet_transactions.update_one(
                    {"_id": transaction["_id"]},
                    {
                        "$set": {
                            "status": "failed",
                            "resultDesc": query_result.get("resultDesc"),
                            "updatedAt": datetime.utcnow()
                        }
                    }
                )
                
                return {
                    "success": False,
                    "status": query_result.get("status"),
                    "tx_ref": transaction["tx_ref"],
                    "message": query_result.get("resultDesc", "Payment was not completed")
                }
            else:
                # Still pending
                return {
                    "success": True,
                    "status": "pending",
                    "tx_ref": transaction["tx_ref"],
                    "message": "Payment is still being processed. Please wait..."
                }
                
        except Exception as e:
            logger.error(f"Error querying M-Pesa status: {str(e)}")
            return {
                "success": True,
                "status": "pending",
                "tx_ref": transaction["tx_ref"],
                "message": "Payment is being processed. Please wait..."
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking payment status")


@api_router.get("/payments/transactions")
async def get_user_transactions(
    limit: int = 20,
    offset: int = 0,
    user: dict = Depends(verify_token)
):
    """Get user's wallet transaction history"""
    transactions = await db.wallet_transactions.find(
        {"userId": user["id"]}
    ).sort("createdAt", -1).skip(offset).limit(limit).to_list(limit)
    
    total = await db.wallet_transactions.count_documents({"userId": user["id"]})
    
    return {
        "success": True,
        "transactions": [serialize_doc(t) for t in transactions],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@api_router.get("/wallet/balance")
async def get_wallet_balance(user: dict = Depends(verify_token)):
    """Lightweight endpoint to fetch current wallet balance only."""
    user_doc = await db.users.find_one({"_id": ObjectId(user["id"])})
    if not user_doc:
        return {"success": True, "balance": 0, "freeLessonsRemaining": 0, "currency": "KES"}
    
    return {
        "success": True,
        "balance": float(user_doc.get("walletBalance", 0)),
        "freeLessonsRemaining": user_doc.get("freeLessonsRemaining", 0),
        "currency": "KES"
    }


# ===========================================
# ADMIN WALLET/PAYMENT ENDPOINTS
# ===========================================

@api_router.get("/admin/wallet-transactions")
async def admin_get_transactions(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    userId: Optional[str] = None,
    user: dict = Depends(verify_token)
):
    """Admin: Get all wallet transactions with filtering"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = {}
    if status:
        query["status"] = status
    if userId:
        query["userId"] = userId
    
    transactions = await db.wallet_transactions.find(query)\
        .sort("createdAt", -1)\
        .skip(offset)\
        .limit(limit)\
        .to_list(limit)
    
    total = await db.wallet_transactions.count_documents(query)
    
    # Calculate totals
    successful_pipeline = [
        {"$match": {"status": "successful", **({} if not userId else {"userId": userId})}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    successful_stats = await db.wallet_transactions.aggregate(successful_pipeline).to_list(1)
    
    return {
        "success": True,
        "transactions": [serialize_doc(t) for t in transactions],
        "total": total,
        "limit": limit,
        "offset": offset,
        "stats": {
            "successfulAmount": successful_stats[0]["total"] if successful_stats else 0,
            "successfulCount": successful_stats[0]["count"] if successful_stats else 0
        }
    }


@api_router.get("/admin/wallet-reconciliation")
async def admin_reconciliation(
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    user: dict = Depends(verify_token)
):
    """Admin: Wallet reconciliation report"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    match_query = {"status": "successful"}
    
    if startDate:
        match_query["createdAt"] = {"$gte": datetime.fromisoformat(startDate)}
    if endDate:
        if "createdAt" in match_query:
            match_query["createdAt"]["$lte"] = datetime.fromisoformat(endDate)
        else:
            match_query["createdAt"] = {"$lte": datetime.fromisoformat(endDate)}
    
    # Aggregate by day
    pipeline = [
        {"$match": match_query},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$createdAt"}
                },
                "totalAmount": {"$sum": "$amount"},
                "transactionCount": {"$sum": 1}
            }
        },
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ]
    
    daily_stats = await db.wallet_transactions.aggregate(pipeline).to_list(30)
    
    # Total wallet balances
    wallet_pipeline = [
        {"$group": {"_id": None, "totalBalance": {"$sum": "$walletBalance"}, "userCount": {"$sum": 1}}}
    ]
    wallet_stats = await db.users.aggregate(wallet_pipeline).to_list(1)
    
    return {
        "success": True,
        "dailyStats": daily_stats,
        "totalWalletBalance": wallet_stats[0]["totalBalance"] if wallet_stats else 0,
        "totalUsers": wallet_stats[0]["userCount"] if wallet_stats else 0

    }


@api_router.get("/grades")
async def get_grades(user: dict = Depends(verify_token)):
    grades = await db.grades.find().sort("order", 1).to_list(100)
    return {"success": True, "grades": [serialize_doc(g) for g in grades]}

@api_router.get("/subjects")
async def get_subjects(gradeId: str, user: dict = Depends(verify_token)):
    # Sort subjects alphabetically by name for user convenience
    subjects = await db.subjects.find({"gradeIds": gradeId}).sort("name", 1).to_list(100)
    return {"success": True, "subjects": [serialize_doc(s) for s in subjects]}

@api_router.get("/strands")
async def get_strands(subjectId: str, user: dict = Depends(verify_token)):
    # NO SORTING - preserve curriculum teaching order (insertion order)
    strands = await db.strands.find({"subjectId": subjectId}).to_list(100)
    return {"success": True, "strands": [serialize_doc(s) for s in strands]}

@api_router.get("/substrands")
async def get_substrands(strandId: str, user: dict = Depends(verify_token)):
    logger.info(f"[SUBSTRANDS] Fetching substrands for strandId: {strandId}")
    # NO SORTING - preserve curriculum teaching order (insertion order)
    substrands = await db.substrands.find({"strandId": strandId}).to_list(100)
    logger.info(f"[SUBSTRANDS] Found {len(substrands)} substrands for strandId: {strandId}")
    return {"success": True, "substrands": [serialize_doc(s) for s in substrands]}

@api_router.get("/slos")
async def get_slos(substrandId: str, user: dict = Depends(verify_token)):
    # NO SORTING - preserve curriculum teaching order (insertion order)
    slos = await db.slos.find({"substrandId": substrandId}).to_list(100)
    return {"success": True, "slos": [serialize_doc(s) for s in slos]}

@api_router.post("/lesson-plans/generate")
async def generate_lesson_plan(request: GenerateLessonRequest, user: dict = Depends(verify_token)):
    """
    Generate a lesson plan with payment logic:
    - First 5 lessons are FREE (tracked via freeLessonsRemaining)
    - After that, each lesson costs KES 2
    - Wallet balance must be sufficient, no negative balances allowed
    - Protected against duplicate submissions and race conditions
    """
    logger.info(f"[LESSON PLAN] Starting generation for user {user.get('id')}")
    logger.info(f"[LESSON PLAN] Request: grade={request.gradeId}, subject={request.subjectId}, strand={request.strandId}, substrand={request.substrandId}, slo={request.sloId}")
    
    user_id = user["id"]
    
    # Rate limiting - max 10 lesson generations per minute
    rate_limit_key = f"lesson_gen:{user_id}"
    if not RateLimiter.check_rate_limit(rate_limit_key, max_requests=10, window_seconds=60):
        ProductionLogger.log_error("RATE_LIMIT", "Lesson generation rate limited", user_id)
        raise HTTPException(
            status_code=429, 
            detail=get_user_error("rate_limited")
        )
    
    # Acquire transaction lock to prevent race conditions
    lock_key = f"lesson_gen_lock:{user_id}"
    if not TransactionLock.acquire(lock_key):
        raise HTTPException(
            status_code=409, 
            detail="A lesson generation is already in progress. Please wait."
        )
    
    try:
        free_remaining = user.get("freeLessonsRemaining", 0)
        wallet_balance = user.get("walletBalance", 0.0)
    
        # Check if user has free lessons or sufficient balance
        if free_remaining > 0:
            # Use free lesson - decrement counter
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": {"freeLessonsRemaining": -1}}
            )
            logger.info(f"User {user_id} used free lesson. Remaining: {free_remaining - 1}")
        else:
            # Charge KES 2 from wallet
            if wallet_balance < LESSON_PLAN_COST_KES:
                raise HTTPException(
                    status_code=402, 
                    detail=f"Insufficient wallet balance. You need KES {LESSON_PLAN_COST_KES} to generate a lesson plan. Current balance: KES {wallet_balance}"
                )
            
            # Atomic deduction with wallet ledger entry
            import uuid
            ledger_ref = f"LESSON-{uuid.uuid4().hex[:12].upper()}"
            
            # Create ledger entry FIRST (source of truth)
            ledger_entry = {
                "userId": user_id,
                "type": "DEBIT",
                "amount": LESSON_PLAN_COST_KES,
                "reference": ledger_ref,
                "source": "LESSON_PLAN",
                "description": f"Lesson plan generation",
                "createdAt": datetime.utcnow()
            }
            
            try:
                await db.wallet_ledger.insert_one(ledger_entry)
            except Exception as e:
                # Duplicate reference - shouldn't happen but handle it
                logger.error(f"Ledger entry failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Payment processing error")
            
            # Atomically decrement wallet balance
            result = await db.users.update_one(
                {"_id": ObjectId(user_id), "walletBalance": {"$gte": LESSON_PLAN_COST_KES}},
                {"$inc": {"walletBalance": -LESSON_PLAN_COST_KES}}
            )
            
            if result.modified_count == 0:
                # Rollback ledger entry if balance update failed
                await db.wallet_ledger.delete_one({"reference": ledger_ref})
                raise HTTPException(status_code=402, detail="Insufficient wallet balance")
            
            logger.info(f"User {user_id} charged KES {LESSON_PLAN_COST_KES} for lesson plan. Ref: {ledger_ref}")
            
            # Sync wallets collection
            await db.wallets.update_one(
                {"userId": user_id},
                {"$inc": {"balance": -LESSON_PLAN_COST_KES}, "$set": {"updatedAt": datetime.utcnow()}},
                upsert=True
            )
        
        # Content generation follows — if it fails after charge, refund is handled at the end
        _charged_wallet = free_remaining <= 0
        
        # Fetch all related data
        grade = await db.grades.find_one({"_id": ObjectId(request.gradeId)})
        subject = await db.subjects.find_one({"_id": ObjectId(request.subjectId)})
        strand = await db.strands.find_one({"_id": ObjectId(request.strandId)})
        substrand = await db.substrands.find_one({"_id": ObjectId(request.substrandId)})
        slo = await db.slos.find_one({"_id": ObjectId(request.sloId)})
        
        logger.info(f"[LESSON PLAN] Data lookup: grade={grade is not None}, subject={subject is not None}, strand={strand is not None}, substrand={substrand is not None}, slo={slo is not None}")
        
        if not all([grade, subject, strand, substrand, slo]):
            missing = [name for name, val in [
                ("grade", grade), ("subject", subject),
                ("strand", strand), ("sub-strand", substrand), ("learning outcome", slo)
            ] if not val]
            logger.error(f"[LESSON PLAN] Missing data: {missing}")
            raise HTTPException(status_code=404, detail=f"Could not find {', '.join(missing)}. Please go back and re-select your topic.")
        
        # Get activities for this strand/substrand
        activities = await db.activities.find({
            "strandId": request.strandId,
            "substrandId": request.substrandId
        }).to_list(100)
        
        # Initialize competencies, values, PCIs, assessments
        competencies = []
        values = []
        pcis = []
        assessments = []
        inquiry_questions = []
        
        # APPROACH 1: Get from SLO mappings (old format)
        mapping = await db.slo_mappings.find_one({"sloId": request.sloId})
        
        if mapping:
            if mapping.get("competencyIds"):
                comp_docs = await db.competencies.find({
                    "_id": {"$in": [ObjectId(cid) for cid in mapping["competencyIds"]]}
                }).to_list(100)
                competencies = [{"name": c["name"], "description": c.get("description", c["name"])} for c in comp_docs]
            
            if mapping.get("valueIds"):
                val_docs = await db.values.find({
                    "_id": {"$in": [ObjectId(vid) for vid in mapping["valueIds"]]}
                }).to_list(100)
                values = [{"name": v["name"], "description": v.get("description", v["name"])} for v in val_docs]
            
            if mapping.get("pciIds"):
                pci_docs = await db.pcis.find({
                    "_id": {"$in": [ObjectId(pid) for pid in mapping["pciIds"]]}
                }).to_list(100)
                pcis = [{"name": p["name"], "description": p.get("description", p["name"])} for p in pci_docs]
            
            if mapping.get("assessmentIds"):
                assess_docs = await db.assessments.find({
                    "_id": {"$in": [ObjectId(aid) for aid in mapping["assessmentIds"]]}
                }).to_list(100)
                assessments = [{"name": a["name"], "description": a.get("description", a["name"])} for a in assess_docs]
        
        # Fetch specific learning activities for this substrand/SLO
        # Try multiple query approaches to handle different data formats
        learning_activities_doc = None
        
        # Try by substrandId (string)
        learning_activities_doc = await db.learning_activities.find_one({"substrandId": request.substrandId})
        
        # Try by sloId (string) if not found
        if not learning_activities_doc:
            learning_activities_doc = await db.learning_activities.find_one({"sloId": request.sloId})
        
        # Try by substrandId (ObjectId) if not found
        if not learning_activities_doc:
            try:
                learning_activities_doc = await db.learning_activities.find_one({"substrandId": ObjectId(request.substrandId)})
            except:
                pass
        
        # Try by sloId (ObjectId) if not found
        if not learning_activities_doc:
            try:
                learning_activities_doc = await db.learning_activities.find_one({"sloId": ObjectId(request.sloId)})
            except:
                pass
        
        # Extract specific activities or use defaults
        intro_activities = []
        dev_activities = []
        conclusion_activities = []
        extended_activities_list = []
        specific_resources = []
        specific_assessments = []
        
        if learning_activities_doc:
            # Support both old format (introduction_activities) and new format (introduction)
            intro_activities = learning_activities_doc.get("introduction_activities", [])
            if not intro_activities:
                intro_text = learning_activities_doc.get("introduction", "")
                if intro_text:
                    intro_activities = [a.strip() for a in intro_text.split(",") if a.strip()]
            
            dev_activities = learning_activities_doc.get("development_activities", [])
            if not dev_activities:
                dev_text = learning_activities_doc.get("development", "")
                if dev_text:
                    dev_activities = [a.strip() for a in dev_text.split(",") if a.strip()]
            
            conclusion_activities = learning_activities_doc.get("conclusion_activities", [])
            if not conclusion_activities:
                conclusion_text = learning_activities_doc.get("conclusion", "")
                if conclusion_text:
                    conclusion_activities = [a.strip() for a in conclusion_text.split(",") if a.strip()]
            
            extended_activities_list = learning_activities_doc.get("extended_activities", [])
            specific_resources = learning_activities_doc.get("learning_resources", [])
            specific_assessments = learning_activities_doc.get("assessment_methods", [])
            
            # APPROACH 2: Get competencies, values, PCIs from learning_activities if not already set
            # (This handles Grade 9 data where these are embedded in the learning_activities)
            if not competencies:
                embedded_competencies = learning_activities_doc.get("core_competencies", [])
                if embedded_competencies:
                    competencies = [{"name": c, "description": c} for c in embedded_competencies]
            
            if not values:
                embedded_values = learning_activities_doc.get("values", [])
                if embedded_values:
                    values = [{"name": v, "description": v} for v in embedded_values]
            
            if not pcis:
                embedded_pcis = learning_activities_doc.get("pci", []) or learning_activities_doc.get("pcis", [])
                if embedded_pcis:
                    pcis = [{"name": p, "description": p} for p in embedded_pcis]
            
            # Get inquiry questions if available
            inquiry_questions = learning_activities_doc.get("inquiry_questions", [])
        
        # APPROACH 3: If still no competencies/values/PCIs, use defaults based on subject
        if not competencies:
            competencies = [
                {"name": "Communication and Collaboration", "description": "Learners communicate effectively and work together"},
                {"name": "Critical Thinking and Problem Solving", "description": "Learners analyze information and solve problems"}
            ]
        
        if not values:
            values = [
                {"name": "Responsibility", "description": "Taking ownership of one's actions and duties"},
                {"name": "Respect", "description": "Showing consideration for others"}
            ]
        
        if not pcis:
            pcis = [
                {"name": "Life Skills", "description": "Skills for everyday living and decision making"}
            ]
        
        # Duration-aware content generation
        duration = request.duration
        
        # Classify SLOs by domain
        knowledge = [f"Understand {slo['name']}", f"Recall key concepts of {substrand['name']}"]
        skills = [f"Apply {substrand['name']} concepts", f"Demonstrate understanding of {slo['name']}"]
        attitudes = ["Show curiosity and interest", "Develop positive learning habits"]
        
        # Duration-based content depth - using specific activities from database
        if duration <= 40:
            # Short lesson (25-40 min): Brief, focused
            intro_time = 5
            dev_time = duration - 15
            conclusion_time = 5
            assessment_time = 5
            
            # Use specific activities if available
            if intro_activities:
                introduction = f"Introduction ({intro_time} min):\n• " + "\n• ".join(intro_activities[:2])
            else:
                introduction = f"Teacher introduces {substrand['name']} ({intro_time} min). Learners share what they know about the topic."
            
            if dev_activities:
                lesson_development = f"Lesson Development ({dev_time} min):\n• " + "\n• ".join(dev_activities[:2])
            else:
                lesson_development = f"Teacher explains {slo['name']} with examples ({dev_time} min). " + \
                                   f"Learners participate in: {activities[0]['description'] if activities else 'guided practice'}."
            
            if extended_activities_list:
                extended_activity = f"Extended Activity:\n• " + extended_activities_list[0]
            else:
                extended_activity = ""
            
            if conclusion_activities:
                conclusion = f"Conclusion ({conclusion_time} min):\n• " + "\n• ".join(conclusion_activities[:1])
            else:
                conclusion = f"Teacher summarizes key points ({conclusion_time} min). Learners reflect on learning."
            
            if specific_assessments:
                assessment_text = f"Assessment ({assessment_time} min): " + "; ".join(specific_assessments[:2])
            else:
                assessment_text = f"Quick assessment ({assessment_time} min): " + \
                                (assessments[0]['description'] if assessments else "Oral questions and observation")
        
        elif duration <= 60:
            # Medium lesson (45-60 min): Moderate depth
            intro_time = 7
            dev_time = int((duration - 20) * 0.6)
            ext_time = int((duration - 20) * 0.4)
            conclusion_time = 8
            assessment_time = 5
            
            # Use specific activities if available
            if intro_activities:
                introduction = f"Introduction ({intro_time} min):\n• " + "\n• ".join(intro_activities[:3])
            else:
                introduction = f"Teacher introduces {substrand['name']} with real-life examples ({intro_time} min). " + \
                              "Learners brainstorm and share prior knowledge."
            
            if dev_activities:
                lesson_development = f"Lesson Development ({dev_time} min):\n• " + "\n• ".join(dev_activities[:3])
            else:
                lesson_development = f"Teacher explains {slo['name']} in detail ({dev_time} min). " + \
                                   f"Learners engage in: {', '.join([a['description'] for a in activities[:2]]) if activities else 'guided activities'}."
            
            if extended_activities_list:
                extended_activity = f"Extended Activities ({ext_time} min):\n• " + "\n• ".join(extended_activities_list[:2])
            else:
                extended_activity = f"Group work ({ext_time} min): Learners work in small groups on practical tasks related to {substrand['name']}."
            
            if conclusion_activities:
                conclusion = f"Conclusion ({conclusion_time} min):\n• " + "\n• ".join(conclusion_activities[:2])
            else:
                conclusion = f"Class discussion and summary ({conclusion_time} min). Learners present findings and reflect."
            
            if specific_assessments:
                assessment_text = f"Assessment ({assessment_time} min): " + "; ".join(specific_assessments[:3])
            else:
                assessment_text = f"Assessment ({assessment_time} min): " + \
                                ('; '.join([a['description'] for a in assessments[:2]]) if assessments else "Oral questions, written tasks, and observation")
        
        else:
            # Long lesson (65-80 min): Comprehensive
            intro_time = 10
            dev_time = int((duration - 25) * 0.45)
            ext_time = int((duration - 25) * 0.35)
            conclusion_time = 10
            assessment_time = int((duration - 25) * 0.20)
            
            # Use specific activities if available
            if intro_activities:
                introduction = f"Comprehensive Introduction ({intro_time} min):\n• " + "\n• ".join(intro_activities)
            else:
                introduction = f"Comprehensive introduction to {substrand['name']} ({intro_time} min). " + \
                              "Teacher uses multimedia/real objects. Learners engage in discussion and pre-assessment."
            
            if dev_activities:
                lesson_development = f"Detailed Lesson Development ({dev_time} min):\n• " + "\n• ".join(dev_activities)
            else:
                lesson_development = f"Detailed explanation of {slo['name']} with multiple examples ({dev_time} min). " + \
                                   f"Learners participate in: {', '.join([a['description'] for a in activities[:3]]) if activities else 'various guided activities'}."
            
            if extended_activities_list:
                extended_activity = f"Extended Activities and Projects ({ext_time} min):\n• " + "\n• ".join(extended_activities_list)
            else:
                extended_activity = f"Extended group work and differentiated activities ({ext_time} min): " + \
                                  f"Learners explore {substrand['name']} through projects, experiments, or research. Teacher provides individualized support."
            
            if conclusion_activities:
                conclusion = f"Comprehensive Conclusion ({conclusion_time} min):\n• " + "\n• ".join(conclusion_activities)
            else:
                conclusion = f"Comprehensive review and reflection ({conclusion_time} min). " + \
                            "Group presentations, peer feedback, and teacher summary."
            
            if specific_assessments:
                assessment_text = f"Comprehensive Assessment ({assessment_time} min): " + "; ".join(specific_assessments)
            else:
                assessment_text = f"Comprehensive assessment ({assessment_time} min): " + \
                                ('; '.join([a['description'] for a in assessments]) if assessments else \
                                 "Multiple methods - oral questions, written tasks, practical demonstrations, peer assessment")
        
        # Use specific resources if available, otherwise use defaults
        if specific_resources:
            learning_resources = specific_resources
        else:
            learning_resources = ["Textbooks", "Charts and diagrams", "Real objects/models", "Digital resources"]
        
        # Create lesson plan with teacher info from profile
        # ── Attach lesson-specific data from lesson_slo_slots (primary) ──
        lesson_specific_outcomes = []
        substrand_lesson_number = None
        slot_resources = []
        slot_inquiry = ""
        num_lessons = substrand.get("number_of_lessons")

        if num_lessons and num_lessons >= 1:
            existing_count = await db.lesson_plans.count_documents({
                "teacherId": user["id"],
                "substrandId": request.substrandId,
            })
            target_idx = existing_count % num_lessons  # 0-based slot_index
            substrand_lesson_number = target_idx + 1

            # Priority 1: lesson_slo_slots (new system)
            slot = await get_slot_for_scheme(db, request.substrandId, target_idx)
            if slot and slot.get("outcome"):
                lesson_specific_outcomes = [slot["outcome"]]
                if slot.get("description"):
                    lesson_specific_outcomes.append(slot["description"])
                slot_resources = slot.get("formatted_resources", [])
                slot_inquiry = slot.get("key_inquiry_question", "")
            else:
                # Priority 2: legacy substrand_lessons
                sl = await db.substrand_lessons.find_one({
                    "substrand_id": request.substrandId,
                    "lesson_number": substrand_lesson_number,
                })
                if sl and sl.get("specific_outcomes"):
                    lesson_specific_outcomes = sl["specific_outcomes"]

        # Merge slot resources into lesson resources
        if slot_resources:
            learning_resources = slot_resources

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
            "sloDescription": slo.get("description", ""),
            "knowledge": knowledge,
            "skills": skills,
            "attitudes": attitudes,
            "learningResources": learning_resources,
            "competencies": competencies,
            "values": values,
            "pcis": pcis,
            "inquiryQuestions": inquiry_questions,
            "introduction": introduction,
            "lessonDevelopment": lesson_development,
            "extendedActivity": extended_activity,
            "conclusion": conclusion,
            "assessment": assessment_text,
            "lessonSpecificOutcomes": lesson_specific_outcomes,
            "lessonNumber": substrand_lesson_number,
            "totalLessonsInSubstrand": num_lessons,
            "createdAt": datetime.utcnow(),
            "expiresAt": datetime.utcnow() + timedelta(days=2)
        }
        
        result = await db.lesson_plans.insert_one(lesson_plan)
        # Remove MongoDB _id and add string id
        if "_id" in lesson_plan:
            del lesson_plan["_id"]
        lesson_plan["id"] = str(result.inserted_id)
        # Convert datetime to ISO string for JSON serialization
        lesson_plan["createdAt"] = lesson_plan["createdAt"].isoformat()
        if "expiresAt" in lesson_plan:
            lesson_plan["expiresAt"] = lesson_plan["expiresAt"].isoformat()
        
        # Log successful generation
        ProductionLogger.log_critical_action("LESSON_PLAN_GENERATED", user_id, {
            "lesson_plan_id": lesson_plan["id"],
            "grade": lesson_plan["gradeName"],
            "subject": lesson_plan["subjectName"],
            "used_free": free_remaining > 0
        })
        
        return {"success": True, "lessonPlan": lesson_plan}
    
    except HTTPException:
        raise
    except Exception as e:
        # Refund if wallet was charged and content generation failed
        if free_remaining <= 0:
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": {"walletBalance": LESSON_PLAN_COST_KES}}
            )
            await db.wallets.update_one(
                {"userId": user_id},
                {"$inc": {"balance": LESSON_PLAN_COST_KES}, "$set": {"updatedAt": datetime.utcnow()}}
            )
            await db.wallet_ledger.delete_one({"reference": ledger_ref})
            logger.warning(f"Lesson plan failed post-charge, refunded user {user_id}. Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate lesson plan. Your payment has been refunded." if free_remaining <= 0
                   else "Failed to generate lesson plan. Please try again."
        )
    
    finally:
        # Always release the lock
        TransactionLock.release(lock_key)

@api_router.get("/lesson-plans")
async def get_lesson_plans(user: dict = Depends(verify_token)):
    """Get all lesson plans for the user, excluding expired ones"""
    current_time = datetime.utcnow()
    
    # Filter out expired plans (plans with expiresAt in the past)
    # Also include plans without expiresAt field (legacy plans)
    plans = await db.lesson_plans.find({
        "teacherId": user["id"],
        "$or": [
            {"expiresAt": {"$gt": current_time}},
            {"expiresAt": {"$exists": False}}
        ]
    }).sort("createdAt", -1).to_list(100)
    
    # Add daysRemaining to each plan
    serialized_plans = []
    for plan in plans:
        doc = serialize_doc(plan)
        if "expiresAt" in plan and plan["expiresAt"]:
            days_remaining = (plan["expiresAt"] - current_time).days
            doc["daysRemaining"] = max(0, days_remaining)
            doc["expiresAt"] = plan["expiresAt"].isoformat()
        else:
            doc["daysRemaining"] = None  # Legacy plan, no expiration
        serialized_plans.append(doc)
    
    return {"success": True, "lessonPlans": serialized_plans}

@api_router.get("/lesson-plans/{plan_id}")
async def get_lesson_plan_by_id(plan_id: str, user: dict = Depends(verify_token)):
    """Get a single lesson plan by ID"""
    try:
        plan = await db.lesson_plans.find_one({
            "_id": ObjectId(plan_id),
            "teacherId": user["id"]
        })
        
        if not plan:
            raise HTTPException(status_code=404, detail="Lesson plan not found")
        
        # Check if expired
        current_time = datetime.utcnow()
        if "expiresAt" in plan and plan["expiresAt"] and plan["expiresAt"] < current_time:
            raise HTTPException(status_code=410, detail="This lesson plan has expired and is no longer available")
        
        doc = serialize_doc(plan)
        if "expiresAt" in plan and plan["expiresAt"]:
            days_remaining = (plan["expiresAt"] - current_time).days
            doc["daysRemaining"] = max(0, days_remaining)
            doc["expiresAt"] = plan["expiresAt"].isoformat()
        else:
            doc["daysRemaining"] = None
        
        return {"success": True, "lessonPlan": doc}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lesson plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch lesson plan")

@api_router.delete("/lesson-plans/{plan_id}")
async def delete_lesson_plan(plan_id: str, user: dict = Depends(verify_token)):
    """Delete a lesson plan"""
    try:
        result = await db.lesson_plans.delete_one({
            "_id": ObjectId(plan_id),
            "teacherId": user["id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Lesson plan not found")
        
        return {"success": True, "message": "Lesson plan deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lesson plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete lesson plan")

@api_router.get("/lesson-plans/{plan_id}/pdf")
async def generate_lesson_plan_pdf_endpoint(plan_id: str, user: dict = Depends(verify_token)):
    """Generate and return a PDF for a lesson plan"""
    try:
        # Get the lesson plan
        plan = await db.lesson_plans.find_one({
            "_id": ObjectId(plan_id),
            "teacherId": user["id"]
        })
        
        if not plan:
            raise HTTPException(status_code=404, detail="Lesson plan not found")
        
        # Check if expired
        current_time = datetime.utcnow()
        if "expiresAt" in plan and plan["expiresAt"] and plan["expiresAt"] < current_time:
            raise HTTPException(status_code=410, detail="This lesson plan has expired")
        
        # Convert ObjectId to string and datetime to ISO format
        plan_dict = serialize_doc(plan)
        if "createdAt" in plan and plan["createdAt"]:
            plan_dict["createdAt"] = plan["createdAt"].isoformat()
        
        # Generate PDF
        pdf_bytes = generate_lesson_plan_pdf(plan_dict)
        
        # Create filename
        subject = plan.get("subjectName", "Lesson")
        grade = plan.get("gradeName", "Plan")
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"LessonPlan_{subject}_{grade}_{date_str}.pdf"
        filename = filename.replace(" ", "_")
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@api_router.post("/admin/cleanup-expired-plans")
async def cleanup_expired_plans(user: dict = Depends(verify_admin)):
    """Admin: Manually trigger cleanup of expired lesson plans"""
    try:
        current_time = datetime.utcnow()
        result = await db.lesson_plans.delete_many({
            "expiresAt": {"$lt": current_time, "$exists": True}
        })
        logger.info(f"Cleaned up {result.deleted_count} expired lesson plans")
        return {
            "success": True,
            "deletedCount": result.deleted_count,
            "message": f"Removed {result.deleted_count} expired lesson plan(s)"
        }
    except Exception as e:
        logger.error(f"Error cleaning up expired plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup expired plans")

@api_router.post("/notes/generate")
async def generate_notes_endpoint(request: GenerateNotesRequest, user: dict = Depends(verify_token)):
    """Generate rich educational notes for a given sub-strand (free to generate and preview)."""
    # Fetch all related curriculum data
    grade = await db.grades.find_one({"_id": ObjectId(request.gradeId)})
    subject = await db.subjects.find_one({"_id": ObjectId(request.subjectId)})
    strand = await db.strands.find_one({"_id": ObjectId(request.strandId)})
    substrand = await db.substrands.find_one({"_id": ObjectId(request.substrandId)})

    if not all([grade, subject, strand, substrand]):
        raise HTTPException(status_code=404, detail="Invalid selection. Please check your grade, subject, strand, and sub-strand.")

    # Fetch SLOs for this substrand
    slos = await db.slos.find({"substrandId": request.substrandId}).to_list(100)
    # Also try ObjectId-based lookup
    if not slos:
        try:
            slos = await db.slos.find({"substrandId": ObjectId(request.substrandId)}).to_list(100)
        except Exception:
            pass

    # Fetch learning activities for this substrand
    activities = []
    try:
        activities = await db.learning_activities.find({"substrandId": request.substrandId}).to_list(100)
        if not activities:
            activities = await db.learning_activities.find({"substrandId": ObjectId(request.substrandId)}).to_list(100)
    except Exception:
        pass
    # Also try 'activities' collection as fallback
    if not activities:
        try:
            activities = await db.activities.find({"substrandId": request.substrandId}).to_list(100)
            if not activities:
                activities = await db.activities.find({"substrandId": ObjectId(request.substrandId)}).to_list(100)
        except Exception:
            pass

    # Generate rich content
    generated = generate_notes_content(
        subject_name=subject["name"],
        strand_name=strand["name"],
        substrand_name=substrand["name"],
        slos=[serialize_doc(s) for s in slos],
        activities=activities,
        grade_name=grade["name"],
    )

    # Create notes record
    notes_doc = {
        "teacherId": user["id"],
        "teacherName": f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
        "schoolName": user.get("schoolName", ""),
        "gradeId": request.gradeId,
        "gradeName": grade["name"],
        "subjectId": request.subjectId,
        "subjectName": subject["name"],
        "strandId": request.strandId,
        "strandName": strand["name"],
        "substrandId": request.substrandId,
        "substrandName": substrand["name"],
        "generatedContent": generated,
        "downloaded": False,
        "createdAt": datetime.utcnow(),
    }

    result = await db.notes.insert_one(notes_doc)
    notes_id = str(result.inserted_id)

    # Build response (without _id)
    response_doc = {k: v for k, v in notes_doc.items() if k != "_id"}
    response_doc["id"] = notes_id
    response_doc["createdAt"] = response_doc["createdAt"].isoformat()

    return {"success": True, "notes": response_doc}


@api_router.get("/notes/{note_id}/preview")
async def preview_notes_pdf(note_id: str, user: dict = Depends(verify_token)):
    """Preview notes as PDF (FREE — no wallet deduction)."""
    note = await db.notes.find_one({"_id": ObjectId(note_id), "teacherId": user["id"]})
    if not note:
        raise HTTPException(status_code=404, detail="Notes not found")

    pdf_bytes = generate_notes_pdf(note)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=notes_{note_id}.pdf"},
    )


@api_router.post("/notes/{note_id}/download")
async def download_notes_pdf(note_id: str, user: dict = Depends(verify_token)):
    """Download notes as PDF (KES 1 deducted from wallet). First generation is free."""
    note = await db.notes.find_one({"_id": ObjectId(note_id), "teacherId": user["id"]})
    if not note:
        raise HTTPException(status_code=404, detail="Notes not found")

    user_id = user["id"]
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    free_notes_used = user_doc.get("freeNotesUsed", False) if user_doc else True
    wallet_balance = user_doc.get("walletBalance", 0.0) if user_doc else 0.0

    # First download is free
    if not free_notes_used:
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"freeNotesUsed": True}}
        )
        logger.info(f"User {user_id} used free notes download for note {note_id}")
    else:
        # Charge KES 1
        if wallet_balance < NOTES_DOWNLOAD_COST_KES:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient wallet balance. You need KES {NOTES_DOWNLOAD_COST_KES} to download notes. Current balance: KES {wallet_balance}"
            )

        import uuid
        ledger_ref = f"NOTES-{uuid.uuid4().hex[:12].upper()}"
        ledger_entry = {
            "userId": user_id,
            "type": "DEBIT",
            "amount": NOTES_DOWNLOAD_COST_KES,
            "reference": ledger_ref,
            "source": "NOTES_DOWNLOAD",
            "description": "Notes download",
            "createdAt": datetime.utcnow(),
        }
        await db.wallet_ledger.insert_one(ledger_entry)

        result = await db.users.update_one(
            {"_id": ObjectId(user_id), "walletBalance": {"$gte": NOTES_DOWNLOAD_COST_KES}},
            {"$inc": {"walletBalance": -NOTES_DOWNLOAD_COST_KES}}
        )
        if result.modified_count == 0:
            await db.wallet_ledger.delete_one({"reference": ledger_ref})
            raise HTTPException(status_code=402, detail="Insufficient wallet balance")

        logger.info(f"User {user_id} charged KES {NOTES_DOWNLOAD_COST_KES} for notes download. Ref: {ledger_ref}")

    # Mark as downloaded
    await db.notes.update_one({"_id": ObjectId(note_id)}, {"$set": {"downloaded": True}})

    # Generate PDF
    pdf_bytes = generate_notes_pdf(note)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=notes_{note_id}.pdf"},
    )

@api_router.get("/notes")
async def get_notes(user: dict = Depends(verify_token)):
    notes = await db.notes.find({"teacherId": user["id"]}).sort("createdAt", -1).to_list(100)
    return {"success": True, "notes": [serialize_doc(n) for n in notes]}

@api_router.get("/notes/{note_id}")
async def get_note(note_id: str, user: dict = Depends(verify_token)):
    note = await db.notes.find_one({"_id": ObjectId(note_id), "teacherId": user["id"]})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"success": True, "note": serialize_doc(note)}

# ==================== SCHEMES OF WORK ====================

@api_router.post("/schemes/generate")
async def generate_scheme_of_work(request: SchemeOfWorkRequest, user: dict = Depends(verify_token)):
    """Generate a comprehensive Scheme of Work matching KICD format"""
    
    # Fetch curriculum data
    grade = await db.grades.find_one({"_id": ObjectId(request.gradeId)})
    subject = await db.subjects.find_one({"_id": ObjectId(request.subjectId)})
    
    if not grade or not subject:
        raise HTTPException(status_code=404, detail="Invalid grade or subject")
    
    # Get all strands for this subject with numbering
    strands = await db.strands.find({"subjectId": request.subjectId}).to_list(100)
    
    # Get all substrands and SLOs with proper numbering
    all_curriculum_content = []
    strand_number = 0
    for strand in strands:
        strand_number += 1
        strand_id = str(strand["_id"])
        substrands = await db.substrands.find({"strandId": strand_id}).to_list(100)
        substrand_number = 0
        for substrand in substrands:
            substrand_number += 1
            substrand_id = str(substrand["_id"])
            slos = await db.slos.find({"substrandId": substrand_id}).to_list(100)
            for slo in slos:
                slo_id = str(slo["_id"])
                
                # Get competencies and values from mapping
                mapping = await db.slo_mappings.find_one({"sloId": slo_id})
                competencies_list = []
                values_list = []
                
                if mapping:
                    # Get competency names
                    for comp_id in mapping.get("competencyIds", []):
                        comp = await db.competencies.find_one({"_id": ObjectId(comp_id)})
                        if comp:
                            competencies_list.append(comp["name"])
                    
                    # Get value names
                    for val_id in mapping.get("valueIds", []):
                        val = await db.values.find_one({"_id": ObjectId(val_id)})
                        if val:
                            values_list.append(val["name"])
                
                all_curriculum_content.append({
                    "strand": f"{strand_number}.0 {strand['name']}",
                    "substrand": f"{strand_number}.{substrand_number} {substrand['name']}",
                    "slo": f"By the end of the lesson, the learner should be able to {slo['name'].lower()}.",
                    "sloRaw": slo['name'],
                    "coreCompetencies": ", ".join(competencies_list) if competencies_list else "Critical Thinking, Communication",
                    "coreValues": ", ".join(values_list) if values_list else "Responsibility, Respect",
                    "keyInquiryQuestions": generate_inquiry_questions(strand['name'], substrand['name'], slo['name']),
                    "learningExperiences": generate_learning_experiences(strand['name'], substrand['name'], slo['name']),
                    "learningResources": generate_learning_resources(strand['name'], substrand['name']),
                    "assessmentMethods": generate_assessment_methods(slo['name'])
                })
    
    # Calculate total lessons
    total_lessons = request.totalWeeks * request.lessonsPerWeek
    
    # Process breaks and create schedule
    breaks_map = {}  # {(week, lesson): break_info}
    
    for brk in request.breaks:
        if brk.durationType == "lessons":
            num_lessons = int(brk.durationValue)
        elif brk.durationType == "fraction":
            num_lessons = int(brk.durationValue * request.lessonsPerWeek)
        else:  # weeks
            num_lessons = int(brk.durationValue * request.lessonsPerWeek)
        
        start_week = brk.startWeek
        start_lesson = brk.startLesson if brk.startLesson else 1
        
        # Mark lessons as breaks
        current_week = start_week
        current_lesson = start_lesson
        lessons_marked = 0
        
        while lessons_marked < num_lessons:
            breaks_map[(current_week, current_lesson)] = {
                "type": brk.breakType,
                "description": brk.description or f"{brk.breakType}",
                "duration": num_lessons,
                "startWeek": brk.startWeek,
                "endWeek": current_week
            }
            lessons_marked += 1
            
            current_lesson += 1
            if current_lesson > request.lessonsPerWeek:
                current_lesson = 1
                current_week += 1
    
    # Generate lesson schedule
    lessons = []
    curriculum_index = 0
    lesson_counter = 0  # Overall lesson counter
    
    for week in range(1, request.totalWeeks + 1):
        week_has_break = any((week, l) in breaks_map for l in range(1, request.lessonsPerWeek + 1))
        
        for lesson_num in range(1, request.lessonsPerWeek + 1):
            lesson_counter += 1
            
            # Check if this is a break
            if (week, lesson_num) in breaks_map:
                brk_info = breaks_map[(week, lesson_num)]
                # Only add break entry once per break period
                existing_break = next((l for l in lessons if l.get("isBreak") and l.get("breakType") == brk_info["type"] and l.get("week") == brk_info["startWeek"]), None)
                if not existing_break:
                    lessons.append({
                        "week": week,
                        "lessonNumber": lesson_num,
                        "isBreak": True,
                        "breakType": brk_info["type"],
                        "breakDescription": brk_info["description"],
                        "breakDuration": brk_info["duration"],
                        "strand": "",
                        "substrand": "",
                        "slo": "",
                        "keyInquiryQuestions": "",
                        "learningExperiences": "",
                        "learningResources": "",
                        "assessmentMethods": "",
                        "reflection": ""
                    })
            else:
                # Regular lesson
                if curriculum_index < len(all_curriculum_content):
                    content = all_curriculum_content[curriculum_index]
                    curriculum_index += 1
                    
                    lessons.append({
                        "week": week,
                        "lessonNumber": lesson_num,
                        "isBreak": False,
                        "breakType": None,
                        "breakDescription": None,
                        "strand": content["strand"],
                        "substrand": content["substrand"],
                        "slo": content["slo"],
                        "coreCompetencies": content["coreCompetencies"],
                        "coreValues": content["coreValues"],
                        "keyInquiryQuestions": content["keyInquiryQuestions"],
                        "learningExperiences": content["learningExperiences"],
                        "learningResources": content["learningResources"],
                        "assessmentMethods": content["assessmentMethods"],
                        "reflection": ""
                    })
                else:
                    # Revision/Consolidation lessons when curriculum exhausted
                    lessons.append({
                        "week": week,
                        "lessonNumber": lesson_num,
                        "isBreak": False,
                        "breakType": None,
                        "breakDescription": None,
                        "strand": "Revision",
                        "substrand": "Term Revision",
                        "slo": "By the end of the lesson, the learner should be able to review and consolidate learning for the term.",
                        "keyInquiryQuestions": "What have we learned? What areas need more practice?",
                        "learningExperiences": "The learner is guided to review key concepts, complete practice exercises, and engage in peer discussions.",
                        "learningResources": "Revision notes, Past papers, Reference materials",
                        "assessmentMethods": "Oral questions, Written tests",
                        "reflection": ""
                    })
    
    # Create scheme document
    scheme = {
        "teacherId": user["id"],
        "teacherName": request.teacherName or f"{user.get('firstName', '')} {user.get('lastName', '')}".strip(),
        "school": request.school,
        "subjectId": request.subjectId,
        "subjectName": subject["name"],
        "gradeId": request.gradeId,
        "gradeName": grade["name"],
        "term": request.term,
        "year": request.year,
        "curriculumStandard": request.curriculumStandard,
        "totalWeeks": request.totalWeeks,
        "lessonsPerWeek": request.lessonsPerWeek,
        "lessons": lessons,
        "createdAt": datetime.utcnow()
    }
    
    result = await db.schemes.insert_one(scheme)
    if "_id" in scheme:
        del scheme["_id"]
    scheme["id"] = str(result.inserted_id)
    scheme["createdAt"] = scheme["createdAt"].isoformat()
    
    return {"success": True, "scheme": scheme}

# Helper functions for generating scheme content
def generate_inquiry_questions(strand: str, substrand: str, slo: str, is_kiswahili: bool = False) -> str:
    """Generate relevant key inquiry questions based on the topic"""
    import re
    # Strip leading numbering like "2.3 ", "1.2.1 ", "3. " from substrand name
    clean_substrand = re.sub(r'^[\d]+(?:\.[\d]+)*\.?\s*', '', substrand).strip()
    if not clean_substrand:
        clean_substrand = substrand
    
    questions = []
    
    if is_kiswahili:
        # Kiswahili inquiry questions
        if "fasihi" in substrand.lower() or "hadithi" in substrand.lower():
            questions.append(f"Umuhimu wa {clean_substrand} ni upi katika jamii?")
            questions.append(f"Tunajifunza nini kutoka kwa {clean_substrand}?")
        elif "sarufi" in substrand.lower() or "lugha" in substrand.lower():
            questions.append(f"Kanuni za {clean_substrand} ni zipi?")
            questions.append(f"Tunatumia vipi {clean_substrand} katika mawasiliano?")
        elif "uandishi" in substrand.lower() or "insha" in substrand.lower():
            questions.append(f"Hatua za kuandika {clean_substrand} ni zipi?")
            questions.append(f"Sifa za {clean_substrand} bora ni zipi?")
        elif "usomaji" in substrand.lower() or "kusoma" in substrand.lower():
            questions.append(f"Mbinu za kusoma {clean_substrand} kwa ufanisi ni zipi?")
            questions.append(f"Tunaelewaje maana ya {clean_substrand}?")
        else:
            questions.append(f"Umuhimu wa {clean_substrand} ni upi?")
            questions.append(f"Tunatumia vipi {clean_substrand} katika maisha ya kila siku?")
    else:
        # English inquiry questions
        if "evolution" in substrand.lower() or "history" in substrand.lower():
            questions.append(f"How has {clean_substrand} developed over time?")
            questions.append(f"What are the key milestones in the development of {clean_substrand}?")
        elif "architecture" in substrand.lower() or "structure" in substrand.lower():
            questions.append(f"What are the main components of {clean_substrand}?")
            questions.append(f"How do the different parts of {clean_substrand} work together?")
        elif "network" in substrand.lower() or "communication" in substrand.lower():
            questions.append(f"How is data transmitted in {clean_substrand}?")
            questions.append(f"What factors affect {clean_substrand} performance?")
        elif "programming" in substrand.lower() or "code" in substrand.lower():
            questions.append(f"How do we implement {clean_substrand} in programming?")
            questions.append(f"What are the best practices for {clean_substrand}?")
        else:
            questions.append(f"What is the importance of {clean_substrand}?")
            questions.append(f"How do we apply {clean_substrand} in real-world situations?")
    
    return " ".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

def generate_learning_experiences(strand: str, substrand: str, slo: str, is_kiswahili: bool = False) -> str:
    """Generate appropriate learning experiences"""
    slo_lower = slo.lower()
    
    if is_kiswahili:
        # Kiswahili learning experiences
        if "tambua" in slo_lower or "eleza" in slo_lower or "ainisha" in slo_lower:
            return f"Mwanafunzi anaongozwa kutafuta habari kuhusu {substrand} kwa kutumia vitabu na nyenzo za kidijitali."
        elif "tunga" in slo_lower or "andika" in slo_lower or "buni" in slo_lower:
            return f"Mwanafunzi anaongozwa kutunga/kuandika kazi inayoonyesha ujuzi wa {substrand}."
        elif "linganisha" in slo_lower or "tofautisha" in slo_lower:
            return f"Mwanafunzi anaongozwa kulinganisha na kutofautisha vipengele vya {substrand} kupitia majadiliano ya vikundi."
        elif "jadili" in slo_lower or "fafanua" in slo_lower:
            return f"Mwanafunzi anaongozwa kujadili na kufafanua dhana za {substrand} kupitia ujifunzaji shirikishi."
        elif "tumia" in slo_lower or "tekeleza" in slo_lower:
            return f"Mwanafunzi anaongozwa kutumia dhana za {substrand} kupitia mazoezi ya vitendo."
        elif "changanua" in slo_lower or "tathmini" in slo_lower:
            return f"Mwanafunzi anaongozwa kuchanganua na kutathmini mifano ya {substrand}."
        else:
            return f"Mwanafunzi anaongozwa kuchunguza na kuelewa {substrand} kupitia shughuli za kujifunza."
    else:
        # English learning experiences
        if "identify" in slo_lower or "describe" in slo_lower:
            return f"The learner is guided to search for information on {substrand} using reference materials and digital resources."
        elif "create" in slo_lower or "make" in slo_lower or "design" in slo_lower:
            return f"The learner is guided to create/design a model or project demonstrating {substrand} using locally available materials."
        elif "compare" in slo_lower or "differentiate" in slo_lower:
            return f"The learner is guided to compare and contrast different aspects of {substrand} through group discussions and research."
        elif "explain" in slo_lower or "discuss" in slo_lower:
            return f"The learner is guided to discuss and explain concepts related to {substrand} through collaborative learning."
        elif "apply" in slo_lower or "use" in slo_lower:
            return f"The learner is guided to apply {substrand} concepts through practical exercises and problem-solving activities."
        elif "analyze" in slo_lower or "evaluate" in slo_lower:
            return f"The learner is guided to analyze case studies and evaluate different approaches to {substrand}."
        else:
            return f"The learner is guided to explore and understand {substrand} through interactive learning activities."

def generate_learning_resources(strand: str, substrand: str, is_kiswahili: bool = False) -> str:
    """Generate appropriate learning resources"""
    
    if is_kiswahili:
        resources = ["Vitabu vya kiada"]
        strand_lower = strand.lower()
        substrand_lower = substrand.lower()
        
        if "fasihi" in strand_lower or "hadithi" in substrand_lower:
            resources.extend(["Vitabu vya fasihi", "Hadithi", "Mashairi"])
        if "sarufi" in strand_lower or "lugha" in substrand_lower:
            resources.extend(["Kamusi", "Chati za sarufi"])
        if "uandishi" in substrand_lower or "insha" in substrand_lower:
            resources.extend(["Sampuli za insha", "Karatasi", "Kalamu"])
        if "usomaji" in substrand_lower:
            resources.extend(["Vifungu vya kusoma", "Magazeti", "Majarida"])
        
        resources.append("Nyenzo za kidijitali")
        return ", ".join(resources[:5])
    else:
        resources = ["Reference materials"]
        strand_lower = strand.lower()
        substrand_lower = substrand.lower()
        
        if "computer" in strand_lower or "technology" in strand_lower:
            resources.extend(["Computers", "Digital devices", "Internet"])
        if "network" in strand_lower or "communication" in substrand_lower:
            resources.extend(["Network cables", "Networking equipment diagrams"])
        if "programming" in strand_lower or "code" in substrand_lower:
            resources.extend(["Programming IDE", "Code samples"])
        if "model" in substrand_lower or "architecture" in substrand_lower:
            resources.extend(["Modeling materials", "Charts", "Diagrams"])
        
        resources.append("Textbooks")
        return ", ".join(resources[:5])

def generate_assessment_methods(slo: str, is_kiswahili: bool = False) -> str:
    """Generate appropriate assessment methods based on SLO"""
    slo_lower = slo.lower()
    
    if is_kiswahili:
        if "tambua" in slo_lower or "eleza" in slo_lower or "fafanua" in slo_lower:
            return "Maswali ya mdomo"
        elif "tunga" in slo_lower or "andika" in slo_lower or "buni" in slo_lower:
            return "Kazi ya uandishi"
        elif "linganisha" in slo_lower or "changanua" in slo_lower:
            return "Kazi ya maandishi"
        elif "soma" in slo_lower or "kariri" in slo_lower:
            return "Usomaji"
        else:
            return "Uchunguzi"
    else:
        if "identify" in slo_lower or "describe" in slo_lower or "explain" in slo_lower:
            return "Oral questions"
        elif "create" in slo_lower or "make" in slo_lower or "design" in slo_lower:
            return "Project"
        elif "compare" in slo_lower or "analyze" in slo_lower:
            return "Written assignment"
        elif "discuss" in slo_lower:
            return "Discussion"
        elif "demonstrate" in slo_lower or "apply" in slo_lower:
            return "Practical assessment"
        else:
            return "Oral questions"

@api_router.get("/schemes")
async def get_schemes(user: dict = Depends(verify_token)):
    schemes = await db.schemes.find({"teacherId": user["id"]}).sort("createdAt", -1).to_list(100)
    return {"success": True, "schemes": [serialize_doc(s) for s in schemes]}

# ==================== NEW SCHEME ENDPOINTS ====================

@api_router.get("/schemes/config/lessons-per-week")
async def get_lessons_per_week_config(
    gradeId: str,
    subjectId: str,
    user: dict = Depends(verify_token)
):
    """Get the default lessons per week for a subject in a grade"""
    grade = await db.grades.find_one({"_id": ObjectId(gradeId)})
    subject = await db.subjects.find_one({"_id": ObjectId(subjectId)})
    
    if not grade or not subject:
        raise HTTPException(status_code=404, detail="Invalid grade or subject")
    
    lessons = get_lessons_per_week(grade["name"], subject["name"])
    
    return {
        "success": True,
        "lessonsPerWeek": lessons,
        "gradeName": grade["name"],
        "subjectName": subject["name"]
    }

@api_router.get("/schemes/topics/{subjectId}")
async def get_scheme_topics(subjectId: str, user: dict = Depends(verify_token)):
    """Get all topics (strands/substrands) for topic selection UI"""
    
    # Get all strands for the subject
    strands = await db.strands.find({"subjectId": subjectId}).sort("order", 1).to_list(100)
    
    topics = []
    for strand in strands:
        strand_id = str(strand["_id"])
        
        # Get substrands for this strand
        substrands = await db.substrands.find({"strandId": strand_id}).sort("order", 1).to_list(100)
        
        substrand_items = []
        for ss in substrands:
            ss_id = str(ss["_id"])
            
            # Count SLOs for this substrand
            slo_count = await db.slos.count_documents({"substrandId": ss_id})
            
            substrand_items.append({
                "id": ss_id,
                "name": ss["name"],
                "sloCount": slo_count
            })
        
        topics.append({
            "id": strand_id,
            "name": strand["name"],
            "substrands": substrand_items,
            "totalSlos": sum(s["sloCount"] for s in substrand_items)
        })
    
    return {"success": True, "topics": topics}

# --- Scheme draft list/detail routes (must come before /{scheme_id} catch-all) ---

@api_router.get("/schemes/drafts")
async def get_scheme_drafts(user: dict = Depends(verify_token)):
    """List user's scheme drafts."""
    drafts = await db.scheme_drafts.find(
        {"teacherId": user["id"]}
    ).sort("updatedAt", -1).to_list(50)
    result = []
    for d in drafts:
        d["id"] = str(d.pop("_id"))
        for k in ["createdAt", "updatedAt", "paidAt", "lastDownloadedAt"]:
            if d.get(k) and hasattr(d[k], "isoformat"):
                d[k] = d[k].isoformat()
        result.append(d)
    return {"success": True, "drafts": result}


@api_router.get("/schemes/drafts/{draft_id}")
async def get_scheme_draft(draft_id: str, user: dict = Depends(verify_token)):
    """Get a single scheme draft by ID."""
    draft = await db.scheme_drafts.find_one({"_id": ObjectId(draft_id), "teacherId": user["id"]})
    if not draft:
        raise HTTPException(status_code=404, detail="Scheme draft not found")
    draft["id"] = str(draft.pop("_id"))
    for k in ["createdAt", "updatedAt", "paidAt", "lastDownloadedAt"]:
        if draft.get(k) and hasattr(draft[k], "isoformat"):
            draft[k] = draft[k].isoformat()
    return {"success": True, "draft": draft}


# Dynamic scheme ID route — MUST come after all static /schemes/... routes
@api_router.get("/schemes/{scheme_id}")
async def get_scheme(scheme_id: str, user: dict = Depends(verify_token)):
    scheme = await db.schemes.find_one({"_id": ObjectId(scheme_id), "teacherId": user["id"]})
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return {"success": True, "scheme": serialize_doc(scheme)}

class SchemeGenerateRequest(BaseModel):
    gradeId: str
    subjectId: str
    term: int
    year: int = datetime.now().year
    totalWeeks: int = 12
    lessonsPerWeek: Optional[int] = None  # Auto-calculated if not provided
    selectedTopics: List[str]  # List of substrand IDs
    breaks: List[Dict[str, Any]] = []
    doubleLesson: Optional[Dict[str, Any]] = None  # { enabled: bool, position: "2-3" }
    includeCarryOver: bool = False  # Compression mode for uncovered content

# Safe integer conversion helper
def to_int(value, default: int = 0) -> int:
    """Safely convert any value to integer"""
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

# Validate break input
def validate_break(brk: Dict[str, Any], lessons_per_week: int, total_weeks: int) -> Dict[str, Any]:
    """Validate and normalize break data"""
    start_week = to_int(brk.get("startWeek"), 1)
    start_lesson = to_int(brk.get("startLesson"), 1)
    end_week = to_int(brk.get("endWeek"), start_week)
    end_lesson = to_int(brk.get("endLesson"), lessons_per_week)
    
    # Clamp values to valid ranges
    start_week = max(1, min(start_week, total_weeks))
    end_week = max(start_week, min(end_week, total_weeks))
    start_lesson = max(1, min(start_lesson, lessons_per_week))
    end_lesson = max(1, min(end_lesson, lessons_per_week))
    
    # Ensure end is after start
    if end_week == start_week and end_lesson < start_lesson:
        end_lesson = start_lesson
    
    return {
        "breakType": brk.get("breakType", "Break"),
        "startWeek": start_week,
        "startLesson": start_lesson,
        "endWeek": end_week,
        "endLesson": end_lesson,
        "startDate": brk.get("startDate")  # Optional calendar date
    }

# Calculate break duration in lessons
def calculate_break_duration(start_week: int, start_lesson: int, end_week: int, end_lesson: int, lessons_per_week: int) -> int:
    """Calculate total lessons covered by a break"""
    if start_week == end_week:
        return (end_lesson - start_lesson) + 1
    else:
        # Lessons in first week + full weeks in between + lessons in last week
        first_week_lessons = lessons_per_week - start_lesson + 1
        full_weeks = (end_week - start_week - 1) * lessons_per_week
        last_week_lessons = end_lesson
        return first_week_lessons + full_weeks + last_week_lessons

@api_router.post("/schemes/generate-v2")
async def generate_scheme_v2(request: SchemeGenerateRequest, user: dict = Depends(verify_token)):
    """Generate scheme of work from selected topics"""
    try:
        # Fetch grade and subject
        grade = await db.grades.find_one({"_id": ObjectId(request.gradeId)})
        subject = await db.subjects.find_one({"_id": ObjectId(request.subjectId)})
        
        if not grade or not subject:
            raise HTTPException(status_code=404, detail="Invalid grade or subject")
        
        # Ensure numeric values are integers
        total_weeks = to_int(request.totalWeeks, 12)
        lessons_per_week = to_int(request.lessonsPerWeek) if request.lessonsPerWeek else get_lessons_per_week(grade["name"], subject["name"])
        
        # Get user's school name
        user_profile = await db.users.find_one({"firebaseUid": user.get("firebaseUid", user.get("id", ""))})
        school_name = user_profile.get("schoolName", "") if user_profile else ""
        
        # Collect all curriculum content from selected topics
        curriculum_content = []
    
        for substrand_id in request.selectedTopics:
            substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
            if not substrand:
                continue
            strand = await db.strands.find_one({"_id": ObjectId(substrand["strandId"])})
            if not strand:
                continue

            # STRICT: slot count from number_of_lessons only
            num_lessons = substrand.get("number_of_lessons")
            if not num_lessons or int(num_lessons) < 1:
                # Fallback: use parent SLO count if number_of_lessons not set
                slo_count = await db.slos.count_documents({"substrandId": substrand_id})
                num_lessons = max(1, slo_count)
            else:
                num_lessons = int(num_lessons)

            # Load parent SLOs for fallback
            parent_slos = await db.slos.find(
                {"substrandId": substrand_id}
            ).sort("order", 1).to_list(100)
            if not parent_slos:
                continue

            learning_act = await db.learning_activities.find_one({"substrandId": substrand_id})

            # Load lesson_slo_slots (primary source — Phase 5)
            raw_slots = await db.lesson_slo_slots.find(
                {"substrandId": substrand_id}
            ).sort("slot_index", 1).to_list(500)
            slots_by_idx = {s["slot_index"]: s for s in raw_slots}

            for idx in range(num_lessons):
                slot = slots_by_idx.get(idx)
                parent_slo = parent_slos[idx % len(parent_slos)]
                parent_slo_id = str(parent_slo["_id"])

                # Resolve outcome: slot > parent SLO
                slo_text = slot["outcome"] if (slot and slot.get("outcome")) else parent_slo["name"]

                # Resolve ONE inquiry question
                inquiry_q = ""
                if slot and slot.get("key_inquiry_question"):
                    inquiry_q = slot["key_inquiry_question"]

                # Resolve competencies / values / pcis
                competencies = (slot.get("competencies") if slot else None) or []
                values_list = (slot.get("values") if slot else None) or []
                pcis = (slot.get("pcis") if slot else None) or []

                if not competencies:
                    mapping = await db.slo_mappings.find_one({"sloId": parent_slo_id})
                    if mapping:
                        for cid in mapping.get("competencyIds", []):
                            doc = await db.competencies.find_one({"_id": ObjectId(cid)})
                            if doc:
                                competencies.append(doc["name"])
                        if not values_list:
                            for vid in mapping.get("valueIds", []):
                                doc = await db.values.find_one({"_id": ObjectId(vid)})
                                if doc:
                                    values_list.append(doc["name"])
                        if not pcis:
                            for pid in mapping.get("pciIds", []):
                                doc = await db.pcis.find_one({"_id": ObjectId(pid)})
                                if doc:
                                    pcis.append(doc["name"])

                # Resolve resources with textbook formatting
                raw_resources = (slot.get("resources") if slot else None) or []
                if raw_resources:
                    formatted_resources = [format_resource_display(r) for r in raw_resources]
                elif learning_act:
                    formatted_resources = learning_act.get("learning_resources", [])
                else:
                    formatted_resources = []

                activities = (slot.get("learning_activities") if slot else None) or (
                    learning_act.get("development_activities", []) if learning_act else []
                )
                assessment = (slot.get("assessment_methods") if slot else None) or (
                    learning_act.get("assessment_methods", []) if learning_act else []
                )

                curriculum_content.append({
                    "strandId": str(strand["_id"]),
                    "strand": strand["name"],
                    "substrandId": substrand_id,
                    "substrand": substrand["name"],
                    "sloId": parent_slo_id,
                    "slo": slo_text,
                    "sloDescription": parent_slo.get("description", parent_slo["name"]),
                    "lessonInSubstrand": idx + 1,
                    "totalLessonsInSubstrand": num_lessons,
                    "competencies": competencies or ["Critical Thinking", "Communication"],
                    "values": values_list or ["Responsibility", "Respect"],
                    "pcis": pcis,
                    "learningActivities": activities,
                    "resources": formatted_resources,
                    "assessmentMethods": assessment,
                    "_slotInquiry": inquiry_q,
                })
    
        if not curriculum_content:
            raise HTTPException(status_code=400, detail="No valid topics selected")
    
        # Process breaks with safe integer conversion
        breaks_map = {}
        validated_breaks = []
    
        for brk in request.breaks:
            # Validate and normalize break data
            validated = validate_break(brk, lessons_per_week, total_weeks)
            validated_breaks.append(validated)
        
            start_week = validated["startWeek"]
            start_lesson = validated["startLesson"]
            end_week = validated["endWeek"]
            end_lesson = validated["endLesson"]
        
            # Mark all lessons from start to end as breaks
            current_week = start_week
            current_lesson = start_lesson
            is_first = True
        
            while True:
                breaks_map[(current_week, current_lesson)] = {
                    "type": validated["breakType"],
                    "isFirst": is_first,
                    "startDate": validated.get("startDate")
                }
                is_first = False
            
                # Check if we've reached the end
                if current_week == end_week and current_lesson == end_lesson:
                    break
            
                # Move to next lesson
                current_lesson += 1
                if current_lesson > lessons_per_week:
                    current_lesson = 1
                    current_week += 1
            
                # Safety check to prevent infinite loop
                if current_week > total_weeks:
                    break
    
        # Generate lessons
        lessons = []
        content_index = 0
        total_lessons_count = total_weeks * lessons_per_week
    
        # Parse double lesson configuration with safe conversion
        double_lesson_enabled = False
        double_lesson_start = 2
        double_lesson_end = 3
        if request.doubleLesson and request.doubleLesson.get("enabled"):
            double_lesson_enabled = True
            pos = str(request.doubleLesson.get("position", "2-3"))
            parts = pos.split("-")
            if len(parts) == 2:
                double_lesson_start = to_int(parts[0], 2)
                double_lesson_end = to_int(parts[1], 3)
    
        # Compression factor for carry-over content
        compression_factor = 0.7 if request.includeCarryOver else 1.0
        
        # Check if this is a Kiswahili subject
        is_kiswahili = 'kiswahili' in subject["name"].lower() or 'fasihi' in subject["name"].lower()
    
        for week in range(1, total_weeks + 1):
            lesson_num = 1
            while lesson_num <= lessons_per_week:
                # Check for break
                if (week, lesson_num) in breaks_map:
                    brk_info = breaks_map[(week, lesson_num)]
                    if brk_info["isFirst"]:
                        # Find the end of this break to show lesson range
                        break_end_week = week
                        break_end_lesson = lesson_num
                        
                        # Look ahead to find the last lesson of this break
                        temp_week = week
                        temp_lesson = lesson_num
                        while (temp_week, temp_lesson) in breaks_map and breaks_map[(temp_week, temp_lesson)]["type"] == brk_info["type"]:
                            break_end_week = temp_week
                            break_end_lesson = temp_lesson
                            temp_lesson += 1
                            if temp_lesson > lessons_per_week:
                                temp_lesson = 1
                                temp_week += 1
                            if temp_week > total_weeks:
                                break
                        
                        # Format lesson range
                        if week == break_end_week:
                            lesson_range = f"{lesson_num}-{break_end_lesson}" if lesson_num != break_end_lesson else str(lesson_num)
                        else:
                            lesson_range = f"Wk{week}L{lesson_num} to Wk{break_end_week}L{break_end_lesson}"
                        
                        lessons.append({
                            "isBreak": True,
                            "breakType": brk_info["type"],
                            "week": week,
                            "lesson": lesson_num,
                            "endWeek": break_end_week,
                            "endLesson": break_end_lesson,
                            "lessonRange": lesson_range
                        })
                    lesson_num += 1
                    continue
            
                # Check if this is a double lesson position
                is_double = double_lesson_enabled and lesson_num == double_lesson_start
                lesson_display = f"{double_lesson_start}-{double_lesson_end}" if is_double else str(lesson_num)
            
                # Add curriculum content
                if content_index < len(curriculum_content):
                    content = curriculum_content[content_index]
                
                    # Generate inquiry questions — prefer slot's single question
                    slot_inquiry = content.get("_slotInquiry", "")
                    if slot_inquiry:
                        inquiry_qs = slot_inquiry
                    else:
                        inquiry_qs = generate_inquiry_questions(
                            content["strand"], 
                            content["substrand"], 
                            content["slo"]
                        )
                
                    # Generate learning experiences
                    experiences = content.get("learningActivities", [])
                    if not experiences:
                        experiences = generate_learning_experiences(
                            content["strand"],
                            content["substrand"],
                            content["slo"]
                        )
                
                    # Generate resources
                    resources = content.get("resources", [])
                    if not resources:
                        resources = generate_learning_resources(
                            content["strand"],
                            content["substrand"]
                        )
                
                    # Get assessment
                    assessment = content.get("assessmentMethods", [])
                    if not assessment:
                        assessment = get_assessment_for_slo(content["slo"])
                
                    lessons.append({
                        "week": week,
                        "lesson": lesson_display,
                        "isDouble": is_double,
                        "strand": content["strand"],
                        "substrand": content["substrand"],
                        "slo": f"By the end of the lesson, the learner should be able to {content['slo'].lower()}.",
                        "lessonInSubstrand": content.get("lessonInSubstrand", 1),
                        "totalLessonsInSubstrand": content.get("totalLessonsInSubstrand", 1),
                        "keyInquiryQuestions": inquiry_qs,
                        "learningExperiences": experiences[:4] if isinstance(experiences, list) else [experiences],
                        "learningResources": resources[:4] if isinstance(resources, list) else [resources],
                        "assessmentMethods": assessment[:2] if isinstance(assessment, list) else [assessment],
                        "competencies": content["competencies"],
                        "values": content["values"],
                        "pcis": content.get("pcis", [])
                    })
                
                    content_index += 1
                
                    # For double lessons, skip the next lesson number
                    if is_double:
                        lesson_num += 2
                    else:
                        lesson_num += 1
                else:
                    # Repeat content if needed (or stop if compression mode)
                    if request.includeCarryOver:
                        break  # Stop if we run out of content in compression mode
                    content_index = 0
                    lesson_num += 1
    
        # Build scheme data
        scheme_data = {
            "teacherId": user.get("id", ""),
            "gradeId": request.gradeId,
            "gradeName": grade["name"],
            "subjectId": request.subjectId,
            "subjectName": subject["name"],
            "term": request.term,
            "year": request.year,
            "totalWeeks": total_weeks,
            "lessonsPerWeek": lessons_per_week,
            "schoolName": school_name,
            "selectedTopics": request.selectedTopics,
            "lessons": lessons,
            "breaks": validated_breaks,
            "doubleLesson": request.doubleLesson,
            "includeCarryOver": request.includeCarryOver,
            "createdAt": datetime.utcnow()
        }
    
        return {
            "success": True,
            "scheme": scheme_data,
            "summary": {
                "totalLessons": len([l for l in lessons if not l.get("isBreak")]),
                "totalBreaks": len([l for l in lessons if l.get("isBreak")]),
                "doubleLessons": len([l for l in lessons if l.get("isDouble")]),
                "topics": len(request.selectedTopics)
            }
        }
    
    except Exception as e:
        logger.error(f"Error generating scheme: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={
                "message": "Failed to generate scheme",
                "error": str(e)
            }
        )

@api_router.post("/schemes/preview")
async def preview_scheme(scheme_data: Dict[str, Any], user: dict = Depends(verify_token)):
    """Generate PDF preview (no wallet charge)"""
    logger.info("Preview scheme route hit")
    try:
        pdf_bytes = generate_scheme_pdf(scheme_data)
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'inline; filename="scheme_preview.pdf"',
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except Exception as e:
        logger.error(f"Error generating scheme preview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate preview")

SCHEME_DOWNLOAD_COST = 15  # KES

@api_router.post("/schemes/download")
async def download_scheme(scheme_data: Dict[str, Any], user: dict = Depends(verify_token)):
    """Download scheme PDF (costs KES 15)"""
    logger.info("Download scheme route hit")
    
    # Check wallet balance - use firebaseUid from user object
    firebase_uid = user.get("firebaseUid")
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Invalid user session")
    
    user_profile = await db.users.find_one({"firebaseUid": firebase_uid})
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_balance = user_profile.get("walletBalance", 0)
    
    if current_balance < SCHEME_DOWNLOAD_COST:
        raise HTTPException(
            status_code=402, 
            detail={
                "message": "Insufficient wallet balance",
                "required": SCHEME_DOWNLOAD_COST,
                "current": current_balance
            }
        )
    
    import uuid as uuid_lib
    ledger_ref = f"SCHEME-{uuid_lib.uuid4().hex[:12].upper()}"
    
    # Create wallet_ledger DEBIT entry first (source of truth)
    ledger_entry = {
        "userId": user["id"],
        "type": "DEBIT",
        "amount": SCHEME_DOWNLOAD_COST,
        "reference": ledger_ref,
        "source": "SCHEME_DOWNLOAD",
        "description": f"Scheme of Work — {scheme_data.get('subjectName', 'Subject')} Term {scheme_data.get('term', 1)}",
        "createdAt": datetime.utcnow()
    }
    try:
        await db.wallet_ledger.insert_one(ledger_entry)
    except Exception:
        raise HTTPException(status_code=500, detail="Payment processing error. Please try again.")
    
    # Atomic deduction with balance guard (prevents race condition)
    result = await db.users.update_one(
        {"firebaseUid": firebase_uid, "walletBalance": {"$gte": SCHEME_DOWNLOAD_COST}},
        {"$inc": {"walletBalance": -SCHEME_DOWNLOAD_COST}}
    )
    
    if result.modified_count == 0:
        # Rollback the ledger entry
        await db.wallet_ledger.delete_one({"reference": ledger_ref})
        raise HTTPException(status_code=402, detail="Insufficient wallet balance")
    
    # Sync wallets collection
    await db.wallets.update_one(
        {"userId": user["id"]},
        {"$inc": {"balance": -SCHEME_DOWNLOAD_COST}, "$set": {"updatedAt": datetime.utcnow()}},
        upsert=True
    )
    
    logger.info(f"Scheme download charged KES {SCHEME_DOWNLOAD_COST} for user {user['id']}. Ref: {ledger_ref}")
    
    # Generate PDF
    try:
        pdf_bytes = generate_scheme_pdf(scheme_data)
        
        # Create filename
        subject = scheme_data.get('subjectName', 'Subject').replace(' ', '_')
        grade = scheme_data.get('gradeName', 'Grade').replace(' ', '_')
        term = scheme_data.get('term', 1)
        filename = f"Scheme_{subject}_{grade}_Term{term}.pdf"
        
        updated_user = await db.users.find_one({"firebaseUid": firebase_uid})
        new_balance = updated_user.get("walletBalance", 0) if updated_user else 0
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
                "X-New-Balance": str(new_balance)
            }
        )
    except Exception as e:
        # Refund wallet atomically
        await db.users.update_one(
            {"firebaseUid": firebase_uid},
            {"$inc": {"walletBalance": SCHEME_DOWNLOAD_COST}}
        )
        # Rollback ledger entry
        await db.wallet_ledger.delete_one({"reference": ledger_ref})
        # Rollback wallets collection
        await db.wallets.update_one(
            {"userId": user["id"]},
            {"$inc": {"balance": SCHEME_DOWNLOAD_COST}, "$set": {"updatedAt": datetime.utcnow()}}
        )
        logger.error(f"Scheme PDF generation failed, refunded user {user['id']}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF. Your payment has been refunded.")

# ==================== SCHEME DRAFT WORKFLOW ====================

@api_router.post("/schemes/save-draft")
async def save_scheme_draft(body: Dict[str, Any], user: dict = Depends(verify_token)):
    """Save a generated scheme as a draft record. No wallet charge."""
    scheme_data = body.get("scheme")
    generation_input = body.get("generationInput")
    if not scheme_data:
        raise HTTPException(status_code=400, detail="No scheme data provided")

    draft = {
        "teacherId": user["id"],
        "scheme": scheme_data,
        "generationInput": generation_input,
        "status": "draft",
        "isPaid": False,
        "paidAt": None,
        "paymentReference": None,
        "downloadCount": 0,
        "lastDownloadedAt": None,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    result = await db.scheme_drafts.insert_one(draft)
    return {"success": True, "draftId": str(result.inserted_id)}


@api_router.post("/schemes/drafts/{draft_id}/regenerate")
async def regenerate_scheme_draft(draft_id: str, body: Dict[str, Any], user: dict = Depends(verify_token)):
    """Regenerate a draft scheme with updated parameters. Replaces scheme data."""
    draft = await db.scheme_drafts.find_one({"_id": ObjectId(draft_id), "teacherId": user["id"]})
    if not draft:
        raise HTTPException(status_code=404, detail="Scheme draft not found")

    new_scheme = body.get("scheme")
    new_input = body.get("generationInput")
    if not new_scheme:
        raise HTTPException(status_code=400, detail="No scheme data provided")

    await db.scheme_drafts.update_one(
        {"_id": ObjectId(draft_id)},
        {"$set": {
            "scheme": new_scheme,
            "generationInput": new_input or draft.get("generationInput"),
            "updatedAt": datetime.utcnow(),
        }}
    )
    return {"success": True, "message": "Draft regenerated"}


@api_router.post("/schemes/drafts/{draft_id}/preview")
async def preview_scheme_draft(draft_id: str, user: dict = Depends(verify_token)):
    """Preview PDF for a saved scheme draft. No wallet charge."""
    draft = await db.scheme_drafts.find_one({"_id": ObjectId(draft_id), "teacherId": user["id"]})
    if not draft:
        raise HTTPException(status_code=404, detail="Scheme draft not found")

    try:
        pdf_bytes = generate_scheme_pdf(draft["scheme"])
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'inline; filename="scheme_preview.pdf"',
                "Content-Length": str(len(pdf_bytes)),
            }
        )
    except Exception as e:
        logger.error(f"Error previewing scheme draft: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate preview")


@api_router.post("/schemes/drafts/{draft_id}/download")
async def download_scheme_draft(draft_id: str, user: dict = Depends(verify_token)):
    """Download PDF for a saved scheme draft. Charges KES 15 on first download."""
    draft = await db.scheme_drafts.find_one({"_id": ObjectId(draft_id), "teacherId": user["id"]})
    if not draft:
        raise HTTPException(status_code=404, detail="Scheme draft not found")

    # If already paid, allow re-download without charge
    if draft.get("isPaid"):
        try:
            pdf_bytes = generate_scheme_pdf(draft["scheme"])
            scheme_data = draft["scheme"]
            subject = scheme_data.get("subjectName", "Subject").replace(" ", "_")
            grade_name = scheme_data.get("gradeName", "Grade").replace(" ", "_")
            term = scheme_data.get("term", 1)
            filename = f"Scheme_{subject}_{grade_name}_Term{term}.pdf"

            await db.scheme_drafts.update_one(
                {"_id": ObjectId(draft_id)},
                {"$inc": {"downloadCount": 1}, "$set": {"lastDownloadedAt": datetime.utcnow()}}
            )
            return StreamingResponse(
                BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Content-Length": str(len(pdf_bytes)),
                }
            )
        except Exception as e:
            logger.error(f"Error re-downloading scheme draft: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate PDF")

    # First download — charge wallet
    firebase_uid = user.get("firebaseUid")
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Invalid user session")

    user_profile = await db.users.find_one({"firebaseUid": firebase_uid})
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    if user_profile.get("walletBalance", 0) < SCHEME_DOWNLOAD_COST:
        raise HTTPException(status_code=402, detail={
            "message": "Insufficient wallet balance",
            "required": SCHEME_DOWNLOAD_COST,
            "current": user_profile.get("walletBalance", 0),
        })

    import uuid as uuid_lib
    ledger_ref = f"SCHEME-{uuid_lib.uuid4().hex[:12].upper()}"

    # Ledger entry first (source of truth)
    scheme_data = draft["scheme"]
    try:
        await db.wallet_ledger.insert_one({
            "userId": user["id"],
            "type": "DEBIT",
            "amount": SCHEME_DOWNLOAD_COST,
            "reference": ledger_ref,
            "source": "SCHEME_DOWNLOAD",
            "description": f"Scheme of Work — {scheme_data.get('subjectName', '')} Term {scheme_data.get('term', 1)}",
            "createdAt": datetime.utcnow(),
        })
    except Exception:
        raise HTTPException(status_code=500, detail="Payment processing error. Please try again.")

    # Atomic deduction
    result = await db.users.update_one(
        {"firebaseUid": firebase_uid, "walletBalance": {"$gte": SCHEME_DOWNLOAD_COST}},
        {"$inc": {"walletBalance": -SCHEME_DOWNLOAD_COST}},
    )
    if result.modified_count == 0:
        await db.wallet_ledger.delete_one({"reference": ledger_ref})
        raise HTTPException(status_code=402, detail="Insufficient wallet balance")

    await db.wallets.update_one(
        {"userId": user["id"]},
        {"$inc": {"balance": -SCHEME_DOWNLOAD_COST}, "$set": {"updatedAt": datetime.utcnow()}},
        upsert=True,
    )

    # Generate PDF
    try:
        pdf_bytes = generate_scheme_pdf(scheme_data)
        subject = scheme_data.get("subjectName", "Subject").replace(" ", "_")
        grade_name = scheme_data.get("gradeName", "Grade").replace(" ", "_")
        term = scheme_data.get("term", 1)
        filename = f"Scheme_{subject}_{grade_name}_Term{term}.pdf"

        # Mark as paid
        await db.scheme_drafts.update_one(
            {"_id": ObjectId(draft_id)},
            {"$set": {
                "status": "finalized",
                "isPaid": True,
                "paidAt": datetime.utcnow(),
                "paymentReference": ledger_ref,
                "lastDownloadedAt": datetime.utcnow(),
            }, "$inc": {"downloadCount": 1}}
        )

        updated_user = await db.users.find_one({"firebaseUid": firebase_uid})
        new_balance = updated_user.get("walletBalance", 0) if updated_user else 0

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
                "X-New-Balance": str(new_balance),
            }
        )
    except Exception as e:
        # Refund
        await db.users.update_one(
            {"firebaseUid": firebase_uid},
            {"$inc": {"walletBalance": SCHEME_DOWNLOAD_COST}},
        )
        await db.wallet_ledger.delete_one({"reference": ledger_ref})
        await db.wallets.update_one(
            {"userId": user["id"]},
            {"$inc": {"balance": SCHEME_DOWNLOAD_COST}, "$set": {"updatedAt": datetime.utcnow()}},
        )
        logger.error(f"Scheme draft PDF failed, refunded: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF. Payment refunded.")

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
async def admin_get_subjects(gradeId: Optional[str] = None, user: dict = Depends(verify_admin)):
    """Get all subjects, optionally filtered by gradeId, sorted alphabetically"""
    if gradeId:
        query = {"gradeIds": gradeId}
    else:
        query = {}
    subjects = await db.subjects.find(query).sort("name", 1).to_list(500)
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
    strands = await db.strands.find(query).to_list(2000)
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
    substrands = await db.substrands.find(query).to_list(2000)
    return {"success": True, "substrands": [serialize_doc(s) for s in substrands]}

@api_router.post("/admin/substrands")
async def admin_create_substrand(substrand: SubStrand, user: dict = Depends(verify_admin)):
    result = await db.substrands.insert_one(substrand.dict(exclude={"id"}))
    new_id = str(result.inserted_id)
    # Auto-sync lesson SLOs if number_of_lessons was set
    if substrand.number_of_lessons and substrand.number_of_lessons >= 1:
        await sync_lesson_slos_for_substrand(db, new_id)
    return {"success": True, "id": new_id}

@api_router.put("/admin/substrands/{substrand_id}")
async def admin_update_substrand(substrand_id: str, substrand: SubStrand, user: dict = Depends(verify_admin)):
    # Only update fields that were explicitly provided (not None)
    update_data = {k: v for k, v in substrand.dict(exclude={"id"}).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    await db.substrands.update_one(
        {"_id": ObjectId(substrand_id)},
        {"$set": update_data}
    )
    # Auto-sync lesson SLOs if number_of_lessons changed
    if "number_of_lessons" in update_data:
        await sync_lesson_slos_for_substrand(db, substrand_id)
    return {"success": True}

@api_router.delete("/admin/substrands/{substrand_id}")
async def admin_delete_substrand(substrand_id: str, user: dict = Depends(verify_admin)):
    await db.substrands.delete_one({"_id": ObjectId(substrand_id)})
    # Clean up related data
    await db.substrand_lessons.delete_many({"substrand_id": substrand_id})
    await db.lesson_slos.delete_many({"substrandId": substrand_id})
    return {"success": True}

# ==================== SUBSTRAND LESSONS ====================

@api_router.get("/substrands/{substrand_id}/lessons")
async def get_substrand_lessons(substrand_id: str, user: dict = Depends(verify_token)):
    """Get all configured lessons for a substrand."""
    lessons = await db.substrand_lessons.find(
        {"substrand_id": substrand_id}
    ).sort("lesson_number", 1).to_list(200)
    return {"success": True, "lessons": [serialize_doc(l) for l in lessons]}

@api_router.post("/substrands/{substrand_id}/lessons/generate")
async def generate_substrand_lessons(substrand_id: str, user: dict = Depends(verify_admin)):
    """Auto-generate empty lesson slots based on number_of_lessons.
    Only creates missing slots — does NOT delete existing ones."""
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")

    num = substrand.get("number_of_lessons")
    if not num or num < 1:
        raise HTTPException(status_code=400, detail="Set number_of_lessons on the substrand first (>= 1)")

    # Find existing lesson numbers
    existing = await db.substrand_lessons.find(
        {"substrand_id": substrand_id}
    ).to_list(200)
    existing_nums = {l["lesson_number"] for l in existing}

    created = 0
    for i in range(1, num + 1):
        if i not in existing_nums:
            await db.substrand_lessons.insert_one({
                "substrand_id": substrand_id,
                "lesson_number": i,
                "specific_outcomes": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })
            created += 1

    # Warn if existing lessons exceed the number
    extra = [l for l in existing if l["lesson_number"] > num]
    warning = ""
    if extra:
        warning = f" Warning: {len(extra)} lesson(s) exist beyond the configured {num}. Review manually."

    all_lessons = await db.substrand_lessons.find(
        {"substrand_id": substrand_id}
    ).sort("lesson_number", 1).to_list(200)

    return {
        "success": True,
        "message": f"Created {created} lesson slot(s).{warning}",
        "lessons": [serialize_doc(l) for l in all_lessons]
    }

@api_router.patch("/substrand-lessons/{lesson_id}")
async def update_substrand_lesson(lesson_id: str, lesson: SubstrandLesson, user: dict = Depends(verify_admin)):
    """Update a specific lesson's outcomes (max 2)."""
    outcomes = [o.strip() for o in lesson.specific_outcomes if o.strip()]
    if len(outcomes) > 2:
        raise HTTPException(status_code=400, detail="Maximum 2 specific outcomes per lesson")
    if len(outcomes) < 1:
        raise HTTPException(status_code=400, detail="At least 1 specific outcome is required")

    await db.substrand_lessons.update_one(
        {"_id": ObjectId(lesson_id)},
        {"$set": {
            "specific_outcomes": outcomes,
            "lesson_number": lesson.lesson_number,
            "updated_at": datetime.utcnow(),
        }}
    )
    return {"success": True}

@api_router.delete("/substrand-lessons/{lesson_id}")
async def delete_substrand_lesson(lesson_id: str, user: dict = Depends(verify_admin)):
    """Delete a single lesson slot."""
    await db.substrand_lessons.delete_one({"_id": ObjectId(lesson_id)})
    return {"success": True}

@api_router.get("/substrands/{substrand_id}/lesson-validation")
async def validate_substrand_lessons(substrand_id: str, user: dict = Depends(verify_token)):
    """Validate that a substrand's lessons are fully configured."""
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")

    num = substrand.get("number_of_lessons")
    if not num:
        return {"success": True, "valid": False, "useFallback": True,
                "message": "number_of_lessons not set — will use SLO fallback"}

    lessons = await db.substrand_lessons.find(
        {"substrand_id": substrand_id}
    ).sort("lesson_number", 1).to_list(200)

    errors = []
    if len(lessons) != num:
        errors.append(f"Expected {num} lessons but found {len(lessons)}")

    # Check for duplicates
    nums = [l["lesson_number"] for l in lessons]
    if len(set(nums)) != len(nums):
        errors.append("Duplicate lesson numbers detected")

    # Check each lesson has outcomes
    incomplete = [l["lesson_number"] for l in lessons if not l.get("specific_outcomes")]
    if incomplete:
        errors.append(f"Lessons {incomplete} have no specific outcomes")

    if errors:
        return {"success": True, "valid": False, "useFallback": False,
                "errors": errors,
                "message": f"Substrand '{substrand['name']}' has {len(errors)} issue(s)"}

    return {"success": True, "valid": True, "useFallback": False,
            "message": "All lessons properly configured"}

# ==================== LESSON SLO ENDPOINTS ====================

@api_router.get("/admin/lesson-slos/{substrand_id}")
async def admin_get_lesson_slos(substrand_id: str, user: dict = Depends(verify_admin)):
    """Get all active lesson SLOs for a substrand. Auto-syncs if missing."""
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")

    num = substrand.get("number_of_lessons")
    if num and num >= 1:
        # Auto-sync: create missing lesson SLOs if needed
        await sync_lesson_slos_for_substrand(db, substrand_id)

    slos = await get_active_lesson_slos(db, substrand_id)
    return {"success": True, "lessonSlos": slos, "numberOfLessons": num or 0}


@api_router.put("/admin/lesson-slos/{substrand_id}/{lesson_number}")
async def admin_upsert_lesson_slo(
    substrand_id: str, lesson_number: int, body: dict, user: dict = Depends(verify_admin)
):
    """Create or update a single lesson SLO. Marks it as admin-edited (isDraft=False)."""
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")

    num = substrand.get("number_of_lessons", 0)
    if lesson_number < 1 or (num and lesson_number > num):
        raise HTTPException(status_code=400, detail=f"Lesson number must be between 1 and {num}")

    update_fields = {
        "substrandId": substrand_id,
        "strandId": substrand.get("strandId", ""),
        "lessonNumber": lesson_number,
        "isDraft": False,
        "isAutoGenerated": False,
        "isActive": True,
        "updatedAt": datetime.utcnow(),
    }
    # Allow updating any of the curriculum fields
    for field in [
        "outcome", "description", "parentSloId", "title",
        "keyInquiryQuestions", "learningExperiences", "learningResources",
        "assessmentMethods", "coreCompetencies", "values", "pcis",
    ]:
        if field in body:
            update_fields[field] = body[field]

    result = await db.lesson_slos.update_one(
        {"substrandId": substrand_id, "lessonNumber": lesson_number},
        {"$set": update_fields, "$setOnInsert": {"createdAt": datetime.utcnow()}},
        upsert=True,
    )
    action = "created" if result.upserted_id else "updated"
    return {"success": True, "action": action}


@api_router.post("/admin/lesson-slos/{substrand_id}/bulk")
async def admin_bulk_upsert_lesson_slos(
    substrand_id: str, body: dict, user: dict = Depends(verify_admin)
):
    """Bulk upsert lesson SLOs. Expects { lessonSlos: [ {lessonNumber, outcome, ...}, ... ] }"""
    items = body.get("lessonSlos", [])
    if not items:
        raise HTTPException(status_code=400, detail="No lesson SLOs provided")

    updated = 0
    for item in items:
        ln = item.get("lessonNumber")
        if not ln:
            continue
        update_fields = {
            "substrandId": substrand_id,
            "lessonNumber": ln,
            "isDraft": False,
            "isAutoGenerated": False,
            "isActive": True,
            "updatedAt": datetime.utcnow(),
        }
        for field in [
            "outcome", "description", "parentSloId", "title",
            "keyInquiryQuestions", "learningExperiences", "learningResources",
            "assessmentMethods", "coreCompetencies", "values", "pcis",
        ]:
            if field in item:
                update_fields[field] = item[field]

        await db.lesson_slos.update_one(
            {"substrandId": substrand_id, "lessonNumber": ln},
            {"$set": update_fields, "$setOnInsert": {"createdAt": datetime.utcnow()}},
            upsert=True,
        )
        updated += 1

    return {"success": True, "updated": updated}


@api_router.post("/admin/lesson-slos/{substrand_id}/regenerate")
async def admin_regenerate_lesson_slos(substrand_id: str, user: dict = Depends(verify_admin)):
    """Regenerate auto-generated draft lesson SLOs. Preserves admin-edited ones."""
    result = await regenerate_lesson_slos(db, substrand_id, force=True)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    slos = await get_active_lesson_slos(db, substrand_id)
    return {"success": True, "result": result, "lessonSlos": slos}


@api_router.post("/admin/lesson-slos/{substrand_id}/sync")
async def admin_sync_lesson_slos(substrand_id: str, user: dict = Depends(verify_admin)):
    """Sync lesson SLOs to match current number_of_lessons (non-destructive)."""
    result = await sync_lesson_slos_for_substrand(db, substrand_id)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    slos = await get_active_lesson_slos(db, substrand_id)
    return {"success": True, "result": result, "lessonSlos": slos}


@api_router.post("/admin/lesson-slos/bootstrap")
async def admin_bootstrap_lesson_slos(user: dict = Depends(verify_admin)):
    """Migration: scan all substrands and generate missing lesson SLOs."""
    stats = await bootstrap_missing_lesson_slos(db)
    return {"success": True, "stats": stats}

# ==================== LESSON SLO SLOTS (Phase 3) ====================

@api_router.get("/admin/lesson-slots/{substrand_id}")
async def admin_get_lesson_slots(substrand_id: str, user: dict = Depends(verify_admin)):
    """Get all lesson SLO slots for a substrand.
    Auto-generates slots if they don't exist yet but number_of_lessons is set.
    """
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")

    num = substrand.get("number_of_lessons")
    if not num or int(num) < 1:
        return {
            "success": True,
            "slots": [],
            "number_of_lessons": 0,
            "message": "Set number_of_lessons on this substrand first"
        }

    slots = await get_slots_for_substrand(db, substrand_id)
    return {
        "success": True,
        "slots": slots,
        "number_of_lessons": int(num),
    }


@api_router.post("/admin/lesson-slots/{substrand_id}/generate")
async def admin_generate_lesson_slots(substrand_id: str, user: dict = Depends(verify_admin)):
    """Generate/regenerate lesson SLO slots from number_of_lessons.
    Preserves customised slots. Fills gaps with fallback.
    """
    result = await generate_slots_for_substrand(db, substrand_id)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result.get("message", result["error"]))
    slots = await get_slots_for_substrand(db, substrand_id)
    return {"success": True, "result": result, "slots": slots}


@api_router.put("/admin/lesson-slots/{substrand_id}/{slot_index}")
async def admin_update_lesson_slot(
    substrand_id: str, slot_index: int, body: dict, user: dict = Depends(verify_admin)
):
    """Update a single lesson SLO slot. Marks it as customised."""
    result = await update_slot(db, substrand_id, slot_index, body)
    if result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@api_router.post("/admin/lesson-slots/{substrand_id}/{slot_index}/clear")
async def admin_clear_lesson_slot(
    substrand_id: str, slot_index: int, user: dict = Depends(verify_admin)
):
    """Clear a slot back to fallback state."""
    result = await clear_slot(db, substrand_id, slot_index)
    return result


# Teacher-facing: get slots (read-only, for lesson plan context)
@api_router.get("/lesson-slots/{substrand_id}")
async def get_lesson_slots_public(substrand_id: str, user: dict = Depends(verify_token)):
    """Get lesson SLO slots for a substrand (teacher read-only)."""
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")
    num = substrand.get("number_of_lessons")
    if not num or int(num) < 1:
        return {"success": True, "slots": [], "number_of_lessons": 0}
    slots = await get_slots_for_substrand(db, substrand_id)
    return {"success": True, "slots": slots, "number_of_lessons": int(num)}

# SLOs
@api_router.get("/admin/slos")
async def admin_get_slos(substrandId: Optional[str] = None, user: dict = Depends(verify_admin)):
    query = {"substrandId": substrandId} if substrandId else {}
    slos = await db.slos.find(query).to_list(100)
    return {"success": True, "slos": [serialize_doc(s) for s in slos]}

# Helper function to create default SLO mapping
async def create_default_slo_mapping(slo_id: str):
    """Create default SLO mapping with common competencies, values, and PCIs"""
    # Get default competencies (3 common ones)
    default_competency_names = [
        "Critical Thinking and Problem Solving",
        "Communication and Collaboration",
        "Learning to Learn"
    ]
    competency_ids = []
    for name in default_competency_names:
        comp = await db.competencies.find_one({"name": name})
        if comp:
            competency_ids.append(str(comp["_id"]))
    
    # Get default values (3 common ones)
    default_value_names = ["Responsibility", "Respect", "Integrity"]
    value_ids = []
    for name in default_value_names:
        val = await db.values.find_one({"name": name})
        if val:
            value_ids.append(str(val["_id"]))
    
    # Get default PCIs (2 common ones)
    default_pci_names = ["Life Skills", "Citizenship"]
    pci_ids = []
    for name in default_pci_names:
        pci = await db.pcis.find_one({"name": name})
        if pci:
            pci_ids.append(str(pci["_id"]))
    
    # Create the mapping
    mapping_doc = {
        "sloId": slo_id,
        "competencyIds": competency_ids,
        "valueIds": value_ids,
        "pciIds": pci_ids,
        "assessmentIds": []
    }
    await db.slo_mappings.insert_one(mapping_doc)
    return mapping_doc

@api_router.post("/admin/slos")
async def admin_create_slo(slo: SLO, user: dict = Depends(verify_admin)):
    """Create a new SLO and automatically add default mappings for competencies, values, and PCIs"""
    result = await db.slos.insert_one(slo.dict(exclude={"id"}))
    slo_id = str(result.inserted_id)
    
    # Automatically create default SLO mapping
    await create_default_slo_mapping(slo_id)
    
    return {"success": True, "id": slo_id, "message": "SLO created with default competency/value/PCI mappings"}

@api_router.put("/admin/slos/{slo_id}")
async def admin_update_slo(slo_id: str, slo: SLO, user: dict = Depends(verify_admin)):
    await db.slos.update_one({"_id": ObjectId(slo_id)}, {"$set": slo.dict(exclude={"id"})})
    return {"success": True}

@api_router.delete("/admin/slos/{slo_id}")
async def admin_delete_slo(slo_id: str, user: dict = Depends(verify_admin)):
    """Delete an SLO and its associated mapping"""
    await db.slos.delete_one({"_id": ObjectId(slo_id)})
    # Also delete the SLO mapping
    await db.slo_mappings.delete_one({"sloId": slo_id})
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

# Learning Activities (used in lesson plan generation)
@api_router.get("/admin/learning-activities")
async def admin_get_learning_activities(substrandId: Optional[str] = None, user: dict = Depends(verify_admin)):
    """Get all learning activities or filter by substrand"""
    query = {}
    if substrandId:
        query["substrandId"] = substrandId
    activities = await db.learning_activities.find(query).to_list(500)
    return {"success": True, "learning_activities": [serialize_doc(a) for a in activities]}

@api_router.get("/admin/learning-activities/{activity_id}")
async def admin_get_learning_activity(activity_id: str, user: dict = Depends(verify_admin)):
    """Get a single learning activity by ID"""
    activity = await db.learning_activities.find_one({"_id": ObjectId(activity_id)})
    if not activity:
        raise HTTPException(status_code=404, detail="Learning activity not found")
    return {"success": True, "learning_activity": serialize_doc(activity)}

@api_router.get("/admin/learning-activities/by-substrand/{substrand_id}")
async def admin_get_learning_activity_by_substrand(substrand_id: str, user: dict = Depends(verify_admin)):
    """Get learning activities for a specific substrand"""
    activity = await db.learning_activities.find_one({"substrandId": substrand_id})
    if activity:
        return {"success": True, "learning_activity": serialize_doc(activity), "exists": True}
    return {"success": True, "learning_activity": None, "exists": False}

@api_router.post("/admin/learning-activities")
async def admin_create_learning_activity(activity: LearningActivities, user: dict = Depends(verify_admin)):
    """Create a new learning activity for a substrand"""
    # Check if activities already exist for this substrand
    existing = await db.learning_activities.find_one({"substrandId": activity.substrandId})
    if existing:
        raise HTTPException(status_code=400, detail="Learning activities already exist for this substrand. Use PUT to update.")
    
    result = await db.learning_activities.insert_one(activity.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

@api_router.put("/admin/learning-activities/{activity_id}")
async def admin_update_learning_activity(activity_id: str, activity: LearningActivities, user: dict = Depends(verify_admin)):
    """Update an existing learning activity"""
    update_data = activity.dict(exclude={"id"})
    result = await db.learning_activities.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Learning activity not found")
    return {"success": True}

@api_router.put("/admin/learning-activities/by-substrand/{substrand_id}")
async def admin_upsert_learning_activity(substrand_id: str, activity: LearningActivities, user: dict = Depends(verify_admin)):
    """Create or update learning activities for a substrand (upsert)"""
    update_data = activity.dict(exclude={"id"})
    update_data["substrandId"] = substrand_id
    
    result = await db.learning_activities.update_one(
        {"substrandId": substrand_id},
        {"$set": update_data},
        upsert=True
    )
    
    if result.upserted_id:
        return {"success": True, "id": str(result.upserted_id), "created": True}
    return {"success": True, "created": False, "updated": True}

@api_router.delete("/admin/learning-activities/{activity_id}")
async def admin_delete_learning_activity(activity_id: str, user: dict = Depends(verify_admin)):
    """Delete a learning activity"""
    result = await db.learning_activities.delete_one({"_id": ObjectId(activity_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Learning activity not found")
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

# SLO Mappings (link SLOs to competencies, values, PCIs)
@api_router.get("/admin/slo-mappings/{slo_id}")
async def admin_get_slo_mapping(slo_id: str, user: dict = Depends(verify_admin)):
    """Get the mapping for a specific SLO"""
    mapping = await db.slo_mappings.find_one({"sloId": slo_id})
    if not mapping:
        return {"success": True, "mapping": None, "exists": False}
    return {"success": True, "mapping": serialize_doc(mapping), "exists": True}

@api_router.put("/admin/slo-mappings/{slo_id}")
async def admin_update_slo_mapping(slo_id: str, mapping_data: dict, user: dict = Depends(verify_admin)):
    """Update or create SLO mapping (upsert)"""
    update_doc = {
        "sloId": slo_id,
        "competencyIds": mapping_data.get("competencyIds", []),
        "valueIds": mapping_data.get("valueIds", []),
        "pciIds": mapping_data.get("pciIds", []),
        "assessmentIds": mapping_data.get("assessmentIds", [])
    }
    
    result = await db.slo_mappings.update_one(
        {"sloId": slo_id},
        {"$set": update_doc},
        upsert=True
    )
    
    if result.upserted_id:
        return {"success": True, "created": True, "id": str(result.upserted_id)}
    return {"success": True, "updated": True}

# Assessments
@api_router.get("/admin/assessments")
async def admin_get_assessments(user: dict = Depends(verify_admin)):
    assessments = await db.assessments.find().to_list(100)
    return {"success": True, "assessments": [serialize_doc(a) for a in assessments]}

@api_router.post("/admin/assessments")
async def admin_create_assessment(assessment: Assessment, user: dict = Depends(verify_admin)):
    result = await db.assessments.insert_one(assessment.dict(exclude={"id"}))
    return {"success": True, "id": str(result.inserted_id)}

@api_router.put("/admin/assessments/{assessment_id}")
async def admin_update_assessment(assessment_id: str, assessment: Assessment, user: dict = Depends(verify_admin)):
    update_data = {k: v for k, v in assessment.dict(exclude={"id"}).items() if v is not None}
    await db.assessments.update_one({"_id": ObjectId(assessment_id)}, {"$set": update_data})
    return {"success": True, "updated": True}

@api_router.delete("/admin/assessments/{assessment_id}")
async def admin_delete_assessment(assessment_id: str, user: dict = Depends(verify_admin)):
    await db.assessments.delete_one({"_id": ObjectId(assessment_id)})
    return {"success": True}

@api_router.post("/admin/assessments/bulk")
async def admin_bulk_create_assessments(request: BulkCreateRequest, user: dict = Depends(verify_admin)):
    """Create multiple assessment methods at once. parentId is ignored but required by schema."""
    created_ids = []
    for item in request.items:
        name = item.name.strip()
        if not name:
            continue
        existing = await db.assessments.find_one({"name": name})
        if existing:
            continue
        result = await db.assessments.insert_one({
            "name": name,
            "description": item.description or name
        })
        created_ids.append(str(result.inserted_id))
    return {
        "success": True,
        "message": f"Created {len(created_ids)} assessment methods",
        "createdIds": created_ids
    }

# SLO Mappings — POST and bulk operations
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

# ==================== REFERENCE DATA ENDPOINT ====================

@api_router.get("/admin/reference-data")
async def admin_get_reference_data(user: dict = Depends(verify_admin)):
    """Get all competencies, values, and PCIs for mapping selection"""
    competencies = await db.competencies.find().to_list(100)
    values = await db.values.find().to_list(100)
    pcis = await db.pcis.find().to_list(100)
    
    return {
        "success": True,
        "competencies": [serialize_doc(c) for c in competencies],
        "values": [serialize_doc(v) for v in values],
        "pcis": [serialize_doc(p) for p in pcis]
    }

# ==================== BULK SLO MAPPING UPDATE ====================

class BulkSloMappingRequest(BaseModel):
    sloIds: List[str]
    competencyIds: List[str]
    valueIds: List[str]
    pciIds: List[str]

@api_router.put("/admin/slo-mappings/bulk")
async def admin_bulk_update_slo_mappings(request: BulkSloMappingRequest, user: dict = Depends(verify_admin)):
    """Update mappings for multiple SLOs at once"""
    updated_count = 0
    created_count = 0
    
    for slo_id in request.sloIds:
        # Check if SLO exists
        slo = await db.slos.find_one({"_id": ObjectId(slo_id)})
        if not slo:
            continue
        
        mapping_data = {
            "sloId": slo_id,
            "competencyIds": request.competencyIds,
            "valueIds": request.valueIds,
            "pciIds": request.pciIds,
            "assessmentIds": []
        }
        
        existing = await db.slo_mappings.find_one({"sloId": slo_id})
        if existing:
            await db.slo_mappings.update_one(
                {"sloId": slo_id},
                {"$set": mapping_data}
            )
            updated_count += 1
        else:
            await db.slo_mappings.insert_one(mapping_data)
            created_count += 1
    
    return {
        "success": True,
        "message": f"Updated {updated_count} mappings, created {created_count} new mappings",
        "updated": updated_count,
        "created": created_count
    }

# ==================== MOVE/REASSIGN ENDPOINTS (with CASCADE) ====================

class MoveStrandRequest(BaseModel):
    targetSubjectId: str

class MoveSubstrandRequest(BaseModel):
    targetStrandId: str

class MoveSloRequest(BaseModel):
    targetSubstrandId: str

class ChangeSubjectGradeRequest(BaseModel):
    targetGradeId: str
    removeFromOtherGrades: bool = False

@api_router.put("/admin/strands/{strand_id}/move")
async def admin_move_strand(strand_id: str, request: MoveStrandRequest, user: dict = Depends(verify_admin)):
    """
    Move a strand to a different subject.
    CASCADE: All substrands, SLOs, SLO mappings, and learning activities move with it.
    """
    # Verify strand exists
    strand = await db.strands.find_one({"_id": ObjectId(strand_id)})
    if not strand:
        raise HTTPException(status_code=404, detail="Strand not found")
    
    # Verify target subject exists
    target_subject = await db.subjects.find_one({"_id": ObjectId(request.targetSubjectId)})
    if not target_subject:
        raise HTTPException(status_code=404, detail="Target subject not found")
    
    old_subject_id = strand.get("subjectId")
    
    # Update the strand's subjectId
    await db.strands.update_one(
        {"_id": ObjectId(strand_id)},
        {"$set": {"subjectId": request.targetSubjectId}}
    )
    
    # Count affected items for response
    substrands = await db.substrands.find({"strandId": strand_id}).to_list(1000)
    substrand_count = len(substrands)
    
    slo_count = 0
    activity_count = 0
    for ss in substrands:
        ss_id = str(ss["_id"])
        slos = await db.slos.count_documents({"substrandId": ss_id})
        slo_count += slos
        activities = await db.learning_activities.count_documents({"substrandId": ss["_id"]})
        activity_count += activities
    
    return {
        "success": True,
        "message": f"Strand moved successfully with all children",
        "moved": {
            "strand": strand.get("name"),
            "fromSubject": old_subject_id,
            "toSubject": request.targetSubjectId,
            "cascadedSubstrands": substrand_count,
            "cascadedSLOs": slo_count,
            "cascadedActivities": activity_count
        }
    }

@api_router.put("/admin/substrands/{substrand_id}/move")
async def admin_move_substrand(substrand_id: str, request: MoveSubstrandRequest, user: dict = Depends(verify_admin)):
    """
    Move a substrand to a different strand.
    CASCADE: All SLOs, SLO mappings, and learning activities move with it.
    """
    # Verify substrand exists
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")
    
    # Verify target strand exists
    target_strand = await db.strands.find_one({"_id": ObjectId(request.targetStrandId)})
    if not target_strand:
        raise HTTPException(status_code=404, detail="Target strand not found")
    
    old_strand_id = substrand.get("strandId")
    
    # Update the substrand's strandId
    await db.substrands.update_one(
        {"_id": ObjectId(substrand_id)},
        {"$set": {"strandId": request.targetStrandId}}
    )
    
    # Count affected items
    slo_count = await db.slos.count_documents({"substrandId": substrand_id})
    activity_count = await db.learning_activities.count_documents({"substrandId": ObjectId(substrand_id)})
    
    return {
        "success": True,
        "message": f"Substrand moved successfully with all children",
        "moved": {
            "substrand": substrand.get("name"),
            "fromStrand": old_strand_id,
            "toStrand": request.targetStrandId,
            "cascadedSLOs": slo_count,
            "cascadedActivities": activity_count
        }
    }

@api_router.put("/admin/slos/{slo_id}/move")
async def admin_move_slo(slo_id: str, request: MoveSloRequest, user: dict = Depends(verify_admin)):
    """
    Move an SLO to a different substrand.
    CASCADE: SLO mapping stays with the SLO.
    """
    # Verify SLO exists
    slo = await db.slos.find_one({"_id": ObjectId(slo_id)})
    if not slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    
    # Verify target substrand exists
    target_substrand = await db.substrands.find_one({"_id": ObjectId(request.targetSubstrandId)})
    if not target_substrand:
        raise HTTPException(status_code=404, detail="Target substrand not found")
    
    old_substrand_id = slo.get("substrandId")
    
    # Update the SLO's substrandId
    await db.slos.update_one(
        {"_id": ObjectId(slo_id)},
        {"$set": {"substrandId": request.targetSubstrandId}}
    )
    
    # Check if SLO mapping exists
    has_mapping = await db.slo_mappings.find_one({"sloId": slo_id}) is not None
    
    return {
        "success": True,
        "message": f"SLO moved successfully",
        "moved": {
            "slo": slo.get("name"),
            "fromSubstrand": old_substrand_id,
            "toSubstrand": request.targetSubstrandId,
            "mappingPreserved": has_mapping
        }
    }

@api_router.put("/admin/subjects/{subject_id}/change-grade")
async def admin_change_subject_grade(subject_id: str, request: ChangeSubjectGradeRequest, user: dict = Depends(verify_admin)):
    """
    Change a subject's grade assignment.
    Can add to new grade or replace all grade assignments.
    """
    # Verify subject exists
    subject = await db.subjects.find_one({"_id": ObjectId(subject_id)})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Verify target grade exists
    target_grade = await db.grades.find_one({"_id": ObjectId(request.targetGradeId)})
    if not target_grade:
        raise HTTPException(status_code=404, detail="Target grade not found")
    
    old_grade_ids = subject.get("gradeIds", [])
    
    if request.removeFromOtherGrades:
        # Replace all grade assignments with just the target grade
        new_grade_ids = [request.targetGradeId]
    else:
        # Add to existing grades if not already present
        new_grade_ids = list(set(old_grade_ids + [request.targetGradeId]))
    
    await db.subjects.update_one(
        {"_id": ObjectId(subject_id)},
        {"$set": {"gradeIds": new_grade_ids}}
    )
    
    return {
        "success": True,
        "message": f"Subject grade assignment updated",
        "updated": {
            "subject": subject.get("name"),
            "oldGradeIds": old_grade_ids,
            "newGradeIds": new_grade_ids
        }
    }

# ==================== BULK CREATE ENDPOINTS ====================

@api_router.post("/admin/strands/bulk")
async def admin_bulk_create_strands(request: BulkCreateRequest, user: dict = Depends(verify_admin)):
    """Create multiple strands at once for a subject (skips duplicates)"""
    subject = await db.subjects.find_one({"_id": ObjectId(request.parentId)})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    existing_names = set()
    existing = await db.strands.find({"subjectId": request.parentId}).to_list(500)
    for s in existing:
        existing_names.add(s["name"].strip().lower())
    
    created_ids = []
    skipped = 0
    for item in request.items:
        name = item.name.strip()
        if not name:
            continue
        if name.lower() in existing_names:
            skipped += 1
            continue
        existing_names.add(name.lower())
        result = await db.strands.insert_one({
            "name": name,
            "subjectId": request.parentId
        })
        created_ids.append(str(result.inserted_id))
    
    msg = f"Created {len(created_ids)} strands"
    if skipped:
        msg += f" ({skipped} duplicates skipped)"
    return {"success": True, "message": msg, "createdIds": created_ids}

@api_router.post("/admin/substrands/bulk")
async def admin_bulk_create_substrands(request: BulkCreateRequest, user: dict = Depends(verify_admin)):
    """Create multiple substrands at once for a strand (skips duplicates)"""
    strand = await db.strands.find_one({"_id": ObjectId(request.parentId)})
    if not strand:
        raise HTTPException(status_code=404, detail="Strand not found")
    
    existing_names = set()
    existing = await db.substrands.find({"strandId": request.parentId}).to_list(500)
    for s in existing:
        existing_names.add(s["name"].strip().lower())
    
    created_ids = []
    skipped = 0
    for item in request.items:
        name = item.name.strip()
        if not name:
            continue
        if name.lower() in existing_names:
            skipped += 1
            continue
        existing_names.add(name.lower())
        result = await db.substrands.insert_one({
            "name": name,
            "strandId": request.parentId
        })
        created_ids.append(str(result.inserted_id))
    
    msg = f"Created {len(created_ids)} substrands"
    if skipped:
        msg += f" ({skipped} duplicates skipped)"
    return {"success": True, "message": msg, "createdIds": created_ids}

@api_router.post("/admin/slos/bulk")
async def admin_bulk_create_slos(request: BulkCreateRequest, user: dict = Depends(verify_admin)):
    """Create multiple SLOs at once for a substrand (skips duplicates), with automatic SLO mappings"""
    substrand = await db.substrands.find_one({"_id": ObjectId(request.parentId)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")
    
    existing_names = set()
    existing = await db.slos.find({"substrandId": request.parentId}).to_list(500)
    for s in existing:
        existing_names.add(s["name"].strip().lower())
    
    created_ids = []
    skipped = 0
    for item in request.items:
        name = item.name.strip()
        if not name:
            continue
        if name.lower() in existing_names:
            skipped += 1
            continue
        existing_names.add(name.lower())
        result = await db.slos.insert_one({
            "name": name,
            "description": item.description or name,
            "substrandId": request.parentId
        })
        slo_id = str(result.inserted_id)
        created_ids.append(slo_id)
        await create_default_slo_mapping(slo_id)
    
    msg = f"Created {len(created_ids)} SLOs with mappings"
    if skipped:
        msg += f" ({skipped} duplicates skipped)"
    return {"success": True, "message": msg, "createdIds": created_ids}

class BulkLearningActivityItem(BaseModel):
    introduction_activities: List[str] = []
    development_activities: List[str] = []
    conclusion_activities: List[str] = []
    extended_activities: List[str] = []

# Keywords that indicate an extended activity
EXTENDED_ACTIVITY_KEYWORDS = [
    "practical", "project", "experiment", "field work", "fieldwork",
    "assignment", "research", "investigation", "survey", "field trip",
    "field study", "hands-on", "hands on"
]

def classify_activities(raw_activities: List[str]) -> tuple:
    """Classify pasted activities into development vs extended.
    Activities containing keywords go to extended_activities, rest to development_activities."""
    development = []
    extended = []
    for activity in raw_activities:
        stripped = activity.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if any(kw in lower for kw in EXTENDED_ACTIVITY_KEYWORDS):
            extended.append(stripped)
        else:
            development.append(stripped)
    return development, extended

@api_router.post("/admin/learning-activities/bulk-update")
async def admin_bulk_update_learning_activities(
    substrand_id: str,
    activities: BulkLearningActivityItem,
    user: dict = Depends(verify_admin)
):
    """Create or update learning activities for a substrand in bulk"""
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")
    
    # Preserve existing introduction and conclusion (DO NOT modify them)
    existing = await db.learning_activities.find_one({"substrandId": ObjectId(substrand_id)})
    
    # Auto-classify development_activities: keyword matches → extended
    raw_dev = [a.strip() for a in activities.development_activities if a.strip()]
    raw_ext = [a.strip() for a in activities.extended_activities if a.strip()]
    
    # Classify from development input
    auto_dev, auto_ext = classify_activities(raw_dev)
    # Also classify from extended input (in case user pasted general ones there)
    auto_dev2, auto_ext2 = classify_activities(raw_ext)
    
    final_dev = auto_dev + auto_dev2
    final_ext = auto_ext + auto_ext2
    
    # Remove duplicates while preserving order
    seen = set()
    deduped_dev = []
    for a in final_dev:
        if a not in seen:
            seen.add(a)
            deduped_dev.append(a)
    deduped_ext = []
    for a in final_ext:
        if a not in seen:
            seen.add(a)
            deduped_ext.append(a)
    
    # introduction and conclusion: use provided values ONLY if non-empty, else preserve existing
    intro = [a.strip() for a in activities.introduction_activities if a.strip()]
    concl = [a.strip() for a in activities.conclusion_activities if a.strip()]
    if not intro and existing:
        intro = existing.get("introduction_activities", [])
    if not concl and existing:
        concl = existing.get("conclusion_activities", [])
    
    update_data = {
        "substrandId": ObjectId(substrand_id),
        "introduction_activities": intro,
        "development_activities": deduped_dev,
        "conclusion_activities": concl,
        "extended_activities": deduped_ext
    }
    
    result = await db.learning_activities.update_one(
        {"substrandId": ObjectId(substrand_id)},
        {"$set": update_data},
        upsert=True
    )
    
    return {
        "success": True,
        "message": f"Learning activities saved. Development: {len(deduped_dev)}, Extended: {len(deduped_ext)}",
        "created": result.upserted_id is not None,
        "classified": {
            "development_count": len(deduped_dev),
            "extended_count": len(deduped_ext)
        }
    }

class BulkLearningActivityPasteRequest(BaseModel):
    items: List[BulkCreateItem]
    parentId: str

@api_router.post("/admin/learning-activities/bulk")
async def admin_bulk_create_learning_activities(
    request: BulkLearningActivityPasteRequest,
    user: dict = Depends(verify_admin)
):
    """Bulk create learning activities from pasted text.
    Auto-classifies: general → development_activities, keyword-matched → extended_activities.
    Does NOT touch introduction_activities or conclusion_activities."""
    substrand_id = request.parentId
    substrand = await db.substrands.find_one({"_id": ObjectId(substrand_id)})
    if not substrand:
        raise HTTPException(status_code=404, detail="Substrand not found")
    
    # Get existing activities to preserve intro/conclusion
    existing = await db.learning_activities.find_one({"substrandId": ObjectId(substrand_id)})
    
    # Parse pasted items and classify
    raw_items = [item.name.strip() for item in request.items if item.name.strip()]
    dev_activities, ext_activities = classify_activities(raw_items)
    
    # Merge with existing (append new, deduplicate)
    existing_dev = existing.get("development_activities", []) if existing else []
    existing_ext = existing.get("extended_activities", []) if existing else []
    
    seen = set(existing_dev + existing_ext)
    new_dev = [a for a in dev_activities if a not in seen]
    for a in new_dev:
        seen.add(a)
    new_ext = [a for a in ext_activities if a not in seen]
    
    final_dev = existing_dev + new_dev
    final_ext = existing_ext + new_ext
    
    update_data = {
        "substrandId": ObjectId(substrand_id),
        "development_activities": final_dev,
        "extended_activities": final_ext,
    }
    
    # Preserve intro/conclusion untouched
    if existing:
        update_data["introduction_activities"] = existing.get("introduction_activities", [])
        update_data["conclusion_activities"] = existing.get("conclusion_activities", [])
    
    await db.learning_activities.update_one(
        {"substrandId": ObjectId(substrand_id)},
        {"$set": update_data},
        upsert=True
    )
    
    return {
        "success": True,
        "message": f"Added {len(new_dev)} development + {len(new_ext)} extended activities",
        "createdIds": [],
        "classified": {
            "development_added": len(new_dev),
            "extended_added": len(new_ext),
            "total_development": len(final_dev),
            "total_extended": len(final_ext)
        }
    }

# ==================== CURRICULUM HIERARCHY ENDPOINT ====================

@api_router.get("/admin/curriculum-tree")
async def admin_get_curriculum_tree(user: dict = Depends(verify_admin)):
    """Get full curriculum hierarchy for dropdown selections"""
    grades = await db.grades.find().to_list(100)
    subjects = await db.subjects.find().to_list(500)
    strands = await db.strands.find().to_list(1000)
    substrands = await db.substrands.find().to_list(5000)
    
    return {
        "success": True,
        "tree": {
            "grades": [serialize_doc(g) for g in grades],
            "subjects": [serialize_doc(s) for s in subjects],
            "strands": [serialize_doc(s) for s in strands],
            "substrands": [serialize_doc(s) for s in substrands]
        }
    }

# ==================== CURRICULUM IMPORT ENDPOINTS ====================

class ImportSaveRequest(BaseModel):
    subjectId: str
    gradeId: str
    rows: List[Dict[str, Any]]
    filename: str = "manual_import"

@api_router.get("/admin/import/template")
async def get_csv_template(user: dict = Depends(verify_admin)):
    """Download CSV template for curriculum import"""
    csv_content = generate_csv_template()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=curriculum_template.csv"}
    )

@api_router.get("/public/import-template")
async def get_public_csv_template():
    """Download CSV template for curriculum import (public access)"""
    csv_content = generate_csv_template()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=curriculum_template.csv"}
    )

@api_router.post("/admin/import/preview-csv")
async def preview_csv_import(file: UploadFile = File(...), user: dict = Depends(verify_admin)):
    """Upload CSV and preview data before saving"""
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    content = await file.read()
    try:
        text_content = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text_content = content.decode('latin-1')
        except:
            raise HTTPException(status_code=400, detail="Unable to decode file. Please ensure it's a valid CSV.")
    
    result = parse_csv_content(text_content)
    
    return {
        "success": True,
        "preview": result.dict()
    }

@api_router.post("/admin/import/extract-pdf")
async def extract_pdf_to_csv(file: UploadFile = File(...), user: dict = Depends(verify_admin)):
    """Extract curriculum data from PDF and return as previewable data"""
    if not file.filename.endswith(('.pdf', '.PDF')):
        raise HTTPException(status_code=400, detail="File must be a PDF file")
    
    content = await file.read()
    result = extract_curriculum_from_pdf(content)
    
    # Also generate downloadable CSV
    csv_content = rows_to_csv(result.rows)
    
    return {
        "success": True,
        "preview": result.dict(),
        "csv_content": csv_content
    }

@api_router.post("/admin/import/extract-docx")
async def extract_docx_to_csv(file: UploadFile = File(...), user: dict = Depends(verify_admin)):
    """Extract curriculum data from Word document (.docx) and return as previewable data"""
    if not file.filename.endswith(('.docx', '.DOCX')):
        raise HTTPException(status_code=400, detail="File must be a Word document (.docx)")
    
    content = await file.read()
    result = extract_curriculum_from_docx(content)
    
    # Also generate downloadable CSV
    csv_content = rows_to_csv(result.rows)
    
    return {
        "success": True,
        "preview": result.dict(),
        "csv_content": csv_content,
        "filename": file.filename
    }

@api_router.post("/admin/import/save")
async def save_imported_data(request: ImportSaveRequest, user: dict = Depends(verify_admin)):
    """Save imported curriculum data to database"""
    
    logger.info(f"Import save request: {len(request.rows)} rows for subject {request.subjectId}, grade {request.gradeId}")
    
    # Verify subject exists
    subject = await db.subjects.find_one({"_id": ObjectId(request.subjectId)})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Verify grade exists
    grade = await db.grades.find_one({"_id": ObjectId(request.gradeId)})
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    subject_id = str(subject["_id"])
    
    # Get reference data for mapping
    competencies = {c["name"].lower(): str(c["_id"]) async for c in db.competencies.find()}
    values = {v["name"].lower(): str(v["_id"]) async for v in db.values.find()}
    pcis = {p["name"].lower(): str(p["_id"]) async for p in db.pcis.find()}
    
    # Track created items
    stats = {
        "strands_created": 0,
        "substrands_created": 0,
        "slos_created": 0,
        "mappings_created": 0,
        "activities_created": 0
    }
    
    # Group rows by strand and substrand
    strand_cache = {}  # strand_name -> strand_id
    substrand_cache = {}  # strand_name|substrand_name -> substrand_id
    
    for row in request.rows:
        strand_name = row.get("strand_name", "").strip()
        substrand_name = row.get("substrand_name", "").strip()
        slo_name = row.get("slo_name", "").strip()
        
        logger.info(f"Processing row: strand={strand_name}, substrand={substrand_name}, slo={slo_name}")
        
        if not strand_name or not substrand_name or not slo_name:
            logger.warning(f"Skipping row - missing required field: strand={strand_name}, substrand={substrand_name}, slo={slo_name}")
            continue
        
        # Get or create strand
        if strand_name not in strand_cache:
            existing_strand = await db.strands.find_one({
                "name": strand_name,
                "subjectId": subject_id
            })
            if existing_strand:
                strand_cache[strand_name] = str(existing_strand["_id"])
            else:
                result = await db.strands.insert_one({
                    "name": strand_name,
                    "subjectId": subject_id
                })
                strand_cache[strand_name] = str(result.inserted_id)
                stats["strands_created"] += 1
        
        strand_id = strand_cache[strand_name]
        substrand_key = f"{strand_name}|{substrand_name}"
        
        # Get or create substrand
        if substrand_key not in substrand_cache:
            existing_substrand = await db.substrands.find_one({
                "name": substrand_name,
                "strandId": strand_id
            })
            if existing_substrand:
                substrand_cache[substrand_key] = str(existing_substrand["_id"])
            else:
                result = await db.substrands.insert_one({
                    "name": substrand_name,
                    "strandId": strand_id,
                    "number_of_lessons": row.get("number_of_lessons") or None
                })
                substrand_cache[substrand_key] = str(result.inserted_id)
                stats["substrands_created"] += 1
                
                # Create learning activities for new substrand
                activities_data = {
                    "substrandId": result.inserted_id,
                    "introduction_activities": row.get("introduction_activities", []),
                    "development_activities": row.get("development_activities", []),
                    "conclusion_activities": row.get("conclusion_activities", []),
                    "extended_activities": row.get("extended_activities", []),
                    "learning_resources": row.get("learning_resources", []),
                    "assessment_methods": row.get("assessment_methods", [])
                }
                await db.learning_activities.insert_one(activities_data)
                stats["activities_created"] += 1
        
        substrand_id = substrand_cache[substrand_key]
        
        # Create SLO
        slo_result = await db.slos.insert_one({
            "name": slo_name,
            "description": row.get("slo_description", slo_name),
            "substrandId": substrand_id
        })
        slo_id = str(slo_result.inserted_id)
        stats["slos_created"] += 1
        
        # Create SLO mapping
        comp_ids = []
        for comp_name in row.get("competencies", []):
            comp_lower = comp_name.lower().strip()
            for key, val in competencies.items():
                if comp_lower in key or key in comp_lower:
                    comp_ids.append(val)
                    break
        
        value_ids = []
        for val_name in row.get("values", []):
            val_lower = val_name.lower().strip()
            for key, val in values.items():
                if val_lower in key or key in val_lower:
                    value_ids.append(val)
                    break
        
        pci_ids = []
        for pci_name in row.get("pcis", []):
            pci_lower = pci_name.lower().strip()
            for key, val in pcis.items():
                if pci_lower in key or key in pci_lower:
                    pci_ids.append(val)
                    break
        
        # Use defaults if no mappings found
        if not comp_ids and competencies:
            comp_ids = list(competencies.values())[:2]
        if not value_ids and values:
            value_ids = list(values.values())[:2]
        if not pci_ids and pcis:
            pci_ids = list(pcis.values())[:2]
        
        await db.slo_mappings.insert_one({
            "sloId": slo_id,
            "competencyIds": comp_ids[:3],
            "valueIds": value_ids[:3],
            "pciIds": pci_ids[:3],
            "assessmentIds": []
        })
        stats["mappings_created"] += 1
    
    # Record import history
    await db.import_history.insert_one({
        "filename": request.filename,
        "import_type": "csv",
        "grade_name": grade.get("name", ""),
        "subject_name": subject.get("name", ""),
        "stats": stats,
        "imported_by": user.get("email", ""),
        "created_at": datetime.now(timezone.utc)
    })
    
    return {
        "success": True,
        "message": f"Import completed successfully",
        "stats": stats
    }


# ==================== RELATIONSHIP REPAIR ====================

@api_router.post("/admin/repair-relationships")
async def repair_relationships(user: dict = Depends(verify_admin)):
    """Scan and repair broken parent-child relationships in curriculum data.
    
    Fixes:
    - Strands with missing/invalid subjectId
    - Substrands with missing/invalid strandId  
    - SLOs with missing/invalid substrandId
    Reports orphaned items that cannot be auto-repaired.
    """
    stats = {
        "strands_checked": 0, "strands_orphaned": 0,
        "substrands_checked": 0, "substrands_orphaned": 0,
        "slos_checked": 0, "slos_orphaned": 0,
        "relationships_repaired": 0
    }
    orphans = []

    # Build lookup caches
    subject_ids = set()
    async for s in db.subjects.find({}, {"_id": 1}):
        subject_ids.add(str(s["_id"]))

    strand_id_to_subject = {}
    async for st in db.strands.find({}, {"_id": 1, "subjectId": 1}):
        strand_id_to_subject[str(st["_id"])] = st.get("subjectId")

    substrand_id_to_strand = {}
    async for ss in db.substrands.find({}, {"_id": 1, "strandId": 1}):
        substrand_id_to_strand[str(ss["_id"])] = ss.get("strandId")

    # Check strands
    async for strand in db.strands.find():
        stats["strands_checked"] += 1
        sid = strand.get("subjectId")
        if not sid or sid not in subject_ids:
            stats["strands_orphaned"] += 1
            orphans.append({
                "type": "strand", "id": str(strand["_id"]),
                "name": strand.get("name", "?"),
                "issue": f"subjectId '{sid}' not found in subjects"
            })

    # Check substrands
    async for ss in db.substrands.find():
        stats["substrands_checked"] += 1
        sid = ss.get("strandId")
        if not sid or sid not in strand_id_to_subject:
            stats["substrands_orphaned"] += 1
            orphans.append({
                "type": "substrand", "id": str(ss["_id"]),
                "name": ss.get("name", "?"),
                "issue": f"strandId '{sid}' not found in strands"
            })

    # Check SLOs
    async for slo in db.slos.find():
        stats["slos_checked"] += 1
        sid = slo.get("substrandId")
        if not sid or sid not in substrand_id_to_strand:
            stats["slos_orphaned"] += 1
            orphans.append({
                "type": "slo", "id": str(slo["_id"]),
                "name": slo.get("name", "?"),
                "issue": f"substrandId '{sid}' not found in substrands"
            })

    return {
        "success": True,
        "stats": stats,
        "orphans": orphans[:100],
        "message": f"Checked {stats['strands_checked']} strands, {stats['substrands_checked']} substrands, {stats['slos_checked']} SLOs. Found {len(orphans)} orphaned items."
    }


# ==================== IMPORT HISTORY ENDPOINTS ====================

@api_router.get("/admin/import/history")
async def get_import_history(user: dict = Depends(verify_admin), limit: int = 20):
    """Get history of data imports"""
    history = []
    cursor = db.import_history.find().sort("created_at", -1).limit(limit)
    async for record in cursor:
        history.append({
            "id": str(record["_id"]),
            "filename": record.get("filename", "Unknown"),
            "import_type": record.get("import_type", "csv"),
            "grade_name": record.get("grade_name", ""),
            "subject_name": record.get("subject_name", ""),
            "stats": record.get("stats", {}),
            "imported_by": record.get("imported_by", ""),
            "created_at": record.get("created_at", "").isoformat() if record.get("created_at") else ""
        })
    return {"success": True, "history": history}

# ==================== BULK EDITING ENDPOINTS ====================

class BulkUpdateRequest(BaseModel):
    item_type: str  # "strand", "substrand", "slo"
    item_ids: List[str]
    updates: Dict[str, Any]  # Fields to update

class ReorderRequest(BaseModel):
    item_type: str  # "strand", "substrand", "slo"
    parent_id: str  # subjectId for strands, strandId for substrands, substrandId for slos
    item_ids: List[str]  # Ordered list of item IDs

class BulkDeleteRequest(BaseModel):
    item_type: str  # "strand", "substrand", "slo"
    item_ids: List[str]

class BulkMappingRequest(BaseModel):
    slo_ids: List[str]
    competency_ids: List[str] = []
    value_ids: List[str] = []
    pci_ids: List[str] = []

@api_router.post("/admin/bulk-update")
async def bulk_update_items(request: BulkUpdateRequest, user: dict = Depends(verify_admin)):
    """Bulk update strands, substrands, or SLOs"""
    collection_map = {
        "strand": db.strands,
        "substrand": db.substrands,
        "slo": db.slos
    }
    
    if request.item_type not in collection_map:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    collection = collection_map[request.item_type]
    updated_count = 0
    
    # Filter out protected fields
    safe_updates = {k: v for k, v in request.updates.items() if k not in ["_id", "id"]}
    
    for item_id in request.item_ids:
        try:
            result = await collection.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": safe_updates}
            )
            if result.modified_count > 0:
                updated_count += 1
        except Exception as e:
            logger.error(f"Error updating {request.item_type} {item_id}: {str(e)}")
    
    return {
        "success": True,
        "message": f"Updated {updated_count} of {len(request.item_ids)} {request.item_type}s",
        "updated_count": updated_count
    }

@api_router.post("/admin/reorder")
async def reorder_items(request: ReorderRequest, user: dict = Depends(verify_admin)):
    """Reorder strands, substrands, or SLOs"""
    collection_map = {
        "strand": db.strands,
        "substrand": db.substrands,
        "slo": db.slos
    }
    parent_field_map = {
        "strand": "subjectId",
        "substrand": "strandId",
        "slo": "substrandId"
    }
    
    if request.item_type not in collection_map:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    collection = collection_map[request.item_type]
    parent_field = parent_field_map[request.item_type]
    
    # Update order for each item
    for idx, item_id in enumerate(request.item_ids):
        try:
            await collection.update_one(
                {"_id": ObjectId(item_id), parent_field: request.parent_id},
                {"$set": {"order": idx}}
            )
        except Exception as e:
            logger.error(f"Error reordering {request.item_type} {item_id}: {str(e)}")
    
    return {
        "success": True,
        "message": f"Reordered {len(request.item_ids)} {request.item_type}s"
    }

@api_router.post("/admin/move-item-order")
async def move_item_order(
    item_type: str,
    item_id: str,
    direction: str,  # "up" or "down"
    user: dict = Depends(verify_admin)
):
    """Move a single item up or down in the order"""
    collection_map = {
        "strand": db.strands,
        "substrand": db.substrands,
        "slo": db.slos
    }
    parent_field_map = {
        "strand": "subjectId",
        "substrand": "strandId",
        "slo": "substrandId"
    }
    
    if item_type not in collection_map:
        raise HTTPException(status_code=400, detail="Invalid item type")
    if direction not in ["up", "down"]:
        raise HTTPException(status_code=400, detail="Direction must be 'up' or 'down'")
    
    collection = collection_map[item_type]
    parent_field = parent_field_map[item_type]
    
    # Get the current item
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail=f"{item_type} not found")
    
    current_order = item.get("order", 0)
    parent_id = item.get(parent_field)
    
    # Find the sibling to swap with
    if direction == "up":
        sibling = await collection.find_one({
            parent_field: parent_id,
            "order": {"$lt": current_order}
        }, sort=[("order", -1)])
    else:
        sibling = await collection.find_one({
            parent_field: parent_id,
            "order": {"$gt": current_order}
        }, sort=[("order", 1)])
    
    if not sibling:
        return {
            "success": False,
            "message": f"Cannot move {direction} - already at the {'top' if direction == 'up' else 'bottom'}"
        }
    
    # Swap orders
    sibling_order = sibling.get("order", 0)
    await collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {"order": sibling_order}}
    )
    await collection.update_one(
        {"_id": sibling["_id"]},
        {"$set": {"order": current_order}}
    )
    
    return {
        "success": True,
        "message": f"Moved {item_type} {direction}"
    }

@api_router.post("/admin/bulk-delete")
async def bulk_delete_items(request: BulkDeleteRequest, user: dict = Depends(verify_admin)):
    """Bulk delete strands, substrands, or SLOs with cascade"""
    collection_map = {
        "strand": db.strands,
        "substrand": db.substrands,
        "slo": db.slos
    }
    
    if request.item_type not in collection_map:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    deleted_count = 0
    cascade_deleted = {"substrands": 0, "slos": 0, "activities": 0, "mappings": 0}
    
    for item_id in request.item_ids:
        try:
            if request.item_type == "strand":
                # Cascade delete substrands, slos, activities, mappings
                substrands = await db.substrands.find({"strandId": item_id}).to_list(None)
                for ss in substrands:
                    ss_id = str(ss["_id"])
                    # Delete SLOs and their mappings
                    slos = await db.slos.find({"substrandId": ss_id}).to_list(None)
                    for slo in slos:
                        await db.slo_mappings.delete_many({"sloId": str(slo["_id"])})
                        cascade_deleted["mappings"] += 1
                    slo_result = await db.slos.delete_many({"substrandId": ss_id})
                    cascade_deleted["slos"] += slo_result.deleted_count
                    # Delete activities
                    act_result = await db.learning_activities.delete_many({"substrandId": ss_id})
                    cascade_deleted["activities"] += act_result.deleted_count
                ss_result = await db.substrands.delete_many({"strandId": item_id})
                cascade_deleted["substrands"] += ss_result.deleted_count
                # Delete strand
                await db.strands.delete_one({"_id": ObjectId(item_id)})
                deleted_count += 1
                
            elif request.item_type == "substrand":
                # Cascade delete slos, activities, mappings
                slos = await db.slos.find({"substrandId": item_id}).to_list(None)
                for slo in slos:
                    await db.slo_mappings.delete_many({"sloId": str(slo["_id"])})
                    cascade_deleted["mappings"] += 1
                slo_result = await db.slos.delete_many({"substrandId": item_id})
                cascade_deleted["slos"] += slo_result.deleted_count
                await db.learning_activities.delete_many({"substrandId": item_id})
                cascade_deleted["activities"] += 1
                await db.substrands.delete_one({"_id": ObjectId(item_id)})
                deleted_count += 1
                
            elif request.item_type == "slo":
                # Delete SLO and its mapping
                await db.slo_mappings.delete_many({"sloId": item_id})
                cascade_deleted["mappings"] += 1
                await db.slos.delete_one({"_id": ObjectId(item_id)})
                deleted_count += 1
                
        except Exception as e:
            logger.error(f"Error deleting {request.item_type} {item_id}: {str(e)}")
    
    return {
        "success": True,
        "message": f"Deleted {deleted_count} {request.item_type}s",
        "deleted_count": deleted_count,
        "cascade_deleted": cascade_deleted
    }

@api_router.post("/admin/bulk-assign-mappings")
async def bulk_assign_mappings(request: BulkMappingRequest, user: dict = Depends(verify_admin)):
    """Bulk assign competencies, values, and PCIs to multiple SLOs"""
    updated_count = 0
    
    for slo_id in request.slo_ids:
        try:
            # Check if mapping exists
            existing = await db.slo_mappings.find_one({"sloId": slo_id})
            
            update_data = {}
            if request.competency_ids:
                update_data["competencyIds"] = request.competency_ids
            if request.value_ids:
                update_data["valueIds"] = request.value_ids
            if request.pci_ids:
                update_data["pciIds"] = request.pci_ids
            
            if existing:
                await db.slo_mappings.update_one(
                    {"sloId": slo_id},
                    {"$set": update_data}
                )
            else:
                await db.slo_mappings.insert_one({
                    "sloId": slo_id,
                    "competencyIds": request.competency_ids,
                    "valueIds": request.value_ids,
                    "pciIds": request.pci_ids,
                    "assessmentIds": []
                })
            updated_count += 1
        except Exception as e:
            logger.error(f"Error updating mapping for SLO {slo_id}: {str(e)}")
    
    return {
        "success": True,
        "message": f"Updated mappings for {updated_count} SLOs",
        "updated_count": updated_count
    }

# ==================== ADMIN UTILITY ENDPOINTS ====================

@api_router.post("/admin/clear-idempotency-cache")
async def clear_idempotency_cache(user: dict = Depends(verify_admin)):
    """Clear the idempotency cache to allow retrying stuck payments"""
    IdempotencyManager.clear_all()
    return {"success": True, "message": "Idempotency cache cleared"}

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

# ===========================================
# CURRICULUM PDF UPLOAD - NEW ISOLATED FEATURE
# ===========================================
import pdfplumber
import hashlib
import shutil

# Ensure directories exist
PDF_DIR = ROOT_DIR / "pdfs"
PROCESSED_DIR = ROOT_DIR / "pdfs_processed"
PDF_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# File size limit: 10MB
MAX_PDF_SIZE = 10 * 1024 * 1024

def extract_metadata_from_path(filename: str):
    """Extract grade and subject from filename"""
    name = filename.lower().replace(".pdf", "")
    # Try to extract grade number
    import re
    grade_match = re.search(r'grade\s*(\d+)', name)
    grade_num = grade_match.group(1) if grade_match else "10"
    # Subject is the filename cleaned up
    subject = re.sub(r'grade\s*\d+', '', name).strip().replace('_', ' ').replace('-', ' ')
    subject = subject.title() if subject else "Unknown Subject"
    return grade_num, subject

async def upsert_grade_async(name: str, order: int):
    """Upsert grade and return its ID"""
    result = await db.grades.find_one_and_update(
        {"name": name},
        {"$set": {"order": order}},
        upsert=True,
        return_document=True
    )
    return str(result["_id"])

async def upsert_subject_async(name: str, grade_id: str):
    """Upsert subject and return its ID"""
    result = await db.subjects.find_one_and_update(
        {"name": name},
        {"$set": {"gradeIds": [grade_id]}},
        upsert=True,
        return_document=True
    )
    return str(result["_id"])

async def upsert_strand_async(name: str, subject_id: str):
    """Upsert strand and return its ID"""
    result = await db.strands.find_one_and_update(
        {"name": name, "subjectId": subject_id},
        {"$set": {}},
        upsert=True,
        return_document=True
    )
    return str(result["_id"])

async def insert_substrand_async(name: str, strand_id: str):
    """Insert substrand and return its ID"""
    doc = {
        "_id": ObjectId(),
        "name": name,
        "strandId": strand_id
    }
    await db.substrands.insert_one(doc)
    return str(doc["_id"])

async def insert_slo_async(slo: dict, substrand_id: str):
    """Insert SLO and return its ID"""
    doc = {
        "_id": ObjectId(),
        "name": slo.get("name", ""),
        "description": slo.get("description", ""),
        "substrandId": substrand_id
    }
    await db.slos.insert_one(doc)
    return str(doc["_id"])

async def insert_slo_mapping_async(slo_id: str):
    """Insert SLO mapping"""
    await db.slo_mappings.insert_one({
        "_id": ObjectId(),
        "sloId": slo_id,
        "competencyIds": [],
        "valueIds": [],
        "pciIds": [],
        "assessmentIds": []
    })

async def insert_activities_async(substrand_id: str, activities: dict):
    """Insert learning activities for substrand"""
    await db.learning_activities.insert_one({
        "_id": ObjectId(),
        "substrandId": substrand_id,
        "introduction_activities": activities.get("introduction", []),
        "development_activities": activities.get("development", []),
        "conclusion_activities": activities.get("conclusion", []),
        "extended_activities": activities.get("extended", []),
        "learning_resources": [],
        "assessment_methods": []
    })

def extract_with_ai_simple(text: str) -> Optional[dict]:
    """
    Simple AI extraction using OpenAI for curriculum data.
    This reuses the same logic from the pipeline's ai_extractor.
    """
    try:
        from openai import OpenAI
        import json
        
        client = OpenAI()
        
        prompt = f"""
You are extracting structured curriculum data from a Kenyan CBC curriculum document.

Return ONLY valid JSON. Do not include any explanation.

STRICT RULES:
- Do NOT summarize
- Preserve exact wording
- Maintain hierarchy
- Capture ALL SLOs fully
- Separate activities correctly

JSON FORMAT:
{{
  "strand": "",
  "substrand": "",
  "slos": [
    {{
      "name": "",
      "description": ""
    }}
  ],
  "activities": {{
    "introduction": [],
    "development": [],
    "conclusion": [],
    "extended": []
  }},
  "competencies": [],
  "values": [],
  "pcis": []
}}

TEXT:
{text[:4000]}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        # Try to extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        return json.loads(content.strip())
    except Exception as e:
        logger.error(f"AI extraction error: {str(e)}")
        return None

async def process_single_pdf(file_path: Path) -> dict:
    """
    Process a single PDF file using the upgraded AI pipeline:
    1. Extract ALL text from PDF (full context, not page-by-page)
    2. Send to Gemini 2.5 Flash for structured extraction
    3. Save extracted JSON
    4. Generate seed script
    5. Run seed script to load into database
    """
    import sys
    sys.path.insert(0, str(ROOT_DIR / "scripts"))
    from ai_extractor import extract_with_gemini_chunked
    from seed_script_generator import generate_seed_script

    filename = file_path.name
    name_no_ext = file_path.stem
    logger.info(f"Processing PDF: {filename}")

    # Step 1: Extract ALL text from PDF
    all_text = []
    with pdfplumber.open(str(file_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text.append(text)

    full_text = "\n\n".join(all_text)
    if not full_text.strip():
        raise ValueError(f"No text found in {filename}")

    logger.info(f"Extracted {len(full_text)} characters from {filename}")

    # Detect grade/subject from filename
    grade_num, subject_name = extract_metadata_from_path(filename)
    grade_hint = f"Grade {grade_num}"

    # Step 2: AI extraction with Gemini (full context)
    logger.info(f"Sending to Gemini 2.5 Flash for extraction...")
    extracted = await extract_with_gemini_chunked(full_text, subject_name, grade_hint)

    if not extracted or not extracted.get("strands"):
        raise ValueError(f"AI extraction returned no data for {filename}")

    # Log detected grade (may be null if AI couldn't determine)
    detected_grade = extracted.get("grade")
    grade_source = extracted.get("_grade_source", "ai")
    logger.info(f"Grade detected: {detected_grade} (source: {grade_source})")
    if not detected_grade:
        logger.warning(f"Grade could not be detected from PDF, using filename hint: {grade_hint}")
        extracted["grade"] = grade_hint
        extracted["_grade_hint"] = grade_hint

    if not extracted or not extracted.get("strands"):
        raise ValueError(f"AI extraction returned no data for {filename}")

    strand_count = len(extracted.get("strands", []))
    ss_count = sum(len(s.get("substrands", [])) for s in extracted.get("strands", []))
    slo_count = sum(
        sum(len(ss.get("slos", [])) for ss in s.get("substrands", []))
        for s in extracted.get("strands", [])
    )
    logger.info(f"Extracted: {strand_count} strands, {ss_count} substrands, {slo_count} SLOs")

    # Step 3: Save JSON
    safe_name = name_no_ext.lower().replace(" ", "_").replace("-", "_")
    json_dir = ROOT_DIR / "curriculum_data"
    json_dir.mkdir(exist_ok=True)
    json_path = json_dir / f"extracted_{safe_name}.json"
    with open(json_path, "w") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)
    logger.info(f"JSON saved to {json_path}")

    # Step 4: Generate seed script
    script_name = f"seed_{safe_name}.py"
    script_path = str(ROOT_DIR / script_name)
    generate_seed_script(extracted, script_path)
    logger.info(f"Seed script saved to {script_path}")

    # Step 5: Run the seed script to load data into DB
    import subprocess
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        logger.error(f"Seed script error: {result.stderr}")
        raise ValueError(f"Seed script failed: {result.stderr[:500]}")

    logger.info(f"Seed script ran successfully")
    logger.info(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)

    return {
        "filename": filename,
        "grade": extracted.get("grade", grade_hint),
        "subject": extracted.get("subject_name", subject_name),
        "strands": strand_count,
        "substrands": ss_count,
        "slos": slo_count,
        "json_path": str(json_path),
        "seed_script": script_name,
    }

@api_router.post("/admin/upload-curriculum")
async def upload_curriculum_pdf(
    file: UploadFile = File(...),
    admin: str = Depends(verify_admin)
):
    """
    Upload and process a curriculum PDF file.
    
    - Accepts PDF files only (max 10MB)
    - Saves to backend/pdfs/
    - Processes using AI extraction pipeline
    - Moves to backend/pdfs_processed/ after completion
    - Returns success/failure status
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_PDF_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    # Generate safe filename
    safe_filename = file.filename.replace(" ", "_").replace("/", "_")
    file_path = PDF_DIR / safe_filename
    
    try:
        # Save file temporarily
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Saved PDF: {safe_filename}")
        
        # Process the PDF
        result = await process_single_pdf(file_path)
        
        # Move to processed directory
        processed_path = PROCESSED_DIR / safe_filename
        shutil.move(str(file_path), str(processed_path))
        
        logger.info(f"Moved to processed: {safe_filename}")
        
        return {
            "status": "success",
            "message": "Curriculum processed successfully",
            "details": result
        }
        
    except Exception as e:
        # Clean up on error
        if file_path.exists():
            file_path.unlink()
        
        logger.error(f"Error processing curriculum PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process curriculum: {str(e)}"
        )

# Health check endpoint
# Include router
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@app.on_event("startup")
async def startup_event():
    """
    Initialize database indexes on startup.
    Safe to call multiple times (createIndex is idempotent).
    """
    try:
        # Create required indexes for production
        # wallet_ledger - UNIQUE reference to prevent duplicate credits
        await db.wallet_ledger.create_index("reference", unique=True)
        await db.wallet_ledger.create_index("userId")
        await db.wallet_ledger.create_index("createdAt")
        
        # payments - Index on provider reference
        await db.payments.create_index("providerRef")
        await db.payments.create_index("userId")
        await db.payments.create_index("status")
        
        # wallets - Index on userId
        await db.wallets.create_index("userId", unique=True)
        
        # users - Index on role for admin queries
        await db.users.create_index("role")
        
        # wallet_transactions - Index on checkoutRequestID and tx_ref
        await db.wallet_transactions.create_index("checkoutRequestID")
        await db.wallet_transactions.create_index("tx_ref", unique=True)
        
        # Add order indexes for curriculum items
        await db.strands.create_index([("subjectId", 1), ("order", 1)])
        await db.substrands.create_index([("strandId", 1), ("order", 1)])
        await db.slos.create_index([("substrandId", 1), ("order", 1)])
        
        # Lesson plans - TTL index for auto-deletion of expired plans
        await db.lesson_plans.create_index("expiresAt", expireAfterSeconds=0)
        await db.lesson_plans.create_index("teacherId")

        # Substrand lessons index (compound unique)
        await db.substrand_lessons.create_index(
            [("substrand_id", 1), ("lesson_number", 1)], unique=True
        )

        # Lesson SLO Slots index (compound unique — Phase 1)
        await db.lesson_slo_slots.create_index(
            [("substrandId", 1), ("slot_index", 1)], unique=True
        )
        await db.lesson_slo_slots.create_index("substrandId")

        # Lesson SLOs index (compound unique)
        await db.lesson_slos.create_index(
            [("substrandId", 1), ("lessonNumber", 1)], unique=True
        )
        await db.lesson_slos.create_index("substrandId")

        # Scheme drafts index
        await db.scheme_drafts.create_index("teacherId")
        await db.scheme_drafts.create_index([("teacherId", 1), ("status", 1)])
        
        logger.info("Database indexes created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")

async def migrate_order_fields():
    """Add order field to strands, substrands, and SLOs that don't have it"""
    try:
        # Migrate strands
        subjects = await db.subjects.find().to_list(None)
        for subject in subjects:
            subject_id = str(subject["_id"])
            strands = await db.strands.find({"subjectId": subject_id}).to_list(None)
            for idx, strand in enumerate(strands):
                if "order" not in strand:
                    await db.strands.update_one(
                        {"_id": strand["_id"]},
                        {"$set": {"order": idx}}
                    )
        
        # Migrate substrands
        strands = await db.strands.find().to_list(None)
        for strand in strands:
            strand_id = str(strand["_id"])
            substrands = await db.substrands.find({"strandId": strand_id}).to_list(None)
            for idx, substrand in enumerate(substrands):
                if "order" not in substrand:
                    await db.substrands.update_one(
                        {"_id": substrand["_id"]},
                        {"$set": {"order": idx}}
                    )
        
        # Migrate SLOs
        substrands = await db.substrands.find().to_list(None)
        for substrand in substrands:
            substrand_id = str(substrand["_id"])
            slos = await db.slos.find({"substrandId": substrand_id}).to_list(None)
            for idx, slo in enumerate(slos):
                if "order" not in slo:
                    await db.slos.update_one(
                        {"_id": slo["_id"]},
                        {"$set": {"order": idx}}
                    )
        
        logger.info("Order field migration completed")
    except Exception as e:
        logger.error(f"Error in order field migration: {str(e)}")
