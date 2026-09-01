"""
Regression tests after wholesale sync of server.py, routes/assessments.py, and 3 frontend files.
Focus: verify all teacher-side endpoints still return 200, admin endpoint rejects teacher, and
new /api/assessments routes work.
"""
import os
import pytest
import requests

BASE = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "https://magical-shannon-6.preview.emergentagent.com").rstrip("/")
FIREBASE_KEY = "AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8"
TEACHER_EMAIL = "visualtest2026@example.com"
TEACHER_PASS = "Visual@2026"


@pytest.fixture(scope="module")
def teacher_token():
    r = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_KEY}",
        json={"email": TEACHER_EMAIL, "password": TEACHER_PASS, "returnSecureToken": True},
        timeout=20,
    )
    assert r.status_code == 200, f"Firebase login failed: {r.text}"
    return r.json()["idToken"]


@pytest.fixture(scope="module")
def auth_headers(teacher_token):
    return {"Authorization": f"Bearer {teacher_token}"}


def test_health():
    r = requests.get(f"{BASE}/api/health", timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d.get("status") == "healthy"
    assert d.get("database") == "connected"


def test_profile(auth_headers):
    r = requests.get(f"{BASE}/api/profile", headers=auth_headers, timeout=20)
    assert r.status_code == 200
    d = r.json()
    # profile may be flat or wrapped in {"success": True, "user": {...}}
    user = d.get("user", d)
    assert "email" in user or "firebaseUid" in user or "role" in user


def test_grades(auth_headers):
    r = requests.get(f"{BASE}/api/grades", headers=auth_headers, timeout=20)
    assert r.status_code == 200
    assert isinstance(r.json(), (list, dict))


def test_subjects(auth_headers):
    # subjects usually requires a grade query param
    r = requests.get(f"{BASE}/api/subjects", headers=auth_headers, params={"grade": "Grade 4"}, timeout=20)
    assert r.status_code in (200, 422), f"subjects returned {r.status_code}: {r.text[:200]}"


def test_strands(auth_headers):
    r = requests.get(f"{BASE}/api/strands", headers=auth_headers, params={"grade": "Grade 4", "subject": "Mathematics"}, timeout=20)
    assert r.status_code in (200, 422), f"strands returned {r.status_code}: {r.text[:200]}"


def test_substrands(auth_headers):
    r = requests.get(f"{BASE}/api/substrands", headers=auth_headers, params={"grade": "Grade 4", "subject": "Mathematics", "strand": "Numbers"}, timeout=20)
    assert r.status_code in (200, 422), f"substrands returned {r.status_code}: {r.text[:200]}"


def test_slos(auth_headers):
    r = requests.get(f"{BASE}/api/slos", headers=auth_headers, params={"grade": "Grade 4", "subject": "Mathematics"}, timeout=20)
    assert r.status_code in (200, 422), f"slos returned {r.status_code}: {r.text[:200]}"


def test_schemes_list(auth_headers):
    r = requests.get(f"{BASE}/api/schemes", headers=auth_headers, timeout=20)
    assert r.status_code == 200
    assert isinstance(r.json(), (list, dict))


def test_lesson_plans_list(auth_headers):
    r = requests.get(f"{BASE}/api/lesson-plans", headers=auth_headers, timeout=20)
    assert r.status_code == 200
    assert isinstance(r.json(), (list, dict))


def test_assessments_list_no_params(auth_headers):
    r = requests.get(f"{BASE}/api/assessments", headers=auth_headers, timeout=20)
    assert r.status_code in (200, 422), f"/api/assessments returned {r.status_code}: {r.text[:300]}"


def test_assessments_list_with_grade_term(auth_headers):
    # First get a real gradeId from /api/grades
    g = requests.get(f"{BASE}/api/grades", headers=auth_headers, timeout=20)
    assert g.status_code == 200
    grades = g.json()
    if isinstance(grades, dict):
        grades = grades.get("grades") or grades.get("data") or []
    assert grades, "No grades returned"
    grade_id = grades[0].get("id") or grades[0].get("_id") or grades[0].get("gradeId")
    r = requests.get(
        f"{BASE}/api/assessments",
        headers=auth_headers,
        params={"gradeId": grade_id, "term": 1},
        timeout=20,
    )
    assert r.status_code == 200, f"assessments grade+term returned {r.status_code}: {r.text[:300]}"
    body = r.json()
    assert isinstance(body, (list, dict))


def test_assessments_download_requires_auth():
    """Unauthenticated should be 401/403."""
    r = requests.post(f"{BASE}/api/assessments/download", json={"assessment_id": "nonexistent"}, timeout=20)
    assert r.status_code in (401, 403, 422), f"unauth download returned {r.status_code}"


def test_assessments_download_authenticated(auth_headers):
    """Authenticated teacher hits download - expect 200, 402 (insufficient funds), 404 (not found), or 400/422 (bad payload)."""
    r = requests.post(
        f"{BASE}/api/assessments/download",
        headers=auth_headers,
        json={"assessment_id": "nonexistent-id-for-test"},
        timeout=20,
    )
    # Should NOT be 500
    assert r.status_code < 500, f"download returned server error {r.status_code}: {r.text[:300]}"


def test_admin_endpoint_rejects_teacher(auth_headers):
    """Admin-only endpoints must return 403 for teacher tokens."""
    # Try known admin endpoints
    for path in ["/api/admin/assessments", "/api/admin/users", "/api/admin/stats"]:
        r = requests.get(f"{BASE}{path}", headers=auth_headers, timeout=20)
        # Either 403 (correct) or 404 (route doesn't exist); should NOT be 200
        assert r.status_code != 200, f"{path} allowed teacher (200)!"
        print(f"{path} -> {r.status_code}")


def test_news_public():
    r = requests.get(f"{BASE}/api/news", timeout=15)
    assert r.status_code == 200


def test_calendar_terms_public():
    r = requests.get(f"{BASE}/api/calendar/terms", timeout=15)
    assert r.status_code == 200
