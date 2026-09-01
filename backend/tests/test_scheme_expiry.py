"""
Regression: schemes auto-expire 24h after creation.

Uses synchronous PyMongo + requests so we don't depend on pytest-asyncio
fixture plumbing. Inserts an expired + live scheme directly via Mongo,
then verifies the three affected endpoints behave correctly.
"""
import os
from datetime import datetime, timedelta

import pytest
import requests
from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "cbeplanner-oregon")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8001").rstrip("/")
TEST_EMAIL = os.environ.get("TEST_TEACHER_EMAIL", "testteacher2026@gmail.com")
TEST_PASSWORD = os.environ.get("TEST_TEACHER_PASSWORD", "TestPass123!")
FIREBASE_KEY = "AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8"


def _get_token():
    r = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_KEY}",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD, "returnSecureToken": True},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["idToken"]


@pytest.fixture
def seeded():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    user = db.users.find_one({"email": TEST_EMAIL})
    assert user, f"Test teacher {TEST_EMAIL} missing in {DB_NAME}"
    tid = user.get("id") or str(user["_id"])
    now = datetime.utcnow()

    expired = db.schemes.insert_one({
        "teacherId": tid, "schoolName": "PYTEST", "gradeName": "Grade 10",
        "subjectName": "PYTEST EXPIRED", "term": 1, "year": 2026, "lessons": [],
        "createdAt": now - timedelta(hours=25),
        "expiresAt": now - timedelta(hours=1),
        "isPaid": False,
    })
    live = db.schemes.insert_one({
        "teacherId": tid, "schoolName": "PYTEST", "gradeName": "Grade 10",
        "subjectName": "PYTEST LIVE", "term": 1, "year": 2026, "lessons": [],
        "createdAt": now,
        "expiresAt": now + timedelta(hours=23),
        "isPaid": False,
    })
    try:
        yield {"expired": str(expired.inserted_id), "live": str(live.inserted_id)}
    finally:
        db.schemes.delete_many({"_id": {"$in": [expired.inserted_id, live.inserted_id]}})
        client.close()


def test_list_filters_expired_schemes(seeded):
    token = _get_token()
    r = requests.get(
        f"{BASE_URL}/api/schemes",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15, allow_redirects=True,
    )
    assert r.status_code == 200
    titles = [s.get("subjectName") for s in r.json().get("schemes", [])]
    assert "PYTEST LIVE" in titles
    assert "PYTEST EXPIRED" not in titles


def test_detail_returns_410_for_expired(seeded):
    token = _get_token()
    r = requests.get(
        f"{BASE_URL}/api/schemes/{seeded['expired']}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15, allow_redirects=True,
    )
    assert r.status_code == 410, r.text
    assert "expired" in r.json().get("detail", "").lower()


def test_download_returns_410_for_expired(seeded):
    """No wallet charge must occur when the scheme has expired."""
    token = _get_token()
    r = requests.post(
        f"{BASE_URL}/api/schemes/{seeded['expired']}/download",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15, allow_redirects=True,
    )
    assert r.status_code == 410, r.text


def test_live_scheme_still_accessible(seeded):
    token = _get_token()
    r = requests.get(
        f"{BASE_URL}/api/schemes/{seeded['live']}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15, allow_redirects=True,
    )
    assert r.status_code == 200
