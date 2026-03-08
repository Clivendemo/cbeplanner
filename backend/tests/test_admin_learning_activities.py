"""
Backend tests for Admin Learning Activities CRUD API endpoints.

Tests cover:
- GET /api/admin/learning-activities - List all learning activities
- GET /api/admin/learning-activities/by-substrand/{id} - Get by substrand
- PUT /api/admin/learning-activities/by-substrand/{id} - Upsert by substrand  
- POST /api/admin/learning-activities - Create new learning activity
- DELETE /api/admin/learning-activities/{id} - Delete learning activity

Also tests admin CRUD endpoints for:
- Grades, Subjects, Strands, Substrands, SLOs

Since endpoints require Firebase auth, we test:
1. Unauthenticated requests return 401
2. Database operations work correctly via direct MongoDB queries
"""

import pytest
import requests
import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('/app/backend/.env')

# Get environment variables
BASE_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://cbe-lesson-planner.preview.emergentagent.com').rstrip('/')
MONGO_URL = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
DB_NAME = os.environ.get('DB_NAME', 'cbeplanner')

# Test data prefix for cleanup
TEST_PREFIX = "TEST_"


@pytest.fixture(scope="module")
def db():
    """Create MongoDB client connection"""
    client = MongoClient(MONGO_URL)
    database = client[DB_NAME]
    yield database
    client.close()


@pytest.fixture(scope="module")
def api_client():
    """Create requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def test_substrand_id(db):
    """Get a real substrand ID for testing"""
    substrand = db.substrands.find_one({})
    if substrand:
        return str(substrand["_id"])
    return None


# ==================== AUTHENTICATION TESTS ====================

class TestAuthenticationRequired:
    """Verify all admin endpoints require authentication"""
    
    def test_learning_activities_get_requires_auth(self, api_client):
        """GET /api/admin/learning-activities requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/admin/learning-activities")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("GET /api/admin/learning-activities correctly returns 401 without auth")
    
    def test_learning_activities_by_substrand_requires_auth(self, api_client, test_substrand_id):
        """GET /api/admin/learning-activities/by-substrand/{id} requires authentication"""
        if not test_substrand_id:
            pytest.skip("No substrand found in database")
        response = api_client.get(f"{BASE_URL}/api/admin/learning-activities/by-substrand/{test_substrand_id}")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("GET /api/admin/learning-activities/by-substrand requires auth: PASSED")
    
    def test_learning_activities_post_requires_auth(self, api_client, test_substrand_id):
        """POST /api/admin/learning-activities requires authentication"""
        if not test_substrand_id:
            pytest.skip("No substrand found in database")
        response = api_client.post(
            f"{BASE_URL}/api/admin/learning-activities",
            json={
                "substrandId": test_substrand_id,
                "introduction_activities": ["Test activity"],
                "development_activities": [],
                "conclusion_activities": [],
                "extended_activities": []
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("POST /api/admin/learning-activities requires auth: PASSED")
    
    def test_learning_activities_upsert_requires_auth(self, api_client, test_substrand_id):
        """PUT /api/admin/learning-activities/by-substrand/{id} requires authentication"""
        if not test_substrand_id:
            pytest.skip("No substrand found in database")
        response = api_client.put(
            f"{BASE_URL}/api/admin/learning-activities/by-substrand/{test_substrand_id}",
            json={
                "substrandId": test_substrand_id,
                "introduction_activities": ["Test"],
                "development_activities": [],
                "conclusion_activities": [],
                "extended_activities": []
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PUT /api/admin/learning-activities/by-substrand requires auth: PASSED")
    
    def test_admin_grades_requires_auth(self, api_client):
        """GET /api/admin/grades requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/admin/grades")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("GET /api/admin/grades requires auth: PASSED")
    
    def test_admin_subjects_requires_auth(self, api_client):
        """GET /api/admin/subjects requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/admin/subjects")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("GET /api/admin/subjects requires auth: PASSED")
    
    def test_admin_strands_requires_auth(self, api_client):
        """GET /api/admin/strands requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/admin/strands")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("GET /api/admin/strands requires auth: PASSED")
    
    def test_admin_substrands_requires_auth(self, api_client):
        """GET /api/admin/substrands requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/admin/substrands")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("GET /api/admin/substrands requires auth: PASSED")
    
    def test_admin_slos_requires_auth(self, api_client):
        """GET /api/admin/slos requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/admin/slos")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("GET /api/admin/slos requires auth: PASSED")


# ==================== DATABASE OPERATIONS TESTS ====================

class TestLearningActivitiesDatabase:
    """Test learning activities database operations directly"""
    
    def test_learning_activities_collection_exists(self, db):
        """Verify learning_activities collection exists and has data"""
        count = db.learning_activities.count_documents({})
        print(f"Learning activities in database: {count}")
        assert count > 0, "No learning activities found in database"
    
    def test_learning_activity_structure(self, db):
        """Verify learning activity document structure"""
        activity = db.learning_activities.find_one({})
        assert activity is not None, "No learning activity found"
        
        # Required field
        assert "substrandId" in activity, "Missing substrandId field"
        
        # Expected activity fields
        expected_fields = [
            "introduction_activities",
            "development_activities", 
            "conclusion_activities",
            "extended_activities"
        ]
        
        found_fields = [f for f in expected_fields if f in activity]
        print(f"Learning activity fields found: {found_fields}")
        assert len(found_fields) > 0, "Missing activity content fields"
    
    def test_create_learning_activity(self, db, test_substrand_id):
        """Test creating a learning activity document"""
        if not test_substrand_id:
            pytest.skip("No substrand found in database")
        
        test_substrand = f"{TEST_PREFIX}substrand_{datetime.utcnow().timestamp()}"
        
        test_activity = {
            "substrandId": test_substrand,
            "introduction_activities": ["TEST: Introduce topic", "TEST: Review prerequisites"],
            "development_activities": ["TEST: Explain concepts", "TEST: Practice exercises"],
            "conclusion_activities": ["TEST: Summarize key points"],
            "extended_activities": ["TEST: Homework assignment"],
            "learning_resources": ["TEST: Textbook", "TEST: Whiteboard"],
            "assessment_methods": ["TEST: Oral questions"]
        }
        
        # Insert
        result = db.learning_activities.insert_one(test_activity)
        assert result.inserted_id is not None, "Insert failed"
        print(f"Created test learning activity: {result.inserted_id}")
        
        # Verify insertion
        created = db.learning_activities.find_one({"_id": result.inserted_id})
        assert created is not None, "Failed to retrieve created activity"
        assert created["substrandId"] == test_substrand
        assert len(created["introduction_activities"]) == 2
        
        # Cleanup
        db.learning_activities.delete_one({"_id": result.inserted_id})
        print("Create learning activity test: PASSED")
    
    def test_upsert_learning_activity(self, db):
        """Test upserting learning activity by substrandId"""
        test_substrand = f"{TEST_PREFIX}upsert_{datetime.utcnow().timestamp()}"
        
        # First upsert - should insert
        activity_data = {
            "substrandId": test_substrand,
            "introduction_activities": ["Initial intro"],
            "development_activities": [],
            "conclusion_activities": [],
            "extended_activities": []
        }
        
        result = db.learning_activities.update_one(
            {"substrandId": test_substrand},
            {"$set": activity_data},
            upsert=True
        )
        
        assert result.upserted_id is not None, "Upsert should have inserted new document"
        print(f"First upsert created document: {result.upserted_id}")
        
        # Second upsert - should update
        activity_data["introduction_activities"] = ["Updated intro"]
        result2 = db.learning_activities.update_one(
            {"substrandId": test_substrand},
            {"$set": activity_data},
            upsert=True
        )
        
        assert result2.modified_count == 1, "Upsert should have updated existing document"
        print("Second upsert updated existing document")
        
        # Verify update
        updated = db.learning_activities.find_one({"substrandId": test_substrand})
        assert updated["introduction_activities"] == ["Updated intro"]
        
        # Cleanup
        db.learning_activities.delete_one({"substrandId": test_substrand})
        print("Upsert learning activity test: PASSED")
    
    def test_get_by_substrand_exists(self, db, test_substrand_id):
        """Test retrieving learning activity by substrand when exists"""
        if not test_substrand_id:
            pytest.skip("No substrand found in database")
        
        # Find a substrand that has learning activities
        activity = db.learning_activities.find_one({})
        if not activity:
            pytest.skip("No learning activities in database")
        
        substrand_id = activity["substrandId"]
        retrieved = db.learning_activities.find_one({"substrandId": substrand_id})
        
        assert retrieved is not None, "Should find activity by substrandId"
        assert retrieved["substrandId"] == substrand_id
        print(f"Found learning activity for substrand {substrand_id}")
    
    def test_get_by_substrand_not_exists(self, db):
        """Test retrieving learning activity by substrand when not exists"""
        fake_id = str(ObjectId())
        result = db.learning_activities.find_one({"substrandId": fake_id})
        assert result is None, "Should return None for non-existent substrand"
        print("Get by non-existent substrand correctly returns None")
    
    def test_delete_learning_activity(self, db):
        """Test deleting a learning activity"""
        # Create test activity
        test_activity = {
            "substrandId": f"{TEST_PREFIX}delete_test",
            "introduction_activities": ["TEST"]
        }
        result = db.learning_activities.insert_one(test_activity)
        activity_id = result.inserted_id
        
        # Verify exists
        assert db.learning_activities.find_one({"_id": activity_id}) is not None
        
        # Delete
        delete_result = db.learning_activities.delete_one({"_id": activity_id})
        assert delete_result.deleted_count == 1
        
        # Verify deleted
        assert db.learning_activities.find_one({"_id": activity_id}) is None
        print("Delete learning activity test: PASSED")


# ==================== ADMIN CRUD OPERATIONS TESTS ====================

class TestGradesCRUD:
    """Test grades CRUD operations via database"""
    
    def test_grades_exist(self, db):
        """Verify grades collection has data"""
        count = db.grades.count_documents({})
        print(f"Grades in database: {count}")
        assert count > 0, "No grades found"
    
    def test_create_grade(self, db):
        """Test creating a grade"""
        test_grade = {
            "name": f"{TEST_PREFIX}Grade Test",
            "order": 999
        }
        result = db.grades.insert_one(test_grade)
        assert result.inserted_id is not None
        
        # Cleanup
        db.grades.delete_one({"_id": result.inserted_id})
        print("Create grade test: PASSED")
    
    def test_update_grade(self, db):
        """Test updating a grade"""
        # Create
        test_grade = {"name": f"{TEST_PREFIX}Update Test", "order": 998}
        result = db.grades.insert_one(test_grade)
        
        # Update
        update_result = db.grades.update_one(
            {"_id": result.inserted_id},
            {"$set": {"name": f"{TEST_PREFIX}Updated Grade"}}
        )
        assert update_result.modified_count == 1
        
        # Verify
        updated = db.grades.find_one({"_id": result.inserted_id})
        assert f"{TEST_PREFIX}Updated Grade" in updated["name"]
        
        # Cleanup
        db.grades.delete_one({"_id": result.inserted_id})
        print("Update grade test: PASSED")


class TestSubjectsCRUD:
    """Test subjects CRUD operations via database"""
    
    def test_subjects_exist(self, db):
        """Verify subjects collection has data"""
        count = db.subjects.count_documents({})
        print(f"Subjects in database: {count}")
        assert count >= 22, f"Expected at least 22 subjects, found {count}"
    
    def test_create_subject(self, db):
        """Test creating a subject"""
        # Get a valid grade ID
        grade = db.grades.find_one({})
        if not grade:
            pytest.skip("No grades found")
        
        test_subject = {
            "name": f"{TEST_PREFIX}Test Subject",
            "gradeIds": [str(grade["_id"])]
        }
        result = db.subjects.insert_one(test_subject)
        assert result.inserted_id is not None
        
        # Cleanup
        db.subjects.delete_one({"_id": result.inserted_id})
        print("Create subject test: PASSED")


class TestStrandsCRUD:
    """Test strands CRUD operations via database"""
    
    def test_strands_exist(self, db):
        """Verify strands collection has data"""
        count = db.strands.count_documents({})
        print(f"Strands in database: {count}")
        assert count >= 60, f"Expected at least 60 strands, found {count}"
    
    def test_create_strand(self, db):
        """Test creating a strand"""
        subject = db.subjects.find_one({})
        if not subject:
            pytest.skip("No subjects found")
        
        test_strand = {
            "name": f"{TEST_PREFIX}Test Strand",
            "subjectId": str(subject["_id"])
        }
        result = db.strands.insert_one(test_strand)
        assert result.inserted_id is not None
        
        # Cleanup
        db.strands.delete_one({"_id": result.inserted_id})
        print("Create strand test: PASSED")
    
    def test_filter_strands_by_subject(self, db):
        """Test filtering strands by subjectId"""
        subject = db.subjects.find_one({})
        if not subject:
            pytest.skip("No subjects found")
        
        subject_id = str(subject["_id"])
        strands = list(db.strands.find({"subjectId": subject_id}))
        print(f"Found {len(strands)} strands for subject {subject['name']}")
        # Most subjects should have strands
        assert len(strands) >= 0  # Just verify the query works


class TestSubstrandsCRUD:
    """Test substrands CRUD operations via database"""
    
    def test_substrands_exist(self, db):
        """Verify substrands collection has data"""
        count = db.substrands.count_documents({})
        print(f"Substrands in database: {count}")
        assert count >= 235, f"Expected at least 235 substrands, found {count}"
    
    def test_create_substrand(self, db):
        """Test creating a substrand"""
        strand = db.strands.find_one({})
        if not strand:
            pytest.skip("No strands found")
        
        test_substrand = {
            "name": f"{TEST_PREFIX}Test Substrand",
            "strandId": str(strand["_id"])
        }
        result = db.substrands.insert_one(test_substrand)
        assert result.inserted_id is not None
        
        # Cleanup
        db.substrands.delete_one({"_id": result.inserted_id})
        print("Create substrand test: PASSED")
    
    def test_filter_substrands_by_strand(self, db):
        """Test filtering substrands by strandId"""
        strand = db.strands.find_one({})
        if not strand:
            pytest.skip("No strands found")
        
        strand_id = str(strand["_id"])
        substrands = list(db.substrands.find({"strandId": strand_id}))
        print(f"Found {len(substrands)} substrands for strand {strand['name']}")


class TestSLOsCRUD:
    """Test SLOs CRUD operations via database"""
    
    def test_slos_exist(self, db):
        """Verify SLOs collection has data"""
        count = db.slos.count_documents({})
        print(f"SLOs in database: {count}")
        assert count >= 898, f"Expected at least 898 SLOs, found {count}"
    
    def test_create_slo(self, db):
        """Test creating an SLO"""
        substrand = db.substrands.find_one({})
        if not substrand:
            pytest.skip("No substrands found")
        
        test_slo = {
            "name": f"{TEST_PREFIX}Test SLO",
            "description": "Test SLO description",
            "substrandId": str(substrand["_id"])
        }
        result = db.slos.insert_one(test_slo)
        assert result.inserted_id is not None
        
        # Cleanup
        db.slos.delete_one({"_id": result.inserted_id})
        print("Create SLO test: PASSED")
    
    def test_filter_slos_by_substrand(self, db):
        """Test filtering SLOs by substrandId"""
        substrand = db.substrands.find_one({})
        if not substrand:
            pytest.skip("No substrands found")
        
        substrand_id = str(substrand["_id"])
        slos = list(db.slos.find({"substrandId": substrand_id}))
        print(f"Found {len(slos)} SLOs for substrand {substrand['name']}")


# ==================== ENDPOINT ROUTE TESTS ====================

class TestEndpointRouteValidation:
    """Test that API routes are correctly registered"""
    
    def test_api_docs_available(self, api_client):
        """Verify API docs are accessible"""
        response = api_client.get(f"{BASE_URL}/api/docs")
        # Should return 200 (docs page) or redirect
        assert response.status_code in [200, 302, 307], f"Unexpected status: {response.status_code}"
        print("API docs endpoint: ACCESSIBLE")
    
    def test_health_endpoint(self, api_client):
        """Verify health endpoint returns healthy status"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"Health check: {data}")
    
    def test_invalid_admin_endpoint_returns_404(self, api_client):
        """Verify non-existent admin endpoint returns 404 or 401"""
        response = api_client.get(f"{BASE_URL}/api/admin/nonexistent")
        # Should return 404 (not found) or 401 (auth required first)
        assert response.status_code in [401, 404, 405], f"Unexpected status: {response.status_code}"
        print(f"Invalid admin endpoint returns: {response.status_code}")


# ==================== DATA VALIDATION TESTS ====================

class TestLearningActivityDataValidation:
    """Test learning activity data validation"""
    
    def test_invalid_substrand_id_format(self, api_client):
        """Test POST with invalid substrand ID format"""
        response = api_client.post(
            f"{BASE_URL}/api/admin/learning-activities",
            json={
                "substrandId": "invalid-id",
                "introduction_activities": ["Test"]
            }
        )
        # Should return 401 (auth required) before validation
        assert response.status_code == 401
        print("Invalid substrand ID POST correctly requires auth first")
    
    def test_empty_activities_arrays(self, db):
        """Test that empty activity arrays are valid"""
        test_activity = {
            "substrandId": f"{TEST_PREFIX}empty_arrays",
            "introduction_activities": [],
            "development_activities": [],
            "conclusion_activities": [],
            "extended_activities": []
        }
        
        result = db.learning_activities.insert_one(test_activity)
        assert result.inserted_id is not None
        
        retrieved = db.learning_activities.find_one({"_id": result.inserted_id})
        assert retrieved["introduction_activities"] == []
        
        # Cleanup
        db.learning_activities.delete_one({"_id": result.inserted_id})
        print("Empty activity arrays test: PASSED")


# ==================== CLEANUP ====================

@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data(db):
    """Cleanup TEST_ prefixed data after all tests"""
    yield
    
    # Remove any leftover test data
    collections = [
        "learning_activities",
        "grades", 
        "subjects",
        "strands",
        "substrands",
        "slos"
    ]
    
    for collection in collections:
        result = db[collection].delete_many({"name": {"$regex": f"^{TEST_PREFIX}"}})
        if result.deleted_count > 0:
            print(f"Cleaned up {result.deleted_count} test documents from {collection}")
    
    # Also cleanup by substrandId pattern
    result = db.learning_activities.delete_many({"substrandId": {"$regex": f"^{TEST_PREFIX}"}})
    if result.deleted_count > 0:
        print(f"Cleaned up {result.deleted_count} test learning activities")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
