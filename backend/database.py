"""
MongoDB Production Connection Module
Serverless-safe pattern for Vercel/Railway deployment
Developed by LEGIT LAB
"""

import os
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# Global cached client instance (serverless-safe pattern)
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


class MongoDBConnectionError(Exception):
    """Raised when MongoDB connection fails or environment variables are missing"""
    pass


def get_mongodb_uri() -> str:
    """
    Get MongoDB URI from environment variables.
    Raises MongoDBConnectionError if not configured.
    """
    uri = os.getenv('MONGODB_URI')
    
    if not uri:
        # Fallback for legacy support
        uri = os.getenv('MONGO_URL')
    
    if not uri:
        raise MongoDBConnectionError(
            "MONGODB_URI environment variable is not set. "
            "Please configure your MongoDB connection string."
        )
    
    return uri


def get_database_name() -> str:
    """Get database name from environment variables with default fallback."""
    return os.getenv('MONGODB_DB') or os.getenv('DB_NAME', 'cbeplanner')


def get_client() -> AsyncIOMotorClient:
    """
    Get cached MongoDB client instance.
    Creates new client if not exists (serverless-safe pattern).
    """
    global _client
    
    if _client is None:
        uri = get_mongodb_uri()
        logger.info("Creating new MongoDB client connection...")
        
        _client = AsyncIOMotorClient(
            uri,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True,
            w='majority'
        )
        
        logger.info("MongoDB client created successfully")
    
    return _client


def get_database() -> AsyncIOMotorDatabase:
    """
    Get cached database instance.
    Returns the configured database from the cached client.
    """
    global _db
    
    if _db is None:
        client = get_client()
        db_name = get_database_name()
        _db = client[db_name]
        logger.info(f"Connected to database: {db_name}")
    
    return _db


async def ping_database() -> bool:
    """
    Test database connection.
    Returns True if connection is successful, False otherwise.
    """
    try:
        client = get_client()
        await client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"Database ping failed: {str(e)}")
        return False


async def close_connection():
    """Close MongoDB connection (for cleanup)."""
    global _client, _db
    
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")


async def ensure_indexes():
    """
    Create required indexes for production.
    Safe to call multiple times (createIndex is idempotent).
    """
    db = get_database()
    
    try:
        # Wallet ledger - UNIQUE reference to prevent duplicate credits
        await db.wallet_ledger.create_index("reference", unique=True)
        await db.wallet_ledger.create_index("userId")
        await db.wallet_ledger.create_index("createdAt")
        
        # Payments - Index on provider reference
        await db.payments.create_index("providerRef")
        await db.payments.create_index("userId")
        await db.payments.create_index("status")
        
        # Wallets - Index on userId
        await db.wallets.create_index("userId", unique=True)
        
        # Users - Index on role for admin queries
        await db.users.create_index("role")
        await db.users.create_index("email", unique=True)
        await db.users.create_index("firebaseUid", unique=True, sparse=True)
        
        # Wallet transactions (legacy) - Index on checkoutRequestID
        await db.wallet_transactions.create_index("checkoutRequestID")
        await db.wallet_transactions.create_index("tx_ref", unique=True)
        
        logger.info("Database indexes created/verified successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        return False


# Convenience function for direct database access
db = property(lambda self: get_database())
