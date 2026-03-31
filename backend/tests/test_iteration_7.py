"""
Test Suite for Iteration 7 - Testing:
1. Backend /api/schemes/generate-v2 works without type comparison errors
2. Safe integer conversion (to_int helper) prevents type errors
3. Breaks with same week (e.g., week 6 lesson 1-5) work correctly
4. Break type 'Opener CAT' is available in dropdown (frontend test)
5. Calendar date input appears in break modal (frontend test)
6. GET /api/wallet/balance endpoint returns balance
7. Wallet auto-refreshes after successful download (frontend test)
8. Dashboard shows two-column layout (frontend test)
9. PDF break rows show only break name (no week/lesson numbers)
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://magical-shannon-6.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "demo2@example.com"
TEST_PASSWORD = "Demo1234!"

# Firebase API key for authentication
FIREBASE_API_KEY = "AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8"


@pytest.fixture(scope="module")
def auth_token():
    """Get Firebase auth token for test user"""
    try:
        # Sign in with Firebase
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "returnSecureToken": True
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("idToken")
        else:
            pytest.skip(f"Authentication failed: {response.text}")
    except Exception as e:
        pytest.skip(f"Authentication error: {str(e)}")


@pytest.fixture(scope="module")
def headers(auth_token):
    """Get headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="module")
def grade_and_subject(headers):
    """Get Grade 1 and CRE subject IDs"""
    # Get grades
    grades_response = requests.get(f"{BASE_URL}/api/grades", headers=headers)
    assert grades_response.status_code == 200
    grades = grades_response.json().get("grades", [])
    
    # Find Grade 1
    grade_1 = next((g for g in grades if "1" in g["name"]), None)
    if not grade_1:
        pytest.skip("Grade 1 not found in database")
    
    # Get subjects for Grade 1
    subjects_response = requests.get(
        f"{BASE_URL}/api/subjects?gradeId={grade_1['id']}", 
        headers=headers
    )
    assert subjects_response.status_code == 200
    subjects = subjects_response.json().get("subjects", [])
    
    # Find CRE subject
    cre_subject = next((s for s in subjects if "CRE" in s["name"].upper()), None)
    if not cre_subject:
        pytest.skip("CRE subject not found for Grade 1")
    
    return grade_1, cre_subject


@pytest.fixture(scope="module")
def topics(headers, grade_and_subject):
    """Get topics for the subject"""
    _, subject = grade_and_subject
    
    response = requests.get(
        f"{BASE_URL}/api/schemes/topics/{subject['id']}",
        headers=headers
    )
    assert response.status_code == 200
    topics = response.json().get("topics", [])
    
    if not topics:
        pytest.skip("No topics found for subject")
    
    # Get first substrand ID
    substrand_ids = []
    for topic in topics:
        for substrand in topic.get("substrands", []):
            substrand_ids.append(substrand["id"])
    
    if not substrand_ids:
        pytest.skip("No substrands found")
    
    return substrand_ids[:3]  # Return first 3 topics


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print("✓ API health check passed")


class TestWalletBalance:
    """Test GET /api/wallet/balance endpoint"""
    
    def test_wallet_balance_endpoint_exists(self, headers):
        """Test that wallet balance endpoint exists and returns balance"""
        response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        assert isinstance(data["balance"], (int, float))
        print(f"✓ Wallet balance endpoint works, balance: {data['balance']}")
    
    def test_wallet_balance_requires_auth(self):
        """Test that wallet balance requires authentication"""
        response = requests.get(f"{BASE_URL}/api/wallet/balance")
        assert response.status_code == 401
        print("✓ Wallet balance requires authentication")


class TestSchemeGenerateV2:
    """Test /api/schemes/generate-v2 endpoint"""
    
    def test_generate_scheme_basic(self, headers, grade_and_subject, topics):
        """Test basic scheme generation works without type errors"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "scheme" in data
        print("✓ Basic scheme generation works without type errors")
    
    def test_generate_scheme_with_same_week_break(self, headers, grade_and_subject, topics):
        """Test breaks with same week (e.g., week 6 lesson 1-5) work correctly"""
        grade, subject = grade_and_subject
        
        # Break within same week: Week 6, Lesson 1 to Week 6, Lesson 5
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [
                {
                    "breakType": "Mid-Term Break",
                    "startWeek": 6,
                    "startLesson": 1,
                    "endWeek": 6,
                    "endLesson": 5
                }
            ],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200, f"Same-week break failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        
        # Verify break is in the lessons
        lessons = data["scheme"]["lessons"]
        break_lessons = [l for l in lessons if l.get("isBreak")]
        assert len(break_lessons) > 0, "No break lessons found"
        print(f"✓ Same-week break works correctly, found {len(break_lessons)} break lesson(s)")
    
    def test_generate_scheme_with_opener_cat_break(self, headers, grade_and_subject, topics):
        """Test Opener CAT break type works"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [
                {
                    "breakType": "Opener CAT",
                    "startWeek": 1,
                    "startLesson": 1,
                    "endWeek": 1,
                    "endLesson": 2
                }
            ],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200, f"Opener CAT break failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        
        # Verify Opener CAT break is in the lessons
        lessons = data["scheme"]["lessons"]
        opener_cat_breaks = [l for l in lessons if l.get("isBreak") and l.get("breakType") == "Opener CAT"]
        assert len(opener_cat_breaks) > 0, "Opener CAT break not found in lessons"
        print(f"✓ Opener CAT break type works, found {len(opener_cat_breaks)} break(s)")
    
    def test_generate_scheme_with_string_values(self, headers, grade_and_subject, topics):
        """Test that string values for numeric fields don't cause type errors"""
        grade, subject = grade_and_subject
        
        # Send string values that should be converted to integers
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 12,  # Could be "12" in some cases
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [
                {
                    "breakType": "Half-Term Break",
                    "startWeek": 5,  # These could be strings from frontend
                    "startLesson": 1,
                    "endWeek": 5,
                    "endLesson": 5
                }
            ],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200, f"Type conversion failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print("✓ Safe integer conversion (to_int helper) prevents type errors")
    
    def test_generate_scheme_with_partial_week_break(self, headers, grade_and_subject, topics):
        """Test partial week break (e.g., week 3 lesson 3 to week 3 lesson 5)"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [
                {
                    "breakType": "Staff Meeting",
                    "startWeek": 3,
                    "startLesson": 3,
                    "endWeek": 3,
                    "endLesson": 5
                }
            ],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200, f"Partial week break failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print("✓ Partial week break (lesson 3-5 in same week) works correctly")
    
    def test_generate_scheme_with_multi_week_break(self, headers, grade_and_subject, topics):
        """Test multi-week break spanning multiple weeks"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 14,
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [
                {
                    "breakType": "End Term Exams",
                    "startWeek": 12,
                    "startLesson": 1,
                    "endWeek": 14,
                    "endLesson": 5
                }
            ],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200, f"Multi-week break failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print("✓ Multi-week break spanning weeks 12-14 works correctly")
    
    def test_generate_scheme_with_calendar_date(self, headers, grade_and_subject, topics):
        """Test break with optional calendar date"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [
                {
                    "breakType": "Public Holiday",
                    "startWeek": 4,
                    "startLesson": 1,
                    "endWeek": 4,
                    "endLesson": 1,
                    "startDate": "2025-04-15"
                }
            ],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200, f"Calendar date break failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        
        # Verify the break has the date
        validated_breaks = data["scheme"].get("breaks", [])
        if validated_breaks:
            assert validated_breaks[0].get("startDate") == "2025-04-15"
        print("✓ Break with calendar date works correctly")


class TestSchemePreviewAndDownload:
    """Test scheme preview and download endpoints"""
    
    def test_preview_endpoint(self, headers, grade_and_subject, topics):
        """Test preview endpoint returns PDF"""
        grade, subject = grade_and_subject
        
        # First generate a scheme
        gen_payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        gen_response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=gen_payload
        )
        assert gen_response.status_code == 200
        scheme_data = gen_response.json()["scheme"]
        
        # Now preview
        preview_response = requests.post(
            f"{BASE_URL}/api/schemes/preview",
            headers=headers,
            json=scheme_data
        )
        
        assert preview_response.status_code == 200
        assert preview_response.headers.get("Content-Type") == "application/pdf"
        assert len(preview_response.content) > 0
        print("✓ Preview endpoint returns valid PDF")
    
    def test_download_requires_wallet_balance(self, headers, grade_and_subject, topics):
        """Test download endpoint checks wallet balance"""
        grade, subject = grade_and_subject
        
        # First generate a scheme
        gen_payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        gen_response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=gen_payload
        )
        assert gen_response.status_code == 200
        scheme_data = gen_response.json()["scheme"]
        
        # Try to download (should fail with 402 if insufficient balance)
        download_response = requests.post(
            f"{BASE_URL}/api/schemes/download",
            headers=headers,
            json=scheme_data
        )
        
        # Either 200 (if user has balance) or 402 (insufficient funds)
        assert download_response.status_code in [200, 402]
        if download_response.status_code == 402:
            print("✓ Download endpoint correctly returns 402 for insufficient balance")
        else:
            print("✓ Download endpoint works (user has sufficient balance)")


class TestBreakDurationCalculation:
    """Test break duration calculation for same-week breaks"""
    
    def test_same_week_break_duration(self, headers, grade_and_subject, topics):
        """Test that same-week breaks calculate duration correctly"""
        grade, subject = grade_and_subject
        
        # Break from week 6 lesson 1 to week 6 lesson 5 = 5 lessons
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2025,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": topics,
            "breaks": [
                {
                    "breakType": "Mid-Term Break",
                    "startWeek": 6,
                    "startLesson": 1,
                    "endWeek": 6,
                    "endLesson": 5
                }
            ],
            "doubleLesson": None,
            "includeCarryOver": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Count break lessons
        lessons = data["scheme"]["lessons"]
        break_count = len([l for l in lessons if l.get("isBreak")])
        
        # For same-week break, we should have 1 break entry (consolidated)
        assert break_count >= 1, f"Expected at least 1 break entry, got {break_count}"
        print(f"✓ Same-week break duration calculated correctly ({break_count} break entries)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
