"""
Shared dependencies for the CBE Lesson Planner API.

Centralizes database client, authentication, Firebase config, helpers, constants,
and the shared API router so route modules can import what they need without
pulling in the monolithic server.py.
"""
import os
import logging
from datetime import datetime
from typing import Optional

import certifi
import httpx
from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from pathlib import Path

# ===========================================
# ENVIRONMENT CONFIGURATION
# ===========================================
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger("cbeplanner")

# ===========================================
# DATABASE (MongoDB)
# ===========================================
mongo_url = os.getenv('MONGODB_URI') or os.environ.get('MONGO_URL')
if not mongo_url:
    raise RuntimeError("MONGODB_URI or MONGO_URL environment variable is required")
db_name = os.getenv('DB_NAME', 'cbeplanner-oregon')

_connect_opts = {"serverSelectionTimeoutMS": 5000, "connectTimeoutMS": 5000}
if 'mongodb+srv' in mongo_url or 'mongodb.net' in mongo_url:
    mongo_client = AsyncIOMotorClient(mongo_url, tlsCAFile=certifi.where(), **_connect_opts)
else:
    mongo_client = AsyncIOMotorClient(mongo_url, **_connect_opts)
db = mongo_client[db_name]

# ===========================================
# FIREBASE CONFIG
# ===========================================
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'cbeplanner')
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
if not FIREBASE_API_KEY:
    if os.getenv('ENVIRONMENT', 'development') == 'production':
        raise RuntimeError("FIREBASE_API_KEY environment variable is required")
    FIREBASE_API_KEY = 'AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8'  # dev-only fallback

JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    if os.getenv('ENVIRONMENT', 'development') == 'production':
        raise RuntimeError("JWT_SECRET environment variable is required")
    JWT_SECRET = 'default-secret-change-in-production'

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

_admin_emails_env = os.getenv('ADMIN_EMAILS', 'mail2clive@gmail.com,testadmin2026@gmail.com')
ADMIN_EMAILS = {e.strip().lower() for e in _admin_emails_env.split(',') if e.strip()}

# ===========================================
# PRICING CONSTANTS
# ===========================================
LESSON_PLAN_COST_KES = 2
NOTES_DOWNLOAD_COST_KES = 1
SCHEME_DOWNLOAD_COST = 15  # KES
ASSESSMENT_DOWNLOAD_COST_KES = 10  # KES — past papers / assessments from R2
FREE_LESSONS_ON_SIGNUP = 5

# ===========================================
# SHARED API ROUTER
# ===========================================
# All route modules register their endpoints on this single router.
# server.py mounts it with `app.include_router(api_router)`.
api_router = APIRouter(prefix="/api")


# ===========================================
# SERIALIZATION & VALIDATION HELPERS
# ===========================================
def serialize_doc(doc):
    """Convert a MongoDB doc's ObjectId to a string `id` field and drop `_id`."""
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


def to_int(value, default: int = 0) -> int:
    """Safely convert any value to integer."""
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


# ===========================================
# AUTH DEPENDENCIES
# ===========================================
async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify a Firebase ID token and return the corresponding DB user record.
    Creates the user on first-seen. Raises 401 on any auth failure."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.split("Bearer ")[1]
    try:
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


async def verify_admin(authorization: Optional[str] = Header(None)):
    """Verify the caller is one of the ADMIN_EMAILS. 403 otherwise."""
    user = await verify_token(authorization)
    user_email = user.get("email", "").lower().strip()
    if user_email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=403,
            detail="Admin access denied. This action is restricted to authorized administrators only."
        )
    return user
