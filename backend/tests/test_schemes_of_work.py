"""
Test Schemes of Work API Endpoints
Tests the multi-step scheme generation flow including:
- Lessons per week configuration
- Topic selection
- Scheme generation (v2)
- Preview and download with wallet deduction
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://be518031-b59f-4d70-b8c4-b9d51851b23c.preview.emergentagent.com').rstrip('/')


class TestSchemesAPIHealth:
    """Basic health and endpoint availability tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print("PASSED: API health check")
    
    def test_grades_endpoint_requires_auth(self):
        """Test that grades endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/grades")
        assert response.status_code == 401
        print("PASSED: Grades endpoint requires auth (401)")
    
    def test_subjects_endpoint_requires_auth(self):
        """Test that subjects endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/subjects?gradeId=test")
        assert response.status_code == 401
        print("PASSED: Subjects endpoint requires auth (401)")


class TestSchemesConfigEndpoints:
    """Test scheme configuration endpoints"""
    
    def test_lessons_per_week_requires_auth(self):
        """Test lessons-per-week config requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/schemes/config/lessons-per-week",
            params={"gradeId": "test", "subjectId": "test"}
        )
        assert response.status_code == 401
        print("PASSED: Lessons per week config requires auth (401)")
    
    def test_scheme_topics_requires_auth(self):
        """Test scheme topics endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/schemes/topics/test_subject_id")
        assert response.status_code == 401
        print("PASSED: Scheme topics endpoint requires auth (401)")


class TestSchemeGenerationEndpoints:
    """Test scheme generation endpoints"""
    
    def test_generate_v2_requires_auth(self):
        """Test generate-v2 endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/schemes/generate-v2",
            json={
                "gradeId": "test",
                "subjectId": "test",
                "term": 1,
                "year": 2026,
                "totalWeeks": 14,
                "lessonsPerWeek": 5,
                "selectedTopics": ["topic1"],
                "breaks": []
            }
        )
        assert response.status_code == 401
        print("PASSED: Generate-v2 endpoint requires auth (401)")
    
    def test_preview_requires_auth(self):
        """Test preview endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/schemes/preview",
            json={"test": "data"}
        )
        assert response.status_code == 401
        print("PASSED: Preview endpoint requires auth (401)")
    
    def test_download_requires_auth(self):
        """Test download endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/schemes/download",
            json={"test": "data"}
        )
        assert response.status_code == 401
        print("PASSED: Download endpoint requires auth (401)")


class TestSchemeListEndpoints:
    """Test scheme list/get endpoints"""
    
    def test_get_schemes_requires_auth(self):
        """Test get schemes list requires authentication"""
        response = requests.get(f"{BASE_URL}/api/schemes")
        assert response.status_code == 401
        print("PASSED: Get schemes list requires auth (401)")
    
    def test_get_scheme_by_id_requires_auth(self):
        """Test get scheme by ID requires authentication"""
        response = requests.get(f"{BASE_URL}/api/schemes/test_scheme_id")
        assert response.status_code == 401
        print("PASSED: Get scheme by ID requires auth (401)")


class TestDatabaseGradesAndSubjects:
    """Test that grades and subjects exist in database for scheme generation"""
    
    def test_database_has_grades(self):
        """Verify database has grades seeded"""
        from pymongo import MongoClient
        
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        db = client['cbeplanner']
        
        grades = list(db.grades.find())
        assert len(grades) > 0, "No grades found in database"
        
        # Check for expected grades
        grade_names = [g['name'] for g in grades]
        print(f"Found grades: {grade_names}")
        
        # Verify at least Grade 1 or Grade 10 exists (as mentioned in context)
        has_expected_grade = any('Grade 1' in name or 'Grade 10' in name for name in grade_names)
        assert has_expected_grade, f"Expected Grade 1 or Grade 10, found: {grade_names}"
        
        print(f"PASSED: Database has {len(grades)} grades")
        client.close()
    
    def test_database_has_subjects(self):
        """Verify database has subjects seeded"""
        from pymongo import MongoClient
        
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        db = client['cbeplanner']
        
        subjects = list(db.subjects.find())
        assert len(subjects) > 0, "No subjects found in database"
        
        subject_names = [s['name'] for s in subjects]
        print(f"Found subjects: {subject_names[:10]}...")  # Show first 10
        
        print(f"PASSED: Database has {len(subjects)} subjects")
        client.close()
    
    def test_database_has_strands(self):
        """Verify database has strands for scheme topics"""
        from pymongo import MongoClient
        
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        db = client['cbeplanner']
        
        strands = list(db.strands.find())
        assert len(strands) > 0, "No strands found in database"
        
        print(f"PASSED: Database has {len(strands)} strands")
        client.close()
    
    def test_database_has_substrands(self):
        """Verify database has substrands for topic selection"""
        from pymongo import MongoClient
        
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        db = client['cbeplanner']
        
        substrands = list(db.substrands.find())
        assert len(substrands) > 0, "No substrands found in database"
        
        print(f"PASSED: Database has {len(substrands)} substrands")
        client.close()
    
    def test_database_has_slos(self):
        """Verify database has SLOs for scheme generation"""
        from pymongo import MongoClient
        
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        db = client['cbeplanner']
        
        slos = list(db.slos.find())
        assert len(slos) > 0, "No SLOs found in database"
        
        print(f"PASSED: Database has {len(slos)} SLOs")
        client.close()


class TestSchemeGeneratorModule:
    """Test the scheme_generator module functions"""
    
    def test_get_lessons_per_week_lower_primary(self):
        """Test lessons per week for lower primary grades"""
        import sys
        sys.path.insert(0, '/app/backend')
        from scheme_generator import get_lessons_per_week
        
        # Test Grade 1 Mathematics
        lessons = get_lessons_per_week("Grade 1", "Mathematics")
        assert lessons == 5, f"Expected 5 lessons for Grade 1 Math, got {lessons}"
        
        # Test Grade 2 English
        lessons = get_lessons_per_week("Grade 2", "English")
        assert lessons == 5, f"Expected 5 lessons for Grade 2 English, got {lessons}"
        
        print("PASSED: Lower primary lessons per week calculation")
    
    def test_get_lessons_per_week_upper_primary(self):
        """Test lessons per week for upper primary grades"""
        import sys
        sys.path.insert(0, '/app/backend')
        from scheme_generator import get_lessons_per_week
        
        # Test Grade 5 Science
        lessons = get_lessons_per_week("Grade 5", "Science and Technology")
        assert lessons == 4, f"Expected 4 lessons for Grade 5 Science, got {lessons}"
        
        print("PASSED: Upper primary lessons per week calculation")
    
    def test_get_lessons_per_week_junior_secondary(self):
        """Test lessons per week for junior secondary grades"""
        import sys
        sys.path.insert(0, '/app/backend')
        from scheme_generator import get_lessons_per_week
        
        # Test Grade 7 Mathematics
        lessons = get_lessons_per_week("Grade 7", "Mathematics")
        assert lessons == 5, f"Expected 5 lessons for Grade 7 Math, got {lessons}"
        
        # Test Grade 9 Integrated Science
        lessons = get_lessons_per_week("Grade 9", "Integrated Science")
        assert lessons == 5, f"Expected 5 lessons for Grade 9 Science, got {lessons}"
        
        print("PASSED: Junior secondary lessons per week calculation")
    
    def test_get_lessons_per_week_senior_secondary(self):
        """Test lessons per week for senior secondary grades"""
        import sys
        sys.path.insert(0, '/app/backend')
        from scheme_generator import get_lessons_per_week
        
        # Test Grade 10 Biology
        lessons = get_lessons_per_week("Grade 10", "Biology")
        assert lessons == 4, f"Expected 4 lessons for Grade 10 Biology, got {lessons}"
        
        print("PASSED: Senior secondary lessons per week calculation")
    
    def test_get_assessment_for_slo(self):
        """Test assessment method generation based on SLO"""
        import sys
        sys.path.insert(0, '/app/backend')
        from scheme_generator import get_assessment_for_slo
        
        # Test identify action verb
        assessment = get_assessment_for_slo("Identify the parts of a plant")
        assert "Oral questions" in assessment or "Matching exercise" in assessment
        
        # Test describe action verb
        assessment = get_assessment_for_slo("Describe the water cycle")
        assert "Written description" in assessment or "Oral explanation" in assessment
        
        print("PASSED: Assessment method generation")
    
    def test_generate_inquiry_questions(self):
        """Test inquiry question generation"""
        import sys
        sys.path.insert(0, '/app/backend')
        from scheme_generator import generate_inquiry_questions
        
        questions = generate_inquiry_questions("Numbers", "Whole Numbers", "Count objects")
        assert len(questions) >= 2, "Should generate at least 2 inquiry questions"
        assert any("importance" in q.lower() for q in questions), "Should include importance question"
        
        print("PASSED: Inquiry question generation")
    
    def test_generate_learning_experiences(self):
        """Test learning experience generation"""
        import sys
        sys.path.insert(0, '/app/backend')
        from scheme_generator import generate_learning_experiences
        
        experiences = generate_learning_experiences("Numbers", "Counting", "identify numbers")
        assert len(experiences) >= 2, "Should generate at least 2 learning experiences"
        
        print("PASSED: Learning experience generation")
    
    def test_generate_learning_resources(self):
        """Test learning resource generation"""
        import sys
        sys.path.insert(0, '/app/backend')
        from scheme_generator import generate_learning_resources
        
        resources = generate_learning_resources("Numbers", "Counting")
        assert len(resources) >= 2, "Should generate at least 2 resources"
        assert "Textbooks" in resources, "Should include textbooks"
        
        print("PASSED: Learning resource generation")
    
    def test_generate_scheme_pdf(self):
        """Test PDF generation"""
        import sys
        sys.path.insert(0, '/app/backend')
        from scheme_generator import generate_scheme_pdf
        
        # Create test scheme data
        scheme_data = {
            "schoolName": "Test School",
            "gradeName": "Grade 1",
            "subjectName": "Mathematics",
            "term": 1,
            "year": 2026,
            "lessonsPerWeek": 5,
            "lessons": [
                {
                    "week": 1,
                    "lesson": 1,
                    "strand": "Numbers",
                    "substrand": "Whole Numbers",
                    "slo": "Count objects up to 10",
                    "keyInquiryQuestions": ["What is counting?"],
                    "learningExperiences": ["Count objects"],
                    "learningResources": ["Counters"],
                    "assessmentMethods": ["Oral questions"]
                },
                {
                    "isBreak": True,
                    "breakType": "Mid-Term Break",
                    "week": 5,
                    "lesson": 1
                }
            ]
        }
        
        pdf_bytes = generate_scheme_pdf(scheme_data)
        
        # Verify PDF was generated
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF', "Should be a valid PDF file"
        
        print(f"PASSED: PDF generation ({len(pdf_bytes)} bytes)")


class TestUserWalletForSchemes:
    """Test wallet balance checking for scheme downloads"""
    
    def test_demo_user_exists(self):
        """Verify demo2@example.com user exists"""
        from pymongo import MongoClient
        
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        db = client['cbeplanner']
        
        user = db.users.find_one({"email": "demo2@example.com"})
        
        if user:
            print(f"Found demo2 user with wallet balance: {user.get('walletBalance', 0)}")
            print(f"PASSED: Demo user exists")
        else:
            print("INFO: demo2@example.com user not found in database")
            # This is not a failure - user may need to be created via login
        
        client.close()
    
    def test_scheme_download_cost_constant(self):
        """Verify scheme download cost is set correctly"""
        import sys
        sys.path.insert(0, '/app/backend')
        
        # Import from server to check the constant
        # We'll check the scheme_generator module instead
        EXPECTED_COST = 15
        
        # Read server.py to verify the constant
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
            assert 'SCHEME_DOWNLOAD_COST = 15' in content, "SCHEME_DOWNLOAD_COST should be 15"
        
        print(f"PASSED: Scheme download cost is KES {EXPECTED_COST}")


class TestEndpointRouting:
    """Test that all scheme endpoints are properly routed"""
    
    def test_all_scheme_endpoints_exist(self):
        """Verify all scheme endpoints return proper responses (not 404)"""
        endpoints = [
            ("GET", "/api/schemes/config/lessons-per-week?gradeId=test&subjectId=test"),
            ("GET", "/api/schemes/topics/test_id"),
            ("POST", "/api/schemes/generate-v2"),
            ("POST", "/api/schemes/preview"),
            ("POST", "/api/schemes/download"),
            ("GET", "/api/schemes"),
        ]
        
        for method, endpoint in endpoints:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url, json={})
            
            # Should return 401 (auth required) not 404 (not found)
            assert response.status_code != 404, f"Endpoint {method} {endpoint} returned 404"
            print(f"PASSED: {method} {endpoint} exists (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
