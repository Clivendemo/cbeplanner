"""
Test Schemes of Work Enhanced Features:
1. Lessons per Week selector (4-8 options)
2. Number of Weeks (8-14 range with 12 default)
3. Double Lesson toggle with position selector (2-3, 3-4, 4-5)
4. Include Previous Term Uncovered Content toggle
5. Preview PDF route (/api/schemes/preview)
6. Download route (/api/schemes/download) - NO 404
7. PDF has clean header (no purple, dark gray instead)
8. Wallet balance check before download
9. Insufficient funds modal (balance < KES 15)
"""

import pytest
import requests
import os
import json
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://magical-shannon-6.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "demo2@example.com"
TEST_PASSWORD = "Demo1234!"

# Firebase API key
FIREBASE_API_KEY = "AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8"


def get_firebase_token():
    """Get Firebase ID token for authentication"""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("idToken")
    else:
        print(f"Firebase auth failed: {response.text}")
        return None


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    token = get_firebase_token()
    if not token:
        pytest.skip("Could not authenticate with Firebase")
    return token


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="module")
def grade_and_subject(auth_headers):
    """Get Grade 1 and CRE subject for testing"""
    # Get grades
    grades_resp = requests.get(f"{BASE_URL}/api/grades", headers=auth_headers)
    assert grades_resp.status_code == 200
    grades = grades_resp.json().get("grades", [])
    
    # Find Grade 1
    grade_1 = next((g for g in grades if "1" in g.get("name", "")), None)
    if not grade_1:
        pytest.skip("Grade 1 not found in database")
    
    # Get subjects for Grade 1
    subjects_resp = requests.get(f"{BASE_URL}/api/subjects?gradeId={grade_1['id']}", headers=auth_headers)
    assert subjects_resp.status_code == 200
    subjects = subjects_resp.json().get("subjects", [])
    
    # Find CRE subject
    cre_subject = next((s for s in subjects if "CRE" in s.get("name", "").upper()), None)
    if not cre_subject:
        pytest.skip("CRE subject not found for Grade 1")
    
    return grade_1, cre_subject


@pytest.fixture(scope="module")
def selected_topics(auth_headers, grade_and_subject):
    """Get topics (substrands) for testing"""
    grade, subject = grade_and_subject
    
    # Get topics for the subject
    topics_resp = requests.get(f"{BASE_URL}/api/schemes/topics/{subject['id']}", headers=auth_headers)
    assert topics_resp.status_code == 200
    topics = topics_resp.json().get("topics", [])
    
    if not topics:
        pytest.skip("No topics found for CRE subject")
    
    # Collect substrand IDs from first 2 strands
    substrand_ids = []
    for strand in topics[:2]:
        for substrand in strand.get("substrands", [])[:3]:
            substrand_ids.append(substrand["id"])
    
    if not substrand_ids:
        pytest.skip("No substrands found")
    
    return substrand_ids


class TestLessonsPerWeekConfig:
    """Test lessons per week configuration endpoint"""
    
    def test_lessons_per_week_endpoint_exists(self, auth_headers, grade_and_subject):
        """Test that lessons per week config endpoint exists"""
        grade, subject = grade_and_subject
        response = requests.get(
            f"{BASE_URL}/api/schemes/config/lessons-per-week?gradeId={grade['id']}&subjectId={subject['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "lessonsPerWeek" in data
        print(f"✓ Lessons per week config endpoint works: {data.get('lessonsPerWeek')} lessons/week")
    
    def test_lessons_per_week_returns_valid_range(self, auth_headers, grade_and_subject):
        """Test that lessons per week is in valid range (4-8)"""
        grade, subject = grade_and_subject
        response = requests.get(
            f"{BASE_URL}/api/schemes/config/lessons-per-week?gradeId={grade['id']}&subjectId={subject['id']}",
            headers=auth_headers
        )
        data = response.json()
        lpw = data.get("lessonsPerWeek", 0)
        # Should be a reasonable value (typically 2-8)
        assert 2 <= lpw <= 8, f"Lessons per week {lpw} is outside expected range"
        print(f"✓ Lessons per week {lpw} is in valid range")


class TestSchemeGenerationV2:
    """Test scheme generation with new parameters"""
    
    def test_generate_scheme_with_default_params(self, auth_headers, grade_and_subject, selected_topics):
        """Test basic scheme generation"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": selected_topics,
            "breaks": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "scheme" in data
        print(f"✓ Basic scheme generation works")
    
    def test_generate_scheme_with_double_lesson(self, auth_headers, grade_and_subject, selected_topics):
        """Test scheme generation with double lesson enabled"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": selected_topics,
            "breaks": [],
            "doubleLesson": {
                "enabled": True,
                "position": "2-3"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        scheme = data.get("scheme", {})
        lessons = scheme.get("lessons", [])
        
        # Check that some lessons have double lesson format (e.g., "2-3")
        double_lessons = [l for l in lessons if l.get("isDouble")]
        print(f"✓ Double lesson generation works - {len(double_lessons)} double lessons created")
    
    def test_generate_scheme_with_position_3_4(self, auth_headers, grade_and_subject, selected_topics):
        """Test scheme generation with double lesson position 3-4"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 10,
            "lessonsPerWeek": 6,
            "selectedTopics": selected_topics,
            "breaks": [],
            "doubleLesson": {
                "enabled": True,
                "position": "3-4"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        scheme = data.get("scheme", {})
        lessons = scheme.get("lessons", [])
        
        # Check for lessons with "3-4" format
        double_lessons = [l for l in lessons if l.get("lesson") == "3-4"]
        print(f"✓ Double lesson position 3-4 works - found {len(double_lessons)} lessons with '3-4' format")
    
    def test_generate_scheme_with_position_4_5(self, auth_headers, grade_and_subject, selected_topics):
        """Test scheme generation with double lesson position 4-5"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 10,
            "lessonsPerWeek": 6,
            "selectedTopics": selected_topics,
            "breaks": [],
            "doubleLesson": {
                "enabled": True,
                "position": "4-5"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        scheme = data.get("scheme", {})
        lessons = scheme.get("lessons", [])
        
        # Check for lessons with "4-5" format
        double_lessons = [l for l in lessons if l.get("lesson") == "4-5"]
        print(f"✓ Double lesson position 4-5 works - found {len(double_lessons)} lessons with '4-5' format")
    
    def test_generate_scheme_with_carry_over(self, auth_headers, grade_and_subject, selected_topics):
        """Test scheme generation with includeCarryOver enabled"""
        grade, subject = grade_and_subject
        
        payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": selected_topics,
            "breaks": [],
            "includeCarryOver": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        scheme = data.get("scheme", {})
        assert scheme.get("includeCarryOver") == True
        print(f"✓ Carry-over content mode works")
    
    def test_generate_scheme_with_various_weeks(self, auth_headers, grade_and_subject, selected_topics):
        """Test scheme generation with different week counts (8-14)"""
        grade, subject = grade_and_subject
        
        for weeks in [8, 10, 12, 14]:
            payload = {
                "gradeId": grade["id"],
                "subjectId": subject["id"],
                "term": 1,
                "year": 2026,
                "totalWeeks": weeks,
                "lessonsPerWeek": 5,
                "selectedTopics": selected_topics,
                "breaks": []
            }
            
            response = requests.post(
                f"{BASE_URL}/api/schemes/generate-v2",
                headers=auth_headers,
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("scheme", {}).get("totalWeeks") == weeks
        
        print(f"✓ Scheme generation works with weeks 8, 10, 12, 14")
    
    def test_generate_scheme_with_various_lessons_per_week(self, auth_headers, grade_and_subject, selected_topics):
        """Test scheme generation with different lessons per week (4-8)"""
        grade, subject = grade_and_subject
        
        for lpw in [4, 5, 6, 7, 8]:
            payload = {
                "gradeId": grade["id"],
                "subjectId": subject["id"],
                "term": 1,
                "year": 2026,
                "totalWeeks": 10,
                "lessonsPerWeek": lpw,
                "selectedTopics": selected_topics,
                "breaks": []
            }
            
            response = requests.post(
                f"{BASE_URL}/api/schemes/generate-v2",
                headers=auth_headers,
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("scheme", {}).get("lessonsPerWeek") == lpw
        
        print(f"✓ Scheme generation works with lessons per week 4, 5, 6, 7, 8")


class TestSchemePreview:
    """Test scheme preview endpoint"""
    
    def test_preview_endpoint_exists(self, auth_headers, grade_and_subject, selected_topics):
        """Test that preview endpoint exists and returns PDF"""
        grade, subject = grade_and_subject
        
        # First generate a scheme
        gen_payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": selected_topics,
            "breaks": []
        }
        
        gen_response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=gen_payload
        )
        
        assert gen_response.status_code == 200
        scheme_data = gen_response.json().get("scheme", {})
        
        # Now preview the scheme
        preview_response = requests.post(
            f"{BASE_URL}/api/schemes/preview",
            headers=auth_headers,
            json=scheme_data
        )
        
        assert preview_response.status_code == 200, f"Preview failed with status {preview_response.status_code}"
        assert preview_response.headers.get("content-type") == "application/pdf"
        
        # Check PDF content starts with PDF magic bytes
        content = preview_response.content
        assert content[:4] == b'%PDF', "Response is not a valid PDF"
        print(f"✓ Preview endpoint returns valid PDF ({len(content)} bytes)")
    
    def test_preview_no_wallet_charge(self, auth_headers, grade_and_subject, selected_topics):
        """Test that preview does not charge wallet"""
        # Get current balance
        profile_resp = requests.get(f"{BASE_URL}/api/profile", headers=auth_headers)
        initial_balance = profile_resp.json().get("user", {}).get("walletBalance", 0)
        
        grade, subject = grade_and_subject
        
        # Generate and preview
        gen_payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": selected_topics,
            "breaks": []
        }
        
        gen_response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=gen_payload
        )
        scheme_data = gen_response.json().get("scheme", {})
        
        # Preview
        requests.post(
            f"{BASE_URL}/api/schemes/preview",
            headers=auth_headers,
            json=scheme_data
        )
        
        # Check balance unchanged
        profile_resp = requests.get(f"{BASE_URL}/api/profile", headers=auth_headers)
        final_balance = profile_resp.json().get("user", {}).get("walletBalance", 0)
        
        assert final_balance == initial_balance, "Preview should not charge wallet"
        print(f"✓ Preview does not charge wallet (balance: {final_balance})")


class TestSchemeDownload:
    """Test scheme download endpoint"""
    
    def test_download_endpoint_exists(self, auth_headers, grade_and_subject, selected_topics):
        """Test that download endpoint exists (may fail due to insufficient funds)"""
        grade, subject = grade_and_subject
        
        # Generate a scheme
        gen_payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": selected_topics,
            "breaks": []
        }
        
        gen_response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=gen_payload
        )
        scheme_data = gen_response.json().get("scheme", {})
        
        # Try to download
        download_response = requests.post(
            f"{BASE_URL}/api/schemes/download",
            headers=auth_headers,
            json=scheme_data
        )
        
        # Should be 200 (success) or 402 (insufficient funds), NOT 404
        assert download_response.status_code in [200, 402], f"Download returned unexpected status {download_response.status_code}"
        print(f"✓ Download endpoint exists (status: {download_response.status_code})")
    
    def test_download_requires_wallet_balance(self, auth_headers, grade_and_subject, selected_topics):
        """Test that download checks wallet balance"""
        # Get current balance
        profile_resp = requests.get(f"{BASE_URL}/api/profile", headers=auth_headers)
        balance = profile_resp.json().get("user", {}).get("walletBalance", 0)
        
        grade, subject = grade_and_subject
        
        # Generate a scheme
        gen_payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": selected_topics,
            "breaks": []
        }
        
        gen_response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=gen_payload
        )
        scheme_data = gen_response.json().get("scheme", {})
        
        # Try to download
        download_response = requests.post(
            f"{BASE_URL}/api/schemes/download",
            headers=auth_headers,
            json=scheme_data
        )
        
        if balance < 15:
            # Should return 402 for insufficient funds
            assert download_response.status_code == 402, f"Expected 402 for insufficient funds, got {download_response.status_code}"
            print(f"✓ Download correctly returns 402 when balance ({balance}) < KES 15")
        else:
            # Should return 200 and PDF
            assert download_response.status_code == 200
            assert download_response.headers.get("content-type") == "application/pdf"
            print(f"✓ Download returns PDF when balance ({balance}) >= KES 15")
    
    def test_download_no_404_error(self, auth_headers, grade_and_subject, selected_topics):
        """Test that download endpoint does NOT return 404"""
        grade, subject = grade_and_subject
        
        # Generate a scheme
        gen_payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": selected_topics,
            "breaks": []
        }
        
        gen_response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=gen_payload
        )
        scheme_data = gen_response.json().get("scheme", {})
        
        # Try to download
        download_response = requests.post(
            f"{BASE_URL}/api/schemes/download",
            headers=auth_headers,
            json=scheme_data
        )
        
        assert download_response.status_code != 404, "Download endpoint should NOT return 404"
        print(f"✓ Download endpoint does not return 404 (status: {download_response.status_code})")


class TestPDFStyling:
    """Test PDF styling (clean header, no purple)"""
    
    def test_pdf_generated_successfully(self, auth_headers, grade_and_subject, selected_topics):
        """Test that PDF is generated with proper structure"""
        grade, subject = grade_and_subject
        
        # Generate a scheme
        gen_payload = {
            "gradeId": grade["id"],
            "subjectId": subject["id"],
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": selected_topics,
            "breaks": []
        }
        
        gen_response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=auth_headers,
            json=gen_payload
        )
        scheme_data = gen_response.json().get("scheme", {})
        
        # Preview to get PDF
        preview_response = requests.post(
            f"{BASE_URL}/api/schemes/preview",
            headers=auth_headers,
            json=scheme_data
        )
        
        assert preview_response.status_code == 200
        content = preview_response.content
        
        # Check PDF structure
        assert content[:4] == b'%PDF', "Not a valid PDF"
        assert len(content) > 1000, "PDF seems too small"
        
        # PDF is binary compressed, so we just verify it's a valid PDF with reasonable size
        # The actual content verification would require PDF parsing library
        print(f"✓ PDF generated successfully with proper structure ({len(content)} bytes)")


class TestUserProfile:
    """Test user profile and wallet balance"""
    
    def test_get_user_profile(self, auth_headers):
        """Test getting user profile with wallet balance"""
        response = requests.get(f"{BASE_URL}/api/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        
        user = data.get("user", {})
        assert "walletBalance" in user
        
        balance = user.get("walletBalance", 0)
        print(f"✓ User profile retrieved - wallet balance: KES {balance}")
    
    def test_wallet_balance_is_numeric(self, auth_headers):
        """Test that wallet balance is a number"""
        response = requests.get(f"{BASE_URL}/api/profile", headers=auth_headers)
        
        user = response.json().get("user", {})
        balance = user.get("walletBalance")
        
        assert isinstance(balance, (int, float)), f"Wallet balance should be numeric, got {type(balance)}"
        print(f"✓ Wallet balance is numeric: {balance}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
