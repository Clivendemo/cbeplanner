"""
Production-grade utilities for error handling, logging, validation, and security.
"""

import logging
import hashlib
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Set
from functools import wraps
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import re

logger = logging.getLogger(__name__)

# ===========================================
# SAFARICOM M-PESA IP WHITELIST
# ===========================================
SAFARICOM_IPS: Set[str] = {
    "196.201.214.200",
    "196.201.214.206",
    "196.201.213.114",
    "196.201.214.207",
    "196.201.214.208",
    "196.201.213.44",
    "196.201.212.127",
    "196.201.212.138",
    "196.201.212.129",
    "196.201.212.136",
    "196.201.212.74",
    "196.201.212.69",
}

# ===========================================
# M-PESA RESULT CODE MAPPINGS
# ===========================================
MPESA_RESULT_CODES: Dict[int, Dict[str, str]] = {
    0: {"status": "success", "message": "Payment successful"},
    1: {"status": "failed", "message": "Insufficient funds in your M-Pesa account"},
    1032: {"status": "cancelled", "message": "Payment cancelled by user"},
    1037: {"status": "timeout", "message": "Payment request timed out. Please try again"},
    2001: {"status": "failed", "message": "Wrong M-Pesa PIN entered"},
    2029: {"status": "failed", "message": "Payment could not be processed. Please contact support"},
    17: {"status": "failed", "message": "Transaction limit exceeded"},
    26: {"status": "failed", "message": "System busy. Please try again later"},
}

def get_mpesa_result_message(result_code: int) -> Dict[str, str]:
    """Get user-friendly message for M-Pesa result code"""
    return MPESA_RESULT_CODES.get(
        result_code, 
        {"status": "failed", "message": f"Payment failed (Code: {result_code}). Please try again"}
    )

def is_safaricom_ip(ip: str) -> bool:
    """Check if IP address is from Safaricom"""
    return ip in SAFARICOM_IPS

def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies"""
    # Check X-Forwarded-For header (common with load balancers/proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get the first IP in the chain (original client)
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return ""

# ===========================================
# USER-FRIENDLY ERROR MESSAGES
# ===========================================
ERROR_MESSAGES = {
    # Authentication errors
    "auth_required": "Please log in to continue.",
    "auth_expired": "Your session has expired. Please log in again.",
    "auth_invalid": "Invalid credentials. Please check your email and password.",
    "auth_forbidden": "You don't have permission to access this resource.",
    
    # Payment errors
    "payment_failed": "Payment could not be processed. Please try again.",
    "payment_pending": "Your payment is still being processed. Please wait.",
    "payment_duplicate": "This payment has already been processed.",
    "insufficient_balance": "Insufficient wallet balance. Please top up.",
    
    # Validation errors
    "invalid_input": "Please check your input and try again.",
    "missing_fields": "Please fill in all required fields.",
    "invalid_phone": "Please enter a valid phone number.",
    "invalid_amount": "Please enter a valid amount.",
    
    # General errors
    "server_error": "Something went wrong. Please try again later.",
    "network_error": "Connection issue. Please check your internet and try again.",
    "not_found": "The requested resource was not found.",
    "rate_limited": "Too many requests. Please wait a moment and try again.",
    "duplicate_action": "This action has already been performed.",
}

def get_user_error(error_key: str, fallback: str = None) -> str:
    """Get user-friendly error message"""
    return ERROR_MESSAGES.get(error_key, fallback or ERROR_MESSAGES["server_error"])


# ===========================================
# STRUCTURED LOGGING
# ===========================================
class ProductionLogger:
    """Structured logger that sanitizes sensitive data"""
    
    SENSITIVE_FIELDS = {
        'password', 'token', 'idToken', 'accessToken', 'refreshToken',
        'apiKey', 'secret', 'authorization', 'mpesaPassword', 'pin'
    }
    
    @staticmethod
    def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive fields from log data"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if key.lower() in {f.lower() for f in ProductionLogger.SENSITIVE_FIELDS}:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = ProductionLogger.sanitize_data(value)
            else:
                sanitized[key] = value
        return sanitized
    
    @staticmethod
    def log_auth_attempt(email: str, success: bool, ip: str = None, reason: str = None):
        """Log authentication attempt"""
        logger.info(f"AUTH_ATTEMPT: email={email[:3]}***@***.com success={success} ip={ip or 'unknown'} reason={reason or 'N/A'}")
    
    @staticmethod
    def log_payment_attempt(user_id: str, amount: float, phone: str, status: str, reference: str = None):
        """Log payment attempt"""
        masked_phone = f"{phone[:3]}***{phone[-2:]}" if len(phone) > 5 else "***"
        logger.info(f"PAYMENT_ATTEMPT: user={user_id[:8]}... amount={amount} phone={masked_phone} status={status} ref={reference or 'N/A'}")
    
    @staticmethod
    def log_wallet_update(user_id: str, previous_balance: float, new_balance: float, reason: str, reference: str = None):
        """Log wallet balance update"""
        logger.info(f"WALLET_UPDATE: user={user_id[:8]}... prev={previous_balance} new={new_balance} reason={reason} ref={reference or 'N/A'}")
    
    @staticmethod
    def log_error(error_type: str, message: str, user_id: str = None, details: Dict = None):
        """Log error with context"""
        safe_details = ProductionLogger.sanitize_data(details or {})
        logger.error(f"ERROR: type={error_type} user={user_id[:8] + '...' if user_id else 'N/A'} message={message} details={safe_details}")
    
    @staticmethod
    def log_critical_action(action: str, user_id: str, details: Dict = None):
        """Log critical actions like admin operations"""
        safe_details = ProductionLogger.sanitize_data(details or {})
        logger.warning(f"CRITICAL_ACTION: action={action} user={user_id[:8]}... details={safe_details}")


# ===========================================
# IDEMPOTENCY & DUPLICATE PREVENTION
# ===========================================
class IdempotencyManager:
    """Manage idempotency keys to prevent duplicate operations"""
    
    # In-memory cache (for single instance), use Redis in production cluster
    _processed_keys: Dict[str, float] = {}
    _key_expiry_seconds = 60  # 60 seconds - reduced from 1 hour to allow retries
    
    @staticmethod
    def generate_key(*args) -> str:
        """Generate idempotency key from arguments"""
        key_string = ":".join(str(arg) for arg in args)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    @classmethod
    def check_and_mark(cls, key: str) -> bool:
        """
        Check if key has been processed. Returns True if duplicate.
        Also cleans up expired keys.
        """
        current_time = time.time()
        
        # Clean up expired keys
        expired_keys = [k for k, t in cls._processed_keys.items() 
                       if current_time - t > cls._key_expiry_seconds]
        for k in expired_keys:
            del cls._processed_keys[k]
        
        # Check if already processed
        if key in cls._processed_keys:
            return True  # Duplicate
        
        # Mark as processed
        cls._processed_keys[key] = current_time
        return False  # Not a duplicate
    
    @classmethod
    def is_duplicate(cls, key: str) -> bool:
        """Check if key is a duplicate without marking"""
        return key in cls._processed_keys
    
    @classmethod
    def clear_all(cls):
        """Clear all idempotency keys - useful for admin reset"""
        cls._processed_keys.clear()
    
    @classmethod
    def clear_for_user(cls, user_id: str):
        """Clear idempotency keys containing user_id"""
        keys_to_remove = [k for k in cls._processed_keys.keys() if user_id in k]
        for k in keys_to_remove:
            del cls._processed_keys[k]


# ===========================================
# INPUT VALIDATION
# ===========================================
class InputValidator:
    """Validate and sanitize user inputs"""
    
    PHONE_REGEX = re.compile(r'^(?:\+254|254|0)?([17]\d{8})$')
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return ""
        # Remove potential injection characters
        sanitized = value.strip()
        # Limit length
        sanitized = sanitized[:max_length]
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        return sanitized
    
    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, str]:
        """Validate and normalize Kenyan phone number"""
        if not phone:
            return False, "Phone number is required"
        
        # Remove spaces and dashes
        clean_phone = re.sub(r'[\s\-]', '', phone)
        
        match = InputValidator.PHONE_REGEX.match(clean_phone)
        if not match:
            return False, "Please enter a valid Kenyan phone number"
        
        # Normalize to 254 format
        normalized = f"254{match.group(1)}"
        return True, normalized
    
    @staticmethod
    def validate_amount(amount: Any, min_val: float = 1, max_val: float = 150000) -> tuple[bool, float, str]:
        """Validate payment amount"""
        try:
            amount_float = float(amount)
            if amount_float < min_val:
                return False, 0, f"Minimum amount is {min_val} KES"
            if amount_float > max_val:
                return False, 0, f"Maximum amount is {max_val} KES"
            return True, amount_float, ""
        except (TypeError, ValueError):
            return False, 0, "Please enter a valid amount"
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email format"""
        if not email:
            return False, "Email is required"
        
        email = email.strip().lower()
        if not InputValidator.EMAIL_REGEX.match(email):
            return False, "Please enter a valid email address"
        
        return True, email
    
    @staticmethod
    def validate_object_id(id_string: str) -> bool:
        """Validate MongoDB ObjectId format"""
        if not id_string:
            return False
        return bool(re.match(r'^[a-fA-F0-9]{24}$', id_string))


# ===========================================
# RATE LIMITING
# ===========================================
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    _requests: Dict[str, list] = {}
    
    @classmethod
    def check_rate_limit(cls, key: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """
        Check if rate limit exceeded. Returns True if allowed, False if rate limited.
        """
        current_time = time.time()
        
        if key not in cls._requests:
            cls._requests[key] = []
        
        # Clean old requests outside window
        cls._requests[key] = [t for t in cls._requests[key] 
                             if current_time - t < window_seconds]
        
        if len(cls._requests[key]) >= max_requests:
            return False  # Rate limited
        
        cls._requests[key].append(current_time)
        return True  # Allowed


# ===========================================
# TRANSACTION SAFETY
# ===========================================
class TransactionLock:
    """Simple transaction locking to prevent race conditions"""
    
    _locks: Dict[str, float] = {}
    _lock_timeout = 30  # seconds
    
    @classmethod
    def acquire(cls, key: str) -> bool:
        """Acquire lock. Returns True if acquired, False if already locked."""
        current_time = time.time()
        
        # Check if locked and not expired
        if key in cls._locks:
            if current_time - cls._locks[key] < cls._lock_timeout:
                return False  # Still locked
        
        cls._locks[key] = current_time
        return True
    
    @classmethod
    def release(cls, key: str):
        """Release lock"""
        if key in cls._locks:
            del cls._locks[key]
    
    @classmethod
    def is_locked(cls, key: str) -> bool:
        """Check if locked"""
        if key not in cls._locks:
            return False
        return time.time() - cls._locks[key] < cls._lock_timeout


# ===========================================
# HTTP SECURITY HEADERS
# ===========================================
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cache-Control": "no-store, no-cache, must-revalidate",
    "Pragma": "no-cache",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "Content-Security-Policy": "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:;",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
}


def add_security_headers(response):
    """Add security headers to response"""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


# ===========================================
# RATE LIMITING
# ===========================================
class RateLimitManager:
    """
    Simple in-memory rate limiter for API endpoints.
    For production clusters, use Redis-based rate limiting.
    """
    
    _requests: Dict[str, list] = {}  # ip -> list of timestamps
    
    # Rate limit configurations (requests per window)
    LIMITS = {
        "default": {"requests": 100, "window": 60},      # 100 requests per minute
        "auth": {"requests": 10, "window": 60},          # 10 auth attempts per minute
        "payment": {"requests": 5, "window": 60},        # 5 payment attempts per minute
        "admin": {"requests": 200, "window": 60},        # 200 admin requests per minute
    }
    
    @classmethod
    def is_rate_limited(cls, ip: str, endpoint_type: str = "default") -> bool:
        """Check if IP is rate limited"""
        current_time = time.time()
        config = cls.LIMITS.get(endpoint_type, cls.LIMITS["default"])
        window = config["window"]
        max_requests = config["requests"]
        
        # Initialize if not exists
        if ip not in cls._requests:
            cls._requests[ip] = []
        
        # Clean old requests outside window
        cls._requests[ip] = [
            ts for ts in cls._requests[ip] 
            if current_time - ts < window
        ]
        
        # Check if over limit
        if len(cls._requests[ip]) >= max_requests:
            return True
        
        # Record this request
        cls._requests[ip].append(current_time)
        return False
    
    @classmethod
    def get_retry_after(cls, ip: str, endpoint_type: str = "default") -> int:
        """Get seconds until rate limit resets"""
        if ip not in cls._requests or not cls._requests[ip]:
            return 0
        
        config = cls.LIMITS.get(endpoint_type, cls.LIMITS["default"])
        oldest_request = min(cls._requests[ip])
        return max(0, int(config["window"] - (time.time() - oldest_request)))
    
    @classmethod
    def cleanup(cls):
        """Remove old entries to prevent memory bloat"""
        current_time = time.time()
        max_window = max(c["window"] for c in cls.LIMITS.values())
        
        for ip in list(cls._requests.keys()):
            cls._requests[ip] = [
                ts for ts in cls._requests[ip]
                if current_time - ts < max_window
            ]
            if not cls._requests[ip]:
                del cls._requests[ip]


# ===========================================
# REQUEST LOGGING
# ===========================================
class RequestLogger:
    """Log API requests for monitoring and debugging"""
    
    # Paths to exclude from logging (health checks, static files)
    EXCLUDED_PATHS = {"/health", "/api/health", "/favicon.ico"}
    
    @staticmethod
    def should_log(path: str) -> bool:
        """Check if request should be logged"""
        return path not in RequestLogger.EXCLUDED_PATHS
    
    @staticmethod
    def log_request(
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        ip: str,
        user_id: str = None
    ):
        """Log request details"""
        user_info = f"user={user_id[:8]}..." if user_id else "user=anonymous"
        logger.info(
            f"REQUEST: {method} {path} status={status_code} "
            f"duration={duration_ms:.2f}ms ip={ip} {user_info}"
        )


# ===========================================
# PRODUCTION CORS ORIGINS
# ===========================================
PRODUCTION_CORS_ORIGINS = [
    "https://cbeplanner.vercel.app",
    "https://www.cbeplanner.vercel.app",
    "https://cbeplanner.onrender.com",
    # Add your custom domain here when you have one
]

DEVELOPMENT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8081",
    "http://localhost:19006",
    "http://localhost:19000",
    "https://teach-align.preview.emergentagent.com",
]

def get_cors_origins(environment: str) -> list:
    """Get CORS origins based on environment"""
    if environment == "production":
        return PRODUCTION_CORS_ORIGINS
    return DEVELOPMENT_CORS_ORIGINS + PRODUCTION_CORS_ORIGINS
