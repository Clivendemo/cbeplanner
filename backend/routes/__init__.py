"""Route modules.

Each module registers its endpoints on the shared api_router (from app.deps).
server.py imports these modules (side-effect) before including api_router on the app.
"""
