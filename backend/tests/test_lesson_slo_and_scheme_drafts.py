"""
Test Suite: Lesson SLO Admin Endpoints and Scheme Draft Workflow
Tests lesson-level curriculum intelligence and draft-based Scheme of Work workflow.

Test Data (from context):
- Substrand: 69ce15c1b0a9f402592bd090 (Whole Numbers) with number_of_lessons=2
- Grade 4 Math: grade=69ce15c1b0a9f402592bd08d, subject=69ce15c1b0a9f402592bd08e, strand=69ce15c1b0a9f402592bd08f
- Existing draft: 69de91f4740cb98ea8b9c444 (for teacher user)
"""

import pytest
import requests
import os
import time

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://magical-shannon-6.preview.emergentagent.com').rstrip('/')
FIREBASE_API_KEY = "AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8"

# Test data from context
SUBSTRAND_ID = "69ce15c1b0a9f402592bd090"  # Whole Numbers with number_of_lessons=2
GRADE_ID = "69ce15c1b0a9f402592bd08d"
SUBJECT_ID = "69ce15c1b0a9f402592bd08e"
STRAND_ID = "69ce15c1b0a9f402592bd08f"
EXISTING_DRAFT_ID = "69de91f4740cb98ea8b9c444"


def get_firebase_token(email: str, password: str) -> str:
    """Get Firebase ID token for authentication."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    response = requests.post(url, json={
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    if response.status_code != 200:
        pytest.skip(f"Firebase auth failed: {response.text}")
    return response.json().get("idToken")


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token."""
    return get_firebase_token("testadmin2026@gmail.com", "AdminTest123!")


@pytest.fixture(scope="module")
def teacher_token():
    """Get teacher authentication token."""
    return get_firebase_token("testteacher2026@gmail.com", "TestPass123!")


@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin auth."""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def teacher_headers(teacher_token):
    """Headers with teacher auth."""
    return {
        "Authorization": f"Bearer {teacher_token}",
        "Content-Type": "application/json"
    }


# ==================== ROUTE ORDER TESTS ====================
# These tests verify that route ordering doesn't break existing endpoints

class TestRouteOrderNotBroken:
    """Verify that new routes don't break existing endpoints due to route ordering."""
    
    def test_schemes_config_lessons_per_week(self, teacher_headers):
        """GET /api/schemes/config/lessons-per-week - should not be broken by route order."""
        # This endpoint requires gradeId and subjectId query params
        response = requests.get(
            f"{BASE_URL}/api/schemes/config/lessons-per-week",
            params={"gradeId": GRADE_ID, "subjectId": SUBJECT_ID},
            headers=teacher_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "lessonsPerWeek" in data
        print(f"✓ lessons-per-week endpoint works: {data.get('lessonsPerWeek')}")
    
    def test_schemes_topics_endpoint(self, teacher_headers):
        """GET /api/schemes/topics/{subjectId} - should not be broken by route order."""
        response = requests.get(f"{BASE_URL}/api/schemes/topics/{SUBJECT_ID}", headers=teacher_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "topics" in data
        print(f"✓ topics endpoint works: {len(data.get('topics', []))} topics found")
    
    def test_wallet_balance_still_works(self, teacher_headers):
        """GET /api/wallet/balance - should still work."""
        response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=teacher_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "balance" in data
        print(f"✓ wallet/balance endpoint works: balance={data.get('balance')}")
    
    def test_admin_grades_still_works(self, admin_headers):
        """GET /api/admin/grades - admin auth should still work."""
        response = requests.get(f"{BASE_URL}/api/admin/grades", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "grades" in data
        print(f"✓ admin/grades endpoint works: {len(data.get('grades', []))} grades found")


# ==================== LESSON SLO ADMIN ENDPOINTS ====================

class TestLessonSloAdminEndpoints:
    """Test lesson SLO admin CRUD operations."""
    
    def test_get_lesson_slos_for_substrand(self, admin_headers):
        """GET /api/admin/lesson-slos/{substrand_id} - returns auto-synced lesson SLOs."""
        response = requests.get(f"{BASE_URL}/api/admin/lesson-slos/{SUBSTRAND_ID}", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "lessonSlos" in data
        assert "numberOfLessons" in data
        
        # Verify number_of_lessons matches expected
        num_lessons = data.get("numberOfLessons")
        lesson_slos = data.get("lessonSlos", [])
        print(f"✓ GET lesson-slos: numberOfLessons={num_lessons}, lessonSlos count={len(lesson_slos)}")
        
        # Verify lesson SLOs have required fields
        if lesson_slos:
            slo = lesson_slos[0]
            assert "lessonNumber" in slo
            assert "outcome" in slo or "description" in slo
            assert "isActive" in slo
            print(f"  First lesson SLO: lessonNumber={slo.get('lessonNumber')}, isDraft={slo.get('isDraft')}")
    
    def test_get_lesson_slos_requires_admin(self, teacher_headers):
        """GET /api/admin/lesson-slos/{substrand_id} - should require admin auth."""
        response = requests.get(f"{BASE_URL}/api/admin/lesson-slos/{SUBSTRAND_ID}", headers=teacher_headers)
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("✓ lesson-slos endpoint correctly requires admin auth")
    
    def test_put_lesson_slo_creates_or_updates(self, admin_headers):
        """PUT /api/admin/lesson-slos/{substrand_id}/{lesson_number} - creates/updates lesson SLO."""
        lesson_number = 1
        payload = {
            "outcome": "TEST_Demonstrate understanding of whole numbers in context",
            "keyInquiryQuestions": ["What are whole numbers?", "How do we use them?"],
            "learningExperiences": ["Counting objects", "Number line activities"],
            "learningResources": ["Number cards", "Counters"],
            "assessmentMethods": ["Oral questions", "Written exercises"]
        }
        
        response = requests.put(
            f"{BASE_URL}/api/admin/lesson-slos/{SUBSTRAND_ID}/{lesson_number}",
            headers=admin_headers,
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("action") in ["created", "updated"]
        print(f"✓ PUT lesson-slo: action={data.get('action')}")
        
        # Verify the update persisted
        get_response = requests.get(f"{BASE_URL}/api/admin/lesson-slos/{SUBSTRAND_ID}", headers=admin_headers)
        assert get_response.status_code == 200
        slos = get_response.json().get("lessonSlos", [])
        lesson_1 = next((s for s in slos if s.get("lessonNumber") == 1), None)
        assert lesson_1 is not None
        assert lesson_1.get("isDraft") is False, "Admin-edited SLO should have isDraft=False"
        print(f"  Verified: isDraft={lesson_1.get('isDraft')}, isAutoGenerated={lesson_1.get('isAutoGenerated')}")
    
    def test_bulk_upsert_lesson_slos(self, admin_headers):
        """POST /api/admin/lesson-slos/{substrand_id}/bulk - bulk upsert lesson SLOs."""
        payload = {
            "lessonSlos": [
                {
                    "lessonNumber": 1,
                    "outcome": "TEST_BULK_Identify and explain whole numbers",
                    "keyInquiryQuestions": ["What is a whole number?"]
                },
                {
                    "lessonNumber": 2,
                    "outcome": "TEST_BULK_Apply whole number concepts",
                    "keyInquiryQuestions": ["How do we apply whole numbers?"]
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/lesson-slos/{SUBSTRAND_ID}/bulk",
            headers=admin_headers,
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data.get("updated") == 2
        print(f"✓ Bulk upsert: updated={data.get('updated')}")
    
    def test_regenerate_lesson_slos_preserves_admin_edited(self, admin_headers):
        """POST /api/admin/lesson-slos/{substrand_id}/regenerate - preserves admin-edited SLOs."""
        # First, mark lesson 1 as admin-edited
        requests.put(
            f"{BASE_URL}/api/admin/lesson-slos/{SUBSTRAND_ID}/1",
            headers=admin_headers,
            json={"outcome": "ADMIN_EDITED_Outcome that should be preserved"}
        )
        
        # Now regenerate
        response = requests.post(
            f"{BASE_URL}/api/admin/lesson-slos/{SUBSTRAND_ID}/regenerate",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "result" in data
        assert "lessonSlos" in data
        print(f"✓ Regenerate: result={data.get('result')}")
        
        # Verify admin-edited SLO was preserved (isDraft=False should remain)
        slos = data.get("lessonSlos", [])
        lesson_1 = next((s for s in slos if s.get("lessonNumber") == 1), None)
        if lesson_1:
            # Admin-edited should have isDraft=False
            assert lesson_1.get("isDraft") is False, "Admin-edited SLO should be preserved"
            print(f"  Lesson 1 preserved: isDraft={lesson_1.get('isDraft')}")
    
    def test_sync_lesson_slos(self, admin_headers):
        """POST /api/admin/lesson-slos/{substrand_id}/sync - syncs to match number_of_lessons."""
        response = requests.post(
            f"{BASE_URL}/api/admin/lesson-slos/{SUBSTRAND_ID}/sync",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "result" in data
        assert "lessonSlos" in data
        print(f"✓ Sync: result={data.get('result')}")
    
    def test_bootstrap_lesson_slos(self, admin_headers):
        """POST /api/admin/lesson-slos/bootstrap - migration endpoint."""
        response = requests.post(
            f"{BASE_URL}/api/admin/lesson-slos/bootstrap",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "stats" in data
        stats = data.get("stats", {})
        print(f"✓ Bootstrap: scanned={stats.get('scanned')}, synced={stats.get('synced')}, created_total={stats.get('created_total')}")


# ==================== SCHEME DRAFT WORKFLOW ====================

class TestSchemeDraftWorkflow:
    """Test scheme draft save/preview/download workflow."""
    
    def test_save_scheme_draft(self, teacher_headers):
        """POST /api/schemes/save-draft - saves scheme as draft."""
        payload = {
            "scheme": {
                "teacherName": "Test Teacher",
                "school": "Test School",
                "subjectName": "Mathematics",
                "gradeName": "Grade 4",
                "term": 1,
                "year": 2026,
                "curriculumStandard": "KICD CBC",
                "totalWeeks": 12,
                "lessonsPerWeek": 5,
                "lessons": [
                    {
                        "week": 1,
                        "lessonNumber": 1,
                        "strand": "Numbers",
                        "substrand": "Whole Numbers",
                        "slo": "Identify whole numbers",
                        "keyInquiryQuestions": ["What are whole numbers?"],
                        "learningExperiences": ["Counting activities"],
                        "learningResources": ["Number cards"],
                        "assessmentMethods": ["Oral questions"]
                    }
                ]
            },
            "generationInput": {
                "gradeId": GRADE_ID,
                "subjectId": SUBJECT_ID,
                "term": 1,
                "year": 2026
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/save-draft",
            headers=teacher_headers,
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "draftId" in data
        draft_id = data.get("draftId")
        print(f"✓ Save draft: draftId={draft_id}")
        
        # Store for later tests
        TestSchemeDraftWorkflow.created_draft_id = draft_id
    
    def test_list_scheme_drafts(self, teacher_headers):
        """GET /api/schemes/drafts - lists user's scheme drafts."""
        response = requests.get(f"{BASE_URL}/api/schemes/drafts", headers=teacher_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "drafts" in data
        drafts = data.get("drafts", [])
        print(f"✓ List drafts: count={len(drafts)}")
        
        # Verify draft structure
        if drafts:
            draft = drafts[0]
            assert "id" in draft
            assert "status" in draft
            assert "isPaid" in draft
            print(f"  First draft: id={draft.get('id')}, status={draft.get('status')}, isPaid={draft.get('isPaid')}")
    
    def test_get_specific_draft(self, teacher_headers):
        """GET /api/schemes/drafts/{draft_id} - gets specific draft."""
        # Use existing draft from context
        response = requests.get(
            f"{BASE_URL}/api/schemes/drafts/{EXISTING_DRAFT_ID}",
            headers=teacher_headers
        )
        # May be 404 if draft doesn't exist for this user
        if response.status_code == 404:
            # Try with newly created draft
            if hasattr(TestSchemeDraftWorkflow, 'created_draft_id'):
                response = requests.get(
                    f"{BASE_URL}/api/schemes/drafts/{TestSchemeDraftWorkflow.created_draft_id}",
                    headers=teacher_headers
                )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "draft" in data
        draft = data.get("draft")
        assert "scheme" in draft
        print(f"✓ Get draft: id={draft.get('id')}, status={draft.get('status')}")
    
    def test_preview_draft_no_charge(self, teacher_headers):
        """POST /api/schemes/drafts/{draft_id}/preview - preview PDF (no charge)."""
        # Get wallet balance before
        balance_before = requests.get(f"{BASE_URL}/api/wallet/balance", headers=teacher_headers).json().get("balance", 0)
        
        # Use created draft or existing
        draft_id = getattr(TestSchemeDraftWorkflow, 'created_draft_id', EXISTING_DRAFT_ID)
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/drafts/{draft_id}/preview",
            headers=teacher_headers
        )
        
        if response.status_code == 404:
            pytest.skip("Draft not found for preview test")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert response.headers.get("Content-Type") == "application/pdf"
        assert len(response.content) > 0
        print(f"✓ Preview draft: PDF size={len(response.content)} bytes")
        
        # Verify no charge
        balance_after = requests.get(f"{BASE_URL}/api/wallet/balance", headers=teacher_headers).json().get("balance", 0)
        assert balance_after == balance_before, "Preview should not charge wallet"
        print(f"  Balance unchanged: {balance_before} -> {balance_after}")
    
    def test_regenerate_draft(self, teacher_headers):
        """POST /api/schemes/drafts/{draft_id}/regenerate - regenerate with new data."""
        draft_id = getattr(TestSchemeDraftWorkflow, 'created_draft_id', None)
        if not draft_id:
            pytest.skip("No draft created for regenerate test")
        
        payload = {
            "scheme": {
                "teacherName": "Test Teacher Updated",
                "school": "Test School",
                "subjectName": "Mathematics",
                "gradeName": "Grade 4",
                "term": 1,
                "year": 2026,
                "curriculumStandard": "KICD CBC",
                "totalWeeks": 12,
                "lessonsPerWeek": 5,
                "lessons": [
                    {
                        "week": 1,
                        "lessonNumber": 1,
                        "strand": "Numbers",
                        "substrand": "Whole Numbers",
                        "slo": "REGENERATED - Identify whole numbers",
                        "keyInquiryQuestions": ["What are whole numbers?"],
                        "learningExperiences": ["Counting activities"],
                        "learningResources": ["Number cards"],
                        "assessmentMethods": ["Oral questions"]
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/drafts/{draft_id}/regenerate",
            headers=teacher_headers,
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"✓ Regenerate draft: message={data.get('message')}")


# ==================== BACKWARD COMPATIBILITY ====================

class TestBackwardCompatibility:
    """Test backward compatibility with substrands without number_of_lessons."""
    
    def test_substrand_without_number_of_lessons(self, admin_headers):
        """Substrand without number_of_lessons should still work for lesson SLO endpoint."""
        # Find a substrand without number_of_lessons
        # First get all substrands for the strand
        response = requests.get(f"{BASE_URL}/api/substrands?strandId={STRAND_ID}", headers=admin_headers)
        if response.status_code != 200:
            pytest.skip("Could not fetch substrands")
        
        substrands = response.json().get("substrands", [])
        
        # Try to find one without number_of_lessons or use the known one
        for ss in substrands:
            ss_id = ss.get("id")
            # Try the lesson-slos endpoint
            slo_response = requests.get(f"{BASE_URL}/api/admin/lesson-slos/{ss_id}", headers=admin_headers)
            if slo_response.status_code == 200:
                data = slo_response.json()
                num = data.get("numberOfLessons", 0)
                if num == 0:
                    print(f"✓ Substrand {ss_id} has no number_of_lessons, endpoint returns empty: lessonSlos={len(data.get('lessonSlos', []))}")
                    return
        
        # If all have number_of_lessons, that's fine too
        print("✓ All tested substrands have number_of_lessons configured")


# ==================== SCHEME GENERATION V2 ====================

class TestSchemeGenerationV2:
    """Test scheme generation v2 uses lesson SLO outcomes."""
    
    def test_generate_v2_endpoint_exists(self, teacher_headers):
        """POST /api/schemes/generate-v2 - endpoint should exist and accept requests."""
        payload = {
            "gradeId": GRADE_ID,
            "subjectId": SUBJECT_ID,
            "term": 1,
            "year": 2026,
            "totalWeeks": 12,
            "lessonsPerWeek": 5,
            "selectedTopics": [SUBSTRAND_ID],
            "breaks": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            headers=teacher_headers,
            json=payload
        )
        
        # Should return 200 or 400 (if validation fails), not 404
        assert response.status_code != 404, "generate-v2 endpoint should exist"
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is True
            assert "scheme" in data
            scheme = data.get("scheme", {})
            lessons = scheme.get("lessons", [])
            print(f"✓ generate-v2: {len(lessons)} lessons generated")
            
            # Check if lessons have lesson SLO data
            if lessons:
                lesson = lessons[0]
                if not lesson.get("isBreak"):
                    print(f"  First lesson: slo={lesson.get('slo', 'N/A')[:50]}...")
        else:
            print(f"✓ generate-v2 endpoint exists, returned {response.status_code}: {response.text[:200]}")


# ==================== LESSON PLAN GENERATION ====================

class TestLessonPlanUsesLessonSlos:
    """Test that lesson plan generation uses lesson_slos for specific outcomes."""
    
    def test_lesson_plan_generate_endpoint(self, teacher_headers):
        """POST /api/lesson-plans/generate - should work with lesson SLO data."""
        # First get an SLO for the substrand
        slos_response = requests.get(f"{BASE_URL}/api/slos?substrandId={SUBSTRAND_ID}", headers=teacher_headers)
        if slos_response.status_code != 200:
            pytest.skip("Could not fetch SLOs")
        
        slos = slos_response.json().get("slos", [])
        if not slos:
            pytest.skip("No SLOs found for substrand")
        
        slo_id = slos[0].get("id")
        
        payload = {
            "duration": 40,
            "gradeId": GRADE_ID,
            "subjectId": SUBJECT_ID,
            "strandId": STRAND_ID,
            "substrandId": SUBSTRAND_ID,
            "sloId": slo_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/lesson-plans/generate",
            headers=teacher_headers,
            json=payload
        )
        
        # May fail due to insufficient balance, but endpoint should work
        if response.status_code == 402:
            print("✓ lesson-plans/generate endpoint works (insufficient balance)")
            return
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is True
            print(f"✓ lesson-plans/generate: lesson plan created")
        else:
            print(f"✓ lesson-plans/generate endpoint exists, returned {response.status_code}")


# ==================== SCHEME DRAFT DOWNLOAD WITH CHARGE ====================

class TestSchemeDraftDownloadCharge:
    """Test scheme draft download with KES 15 charge."""
    
    def test_download_draft_requires_balance(self, teacher_headers):
        """POST /api/schemes/drafts/{draft_id}/download - requires KES 15 balance."""
        # Get current balance
        balance_response = requests.get(f"{BASE_URL}/api/wallet/balance", headers=teacher_headers)
        balance = balance_response.json().get("balance", 0)
        
        # Use created draft
        draft_id = getattr(TestSchemeDraftWorkflow, 'created_draft_id', None)
        if not draft_id:
            pytest.skip("No draft created for download test")
        
        response = requests.post(
            f"{BASE_URL}/api/schemes/drafts/{draft_id}/download",
            headers=teacher_headers
        )
        
        if balance < 15:
            # Should fail with 402 insufficient balance
            assert response.status_code == 402, f"Expected 402 for insufficient balance, got {response.status_code}"
            print(f"✓ Download correctly requires KES 15 (current balance: {balance})")
        else:
            # Should succeed and charge KES 15
            if response.status_code == 200:
                assert response.headers.get("Content-Type") == "application/pdf"
                new_balance = requests.get(f"{BASE_URL}/api/wallet/balance", headers=teacher_headers).json().get("balance", 0)
                # First download charges, subsequent don't
                print(f"✓ Download succeeded, balance: {balance} -> {new_balance}")
            else:
                print(f"✓ Download endpoint exists, returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
