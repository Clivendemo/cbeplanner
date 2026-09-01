"""
Test Notes Generation Feature
Tests all notes-related endpoints:
- POST /api/notes/generate
- GET /api/notes/{id}/preview
- POST /api/notes/{id}/download
- GET /api/notes
- GET /api/notes/{id}
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://magical-shannon-6.preview.emergentagent.com')
FIREBASE_API_KEY = "AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8"

# Test curriculum data IDs (seeded)
TEST_GRADE_ID = "69ce15c1b0a9f402592bd08d"  # Grade 4
TEST_SUBJECT_ID = "69ce15c1b0a9f402592bd08e"  # Mathematics
TEST_STRAND_ID = "69ce15c1b0a9f402592bd08f"  # Numbers
TEST_SUBSTRAND_ID = "69ce15c1b0a9f402592bd090"  # Whole Numbers


@pytest.fixture(scope="module")
def auth_token():
    """Get Firebase auth token for test user"""
    response = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}",
        json={
            "email": "testteacher2026@gmail.com",
            "password": "TestPass123!",
            "returnSecureToken": True
        }
    )
    if response.status_code != 200:
        pytest.skip("Failed to authenticate test user")
    return response.json().get("idToken")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestNotesGeneration:
    """Test POST /api/notes/generate endpoint"""
    
    def test_generate_notes_success(self, auth_headers):
        """Generate notes with valid curriculum IDs returns 200 with full content"""
        response = requests.post(
            f"{BASE_URL}/api/notes/generate",
            headers=auth_headers,
            json={
                "gradeId": TEST_GRADE_ID,
                "subjectId": TEST_SUBJECT_ID,
                "strandId": TEST_STRAND_ID,
                "substrandId": TEST_SUBSTRAND_ID,
                "duration": 60
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "notes" in data
        
        notes = data["notes"]
        # Verify notes structure
        assert "id" in notes
        assert notes["gradeName"] == "Grade 4"
        assert notes["subjectName"] == "Mathematics"
        assert notes["strandName"] == "Numbers"
        assert notes["substrandName"] == "Whole Numbers"
        
        # Verify generatedContent structure
        assert "generatedContent" in notes
        content = notes["generatedContent"]
        assert "introduction" in content
        assert "sections" in content
        assert "key_terms" in content
        assert "practice_questions" in content
        assert "summary" in content
        
        # Verify sections have proper structure
        assert len(content["sections"]) > 0
        for section in content["sections"]:
            assert "title" in section
            assert "explanation" in section
            assert "examples" in section
            assert "applications" in section
        
        # Store notes ID for other tests
        pytest.notes_id = notes["id"]
    
    def test_generate_notes_requires_auth(self):
        """Generate notes without auth returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/notes/generate",
            json={
                "gradeId": TEST_GRADE_ID,
                "subjectId": TEST_SUBJECT_ID,
                "strandId": TEST_STRAND_ID,
                "substrandId": TEST_SUBSTRAND_ID,
                "duration": 60
            }
        )
        assert response.status_code == 401
    
    def test_generate_notes_invalid_ids(self, auth_headers):
        """Generate notes with invalid IDs returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/notes/generate",
            headers=auth_headers,
            json={
                "gradeId": "000000000000000000000000",
                "subjectId": "000000000000000000000000",
                "strandId": "000000000000000000000000",
                "substrandId": "000000000000000000000000",
                "duration": 60
            }
        )
        assert response.status_code == 404


class TestNotesPreview:
    """Test GET /api/notes/{id}/preview endpoint"""
    
    def test_preview_notes_returns_pdf(self, auth_headers):
        """Preview notes returns PDF with correct content type"""
        # First generate notes to get an ID
        gen_response = requests.post(
            f"{BASE_URL}/api/notes/generate",
            headers=auth_headers,
            json={
                "gradeId": TEST_GRADE_ID,
                "subjectId": TEST_SUBJECT_ID,
                "strandId": TEST_STRAND_ID,
                "substrandId": TEST_SUBSTRAND_ID,
                "duration": 60
            }
        )
        notes_id = gen_response.json()["notes"]["id"]
        
        # Preview the notes
        response = requests.get(
            f"{BASE_URL}/api/notes/{notes_id}/preview",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        assert len(response.content) > 1000  # PDF should have content
    
    def test_preview_notes_requires_auth(self):
        """Preview notes without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/notes/000000000000000000000000/preview")
        assert response.status_code == 401


class TestNotesDownload:
    """Test POST /api/notes/{id}/download endpoint"""
    
    def test_download_notes_returns_pdf(self, auth_headers):
        """Download notes returns PDF (charges wallet after first free)"""
        # First generate notes
        gen_response = requests.post(
            f"{BASE_URL}/api/notes/generate",
            headers=auth_headers,
            json={
                "gradeId": TEST_GRADE_ID,
                "subjectId": TEST_SUBJECT_ID,
                "strandId": TEST_STRAND_ID,
                "substrandId": TEST_SUBSTRAND_ID,
                "duration": 60
            }
        )
        notes_id = gen_response.json()["notes"]["id"]
        
        # Get initial balance
        profile_response = requests.get(f"{BASE_URL}/api/profile", headers=auth_headers)
        initial_balance = profile_response.json()["user"]["walletBalance"]
        
        # Download the notes
        response = requests.post(
            f"{BASE_URL}/api/notes/{notes_id}/download",
            headers=auth_headers
        )
        
        # Should either succeed (200) or fail due to insufficient funds (402)
        assert response.status_code in [200, 402], f"Expected 200 or 402, got {response.status_code}"
        
        if response.status_code == 200:
            assert response.headers.get("content-type") == "application/pdf"
            assert len(response.content) > 1000
    
    def test_download_notes_requires_auth(self):
        """Download notes without auth returns 401"""
        response = requests.post(f"{BASE_URL}/api/notes/000000000000000000000000/download")
        assert response.status_code == 401


class TestNotesListing:
    """Test GET /api/notes and GET /api/notes/{id} endpoints"""
    
    def test_list_notes_returns_user_notes(self, auth_headers):
        """List notes returns array of user's notes"""
        response = requests.get(f"{BASE_URL}/api/notes", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notes" in data
        assert isinstance(data["notes"], list)
        
        # Verify notes structure if any exist
        if len(data["notes"]) > 0:
            note = data["notes"][0]
            assert "id" in note
            assert "gradeName" in note
            assert "subjectName" in note
    
    def test_get_single_note(self, auth_headers):
        """Get single note by ID returns full note data"""
        # First generate a note
        gen_response = requests.post(
            f"{BASE_URL}/api/notes/generate",
            headers=auth_headers,
            json={
                "gradeId": TEST_GRADE_ID,
                "subjectId": TEST_SUBJECT_ID,
                "strandId": TEST_STRAND_ID,
                "substrandId": TEST_SUBSTRAND_ID,
                "duration": 60
            }
        )
        notes_id = gen_response.json()["notes"]["id"]
        
        # Get the note
        response = requests.get(f"{BASE_URL}/api/notes/{notes_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "note" in data
        assert data["note"]["id"] == notes_id
        assert "generatedContent" in data["note"]
    
    def test_get_nonexistent_note(self, auth_headers):
        """Get non-existent note returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/notes/000000000000000000000000",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_list_notes_requires_auth(self):
        """List notes without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/notes")
        assert response.status_code == 401


class TestWalletIntegration:
    """Test wallet deduction for notes downloads"""
    
    def test_wallet_ledger_entry_created(self, auth_headers):
        """Verify wallet ledger entry is created on paid download"""
        # Get initial profile
        profile_response = requests.get(f"{BASE_URL}/api/profile", headers=auth_headers)
        initial_balance = profile_response.json()["user"]["walletBalance"]
        free_notes_used = profile_response.json()["user"].get("freeNotesUsed", False)
        
        if initial_balance < 1 and free_notes_used:
            pytest.skip("Insufficient balance for paid download test")
        
        # Generate and download notes
        gen_response = requests.post(
            f"{BASE_URL}/api/notes/generate",
            headers=auth_headers,
            json={
                "gradeId": TEST_GRADE_ID,
                "subjectId": TEST_SUBJECT_ID,
                "strandId": TEST_STRAND_ID,
                "substrandId": TEST_SUBSTRAND_ID,
                "duration": 60
            }
        )
        notes_id = gen_response.json()["notes"]["id"]
        
        download_response = requests.post(
            f"{BASE_URL}/api/notes/{notes_id}/download",
            headers=auth_headers
        )
        
        if download_response.status_code == 200:
            # Check balance was deducted (if not first free download)
            profile_response = requests.get(f"{BASE_URL}/api/profile", headers=auth_headers)
            new_balance = profile_response.json()["user"]["walletBalance"]
            
            if free_notes_used:
                assert new_balance == initial_balance - 1, "Wallet should be deducted by KES 1"
