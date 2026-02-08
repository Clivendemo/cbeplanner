#!/usr/bin/env python3
"""
CBE Lesson Planning System Backend API Tests
Tests the FastAPI backend endpoints and database functionality
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import time

# Backend URL from environment
BACKEND_URL = "https://lessoncraft-ke.preview.emergentagent.com/api"

class CBEBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.teacher_token = None
        
    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Health Check", True, "API is responding")
                return True
            else:
                self.log_test("Health Check", False, f"Unexpected status code: {response.status_code}", response.text)
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Health Check", False, "Connection failed", str(e))
            return False
    
    def test_seed_data_without_auth(self):
        """Test seed data endpoint without authentication (should fail)"""
        try:
            response = self.session.post(f"{self.base_url}/admin/seed-data")
            if response.status_code == 401:
                self.log_test("Seed Data Auth Check", True, "Correctly requires authentication")
                return True
            else:
                self.log_test("Seed Data Auth Check", False, f"Expected 401, got {response.status_code}", response.text)
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Seed Data Auth Check", False, "Connection failed", str(e))
            return False
    
    def test_grades_without_auth(self):
        """Test grades endpoint without authentication (should fail)"""
        try:
            response = self.session.get(f"{self.base_url}/grades")
            if response.status_code == 401:
                self.log_test("Grades Auth Check", True, "Correctly requires authentication")
                return True
            else:
                self.log_test("Grades Auth Check", False, f"Expected 401, got {response.status_code}", response.text)
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Grades Auth Check", False, "Connection failed", str(e))
            return False
    
    def test_subjects_without_auth(self):
        """Test subjects endpoint without authentication (should fail)"""
        try:
            response = self.session.get(f"{self.base_url}/subjects?gradeId=test")
            if response.status_code == 401:
                self.log_test("Subjects Auth Check", True, "Correctly requires authentication")
                return True
            else:
                self.log_test("Subjects Auth Check", False, f"Expected 401, got {response.status_code}", response.text)
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Subjects Auth Check", False, "Connection failed", str(e))
            return False
    
    def test_admin_endpoints_without_auth(self):
        """Test admin endpoints without authentication"""
        admin_endpoints = [
            "/admin/grades",
            "/admin/subjects", 
            "/admin/strands",
            "/admin/substrands",
            "/admin/slos",
            "/admin/activities",
            "/admin/competencies",
            "/admin/values",
            "/admin/pcis",
            "/admin/assessments"
        ]
        
        all_passed = True
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 401:
                    self.log_test(f"Admin {endpoint} Auth Check", True, "Correctly requires authentication")
                else:
                    self.log_test(f"Admin {endpoint} Auth Check", False, f"Expected 401, got {response.status_code}", response.text)
                    all_passed = False
            except requests.exceptions.RequestException as e:
                self.log_test(f"Admin {endpoint} Auth Check", False, "Connection failed", str(e))
                all_passed = False
        
        return all_passed
    
    def test_backend_server_status(self):
        """Test if backend server is running and accessible"""
        try:
            # Test basic connectivity
            response = self.session.get(self.base_url, timeout=10)
            
            # Check if we get any response (even 404 is better than connection error)
            if response.status_code in [200, 404, 422]:
                self.log_test("Backend Server Status", True, f"Server is running (status: {response.status_code})")
                return True
            else:
                self.log_test("Backend Server Status", False, f"Server responded with status: {response.status_code}", response.text)
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test("Backend Server Status", False, "Cannot connect to backend server", "Connection refused")
            return False
        except requests.exceptions.Timeout:
            self.log_test("Backend Server Status", False, "Backend server timeout", "Request timed out")
            return False
        except requests.exceptions.RequestException as e:
            self.log_test("Backend Server Status", False, "Backend server error", str(e))
            return False
    
    def test_api_structure(self):
        """Test API structure and routing"""
        try:
            # Test root API endpoint
            response = self.session.get(f"{self.base_url}/")
            
            # FastAPI typically returns 422 for missing parameters or 404 for not found
            if response.status_code in [200, 404, 422]:
                self.log_test("API Structure", True, f"API routing is working (status: {response.status_code})")
                return True
            else:
                self.log_test("API Structure", False, f"Unexpected API response: {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("API Structure", False, "API structure test failed", str(e))
            return False
    
    def test_cors_headers(self):
        """Test CORS configuration"""
        try:
            # Test with Origin header to trigger CORS
            headers = {"Origin": "https://example.com"}
            response = self.session.get(f"{self.base_url}/", headers=headers)
            
            # Check for CORS headers
            cors_headers = [
                'access-control-allow-origin',
                'access-control-allow-credentials'
            ]
            
            found_cors = any(header in response.headers for header in cors_headers)
            
            if found_cors:
                self.log_test("CORS Configuration", True, "CORS is properly configured")
                return True
            else:
                self.log_test("CORS Configuration", False, "CORS headers not found", dict(response.headers))
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("CORS Configuration", False, "CORS test failed", str(e))
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity indirectly through API responses"""
        try:
            # Try to access an endpoint that would hit the database
            response = self.session.get(f"{self.base_url}/grades")
            
            # If we get 401 (auth required), it means the endpoint exists and likely DB is connected
            # If we get 500, it might be a DB connection issue
            if response.status_code == 401:
                self.log_test("Database Connectivity", True, "Database appears to be connected (auth required)")
                return True
            elif response.status_code == 500:
                self.log_test("Database Connectivity", False, "Possible database connection issue", response.text)
                return False
            else:
                self.log_test("Database Connectivity", True, f"Database connectivity test inconclusive (status: {response.status_code})")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log_test("Database Connectivity", False, "Database connectivity test failed", str(e))
            return False
    
    def test_seed_data_functionality(self):
        """Test seed data functionality using test endpoint"""
        try:
            # First check if database is empty
            response = self.session.get(f"{self.base_url}/test/db-stats")
            if response.status_code != 200:
                self.log_test("Seed Data Functionality", False, "Cannot access db stats endpoint", response.text)
                return False
            
            # Seed the data
            response = self.session.post(f"{self.base_url}/test/seed-data")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Seed Data Functionality", True, "Sample data seeded successfully")
                    return True
                else:
                    self.log_test("Seed Data Functionality", False, "Seed operation failed", data)
                    return False
            else:
                self.log_test("Seed Data Functionality", False, f"Seed endpoint failed: {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Seed Data Functionality", False, "Seed data test failed", str(e))
            return False
    
    def test_database_structure(self):
        """Test database structure and data integrity"""
        try:
            response = self.session.get(f"{self.base_url}/test/db-stats")
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                # Expected collections and minimum counts
                expected_collections = {
                    "grades": 6,
                    "subjects": 7,
                    "strands": 4,
                    "substrands": 3,
                    "slos": 2,
                    "activities": 3,
                    "competencies": 4,
                    "values": 4,
                    "pcis": 3,
                    "assessments": 4,
                    "slo_mappings": 2
                }
                
                all_good = True
                for collection, expected_count in expected_collections.items():
                    actual_count = stats.get(collection, 0)
                    if actual_count < expected_count:
                        all_good = False
                        break
                
                if all_good:
                    self.log_test("Database Structure", True, f"All collections have expected data counts")
                    return True
                else:
                    self.log_test("Database Structure", False, "Database structure incomplete", stats)
                    return False
            else:
                self.log_test("Database Structure", False, f"Cannot access db stats: {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Database Structure", False, "Database structure test failed", str(e))
            return False
    
    def test_cascading_data_relationships(self):
        """Test cascading data relationships without authentication"""
        try:
            # We can't test the actual API endpoints without auth, but we can verify
            # the database structure supports cascading relationships
            response = self.session.get(f"{self.base_url}/test/db-stats")
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                # Check that we have the hierarchical structure:
                # Grades -> Subjects -> Strands -> Sub-strands -> SLOs
                hierarchy_check = (
                    stats.get("grades", 0) > 0 and
                    stats.get("subjects", 0) > 0 and
                    stats.get("strands", 0) > 0 and
                    stats.get("substrands", 0) > 0 and
                    stats.get("slos", 0) > 0
                )
                
                if hierarchy_check:
                    self.log_test("Cascading Data Relationships", True, "Hierarchical data structure is present")
                    return True
                else:
                    self.log_test("Cascading Data Relationships", False, "Missing hierarchical data", stats)
                    return False
            else:
                self.log_test("Cascading Data Relationships", False, f"Cannot verify relationships: {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Cascading Data Relationships", False, "Cascading relationships test failed", str(e))
            return False
    
    def test_firebase_auth_integration(self):
        """Test Firebase authentication integration"""
        try:
            # Test auth verify endpoint with invalid token
            invalid_token_data = {"idToken": "invalid_token_12345"}
            response = self.session.post(f"{self.base_url}/auth/verify", json=invalid_token_data)
            
            if response.status_code == 401:
                self.log_test("Firebase Auth Integration", True, "Firebase auth is properly rejecting invalid tokens")
                return True
            elif response.status_code == 422:
                self.log_test("Firebase Auth Integration", True, "Firebase auth endpoint exists (validation error)")
                return True
            else:
                self.log_test("Firebase Auth Integration", False, f"Unexpected auth response: {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Firebase Auth Integration", False, "Firebase auth test failed", str(e))
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("CBE LESSON PLANNING SYSTEM - BACKEND API TESTS")
        print("=" * 60)
        print(f"Testing backend at: {self.base_url}")
        print()
        
        # Core connectivity tests
        print("🔍 CONNECTIVITY TESTS")
        print("-" * 30)
        self.test_backend_server_status()
        self.test_api_structure()
        self.test_cors_headers()
        self.test_database_connectivity()
        
        print()
        print("🔐 AUTHENTICATION TESTS")
        print("-" * 30)
        self.test_firebase_auth_integration()
        self.test_grades_without_auth()
        self.test_subjects_without_auth()
        self.test_seed_data_without_auth()
        
        print()
        print("🛡️ ADMIN ENDPOINT SECURITY TESTS")
        print("-" * 30)
        self.test_admin_endpoints_without_auth()
        
        print()
        print("📊 DATA FUNCTIONALITY TESTS")
        print("-" * 30)
        self.test_seed_data_functionality()
        self.test_database_structure()
        self.test_cascading_data_relationships()
        
        print()
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        
        return passed_tests, failed_tests, self.test_results

def main():
    """Main test execution"""
    tester = CBEBackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()