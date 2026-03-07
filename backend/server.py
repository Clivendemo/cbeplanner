from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
import httpx

# Import production utilities
from app.production_utils import (
    ProductionLogger, IdempotencyManager, InputValidator, 
    RateLimiter, TransactionLock, get_user_error, SECURITY_HEADERS
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
db_name = os.getenv('DB_NAME', 'cbeplanner')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Firebase project configuration from environment variables
# Falls back to defaults for backward compatibility
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'cbeplanner')
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', 'AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8')

# JWT Secret for additional security (optional)
JWT_SECRET = os.getenv('JWT_SECRET', 'default-secret-change-in-production')

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
        "https://lesson-plan-builder-1.preview.emergentagent.com"
    ]

# ===========================================
# FASTAPI APPLICATION SETUP
# ===========================================
app = FastAPI(
    title="CBE Lesson Planner API",
    description="Competency-Based Education Lesson Planning System for Kenyan Teachers",
    version="1.0.0",
    docs_url="/api/docs" if ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if ENVIRONMENT != "production" else None
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
app.add_middleware(GlobalErrorHandlerMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if ENVIRONMENT == "production" else ["*"],
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

# ==================== MODELS ====================

# Lesson plan pricing constants
LESSON_PLAN_COST_KES = 2
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

# The ONLY admin email allowed
ADMIN_EMAIL = "mail2clive@gmail.com"

async def verify_admin(authorization: Optional[str] = Header(None)):
    """
    Verify that the user is the designated admin.
    ONLY mail2clive@gmail.com can access admin endpoints.
    This is enforced by email, not by role field.
    """
    user = await verify_token(authorization)
    user_email = user.get("email", "").lower().strip()
    
    if user_email != ADMIN_EMAIL:
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

@api_router.get("/profile/is-admin")
async def check_is_admin(user: dict = Depends(verify_token)):
    """Check if current user is the designated admin"""
    user_email = user.get("email", "").lower().strip()
    is_admin = user_email == ADMIN_EMAIL
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
async def mpesa_callback(callback_data: PaymentCallbackData):
    """
    M-Pesa callback endpoint for payment confirmation
    
    - Receives payment result from M-Pesa
    - Stores raw callback payload for auditing
    - Verifies transaction exists and is pending
    - Updates transaction status
    - Creates wallet_ledger entry (source of truth)
    - Atomically updates wallet balance on success
    - Implements idempotency (ignores already processed transactions)
    """
    try:
        body = callback_data.Body
        stk_callback = body.get("stkCallback", {})
        
        merchant_request_id = stk_callback.get("MerchantRequestID")
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")
        
        logger.info(f"M-Pesa callback received: CheckoutRequestID={checkout_request_id}, ResultCode={result_code}")
        
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
            "rawCallback": body,  # Store full payload
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
            # Payment failed or cancelled
            await db.wallet_transactions.update_one(
                {"_id": transaction["_id"]},
                {
                    "$set": {
                        "status": "failed",
                        "resultCode": str(result_code),
                        "resultDesc": result_desc,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            logger.info(f"Transaction {transaction['tx_ref']} failed: {result_desc}")
        
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
    subjects = await db.subjects.find({"gradeIds": gradeId}).sort("name", 1).to_list(100)
    return {"success": True, "subjects": [serialize_doc(s) for s in subjects]}

@api_router.get("/strands")
async def get_strands(subjectId: str, user: dict = Depends(verify_token)):
    strands = await db.strands.find({"subjectId": subjectId}).sort("name", 1).to_list(100)
    return {"success": True, "strands": [serialize_doc(s) for s in strands]}

@api_router.get("/substrands")
async def get_substrands(strandId: str, user: dict = Depends(verify_token)):
    logger.info(f"[SUBSTRANDS] Fetching substrands for strandId: {strandId}")
    substrands = await db.substrands.find({"strandId": strandId}).sort("name", 1).to_list(100)
    logger.info(f"[SUBSTRANDS] Found {len(substrands)} substrands for strandId: {strandId}")
    return {"success": True, "substrands": [serialize_doc(s) for s in substrands]}

@api_router.get("/slos")
async def get_slos(substrandId: str, user: dict = Depends(verify_token)):
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
        
        # Fetch specific learning activities for this substrand
        learning_activities_doc = await db.learning_activities.find_one({"substrandId": request.substrandId})
        
        # Extract specific activities or use defaults
        intro_activities = []
        dev_activities = []
        conclusion_activities = []
        extended_activities_list = []
        specific_resources = []
        specific_assessments = []
        
        if learning_activities_doc:
            intro_activities = learning_activities_doc.get("introduction_activities", [])
            dev_activities = learning_activities_doc.get("development_activities", [])
            conclusion_activities = learning_activities_doc.get("conclusion_activities", [])
            extended_activities_list = learning_activities_doc.get("extended_activities", [])
            specific_resources = learning_activities_doc.get("learning_resources", [])
            specific_assessments = learning_activities_doc.get("assessment_methods", [])
        
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
        
        # Log successful generation
        ProductionLogger.log_critical_action("LESSON_PLAN_GENERATED", user_id, {
            "lesson_plan_id": lesson_plan["id"],
            "grade": lesson_plan["gradeName"],
            "subject": lesson_plan["subjectName"],
            "used_free": free_remaining > 0
        })
        
        return {"success": True, "lessonPlan": lesson_plan}
    
    finally:
        # Always release the lock
        TransactionLock.release(lock_key)

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
def generate_inquiry_questions(strand: str, substrand: str, slo: str) -> str:
    """Generate relevant key inquiry questions based on the topic"""
    questions = []
    
    # Generic patterns based on topic
    if "evolution" in substrand.lower() or "history" in substrand.lower():
        questions.append(f"How has {substrand} developed over time?")
        questions.append(f"What are the key milestones in the development of {substrand}?")
    elif "architecture" in substrand.lower() or "structure" in substrand.lower():
        questions.append(f"What are the main components of {substrand}?")
        questions.append(f"How do the different parts of {substrand} work together?")
    elif "network" in substrand.lower() or "communication" in substrand.lower():
        questions.append(f"How is data transmitted in {substrand}?")
        questions.append(f"What factors affect {substrand} performance?")
    elif "programming" in substrand.lower() or "code" in substrand.lower():
        questions.append(f"How do we implement {substrand} in programming?")
        questions.append(f"What are the best practices for {substrand}?")
    else:
        questions.append(f"What is the importance of {substrand}?")
        questions.append(f"How do we apply {substrand} in real-world situations?")
    
    return " ".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

def generate_learning_experiences(strand: str, substrand: str, slo: str) -> str:
    """Generate appropriate learning experiences"""
    slo_lower = slo.lower()
    
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

def generate_learning_resources(strand: str, substrand: str) -> str:
    """Generate appropriate learning resources"""
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

def generate_assessment_methods(slo: str) -> str:
    """Generate appropriate assessment methods based on SLO"""
    slo_lower = slo.lower()
    
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

@api_router.get("/schemes/{scheme_id}")
async def get_scheme(scheme_id: str, user: dict = Depends(verify_token)):
    scheme = await db.schemes.find_one({"_id": ObjectId(scheme_id), "teacherId": user["id"]})
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return {"success": True, "scheme": serialize_doc(scheme)}

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
        
        logger.info("Database indexes created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
