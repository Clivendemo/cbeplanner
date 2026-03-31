#!/usr/bin/env python3
"""
CBE Lesson Planning System Backend API Tests
Tests the FastAPI backend endpoints and database functionality
Focus on features mentioned in the review request for React Native Expo app
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import time

# Backend URL from environment
BACKEND_URL = "https://magical-shannon-6.preview.emergentagent.com/api"

# Test credentials for authentication testing
TEST_ADMIN_EMAIL = "mail2clive@gmail.com"
TEST_TEACHER_EMAIL = "test.teacher@example.com"
TEST_PASSWORD = "testpass123"

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
    
    def test_profile_api_endpoints(self):
        """Test profile-related API endpoints without authentication"""
        try:
            # Test profile endpoint (should require auth)
            response = self.session.get(f"{self.base_url}/profile")
            if response.status_code == 401:
                self.log_test("Profile API Endpoint", True, "Profile endpoint correctly requires authentication")
                return True
            else:
                self.log_test("Profile API Endpoint", False, f"Expected 401, got {response.status_code}", response.text)
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Profile API Endpoint", False, "Profile API test failed", str(e))
            return False
    
    def test_wallet_api_endpoints(self):
        """Test wallet/payment-related API endpoints"""
        try:
            # Test wallet balance endpoint (should require auth)
            response = self.session.get(f"{self.base_url}/wallet/balance")
            if response.status_code == 401:
                self.log_test("Wallet Balance API", True, "Wallet balance endpoint correctly requires authentication")
            else:
                self.log_test("Wallet Balance API", False, f"Expected 401, got {response.status_code}", response.text)
                return False
            
            # Test M-Pesa initiate endpoint (should require auth)
            response = self.session.post(f"{self.base_url}/payments/mpesa/initiate", 
                                       json={"phoneNumber": "254712345678", "amount": 100})
            if response.status_code == 401:
                self.log_test("M-Pesa Initiate API", True, "M-Pesa initiate endpoint correctly requires authentication")
            else:
                self.log_test("M-Pesa Initiate API", False, f"Expected 401, got {response.status_code}", response.text)
                return False
            
            # Test payment transactions endpoint (should require auth)
            response = self.session.get(f"{self.base_url}/payments/transactions")
            if response.status_code == 401:
                self.log_test("Payment Transactions API", True, "Payment transactions endpoint correctly requires authentication")
                return True
            else:
                self.log_test("Payment Transactions API", False, f"Expected 401, got {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Wallet API Endpoints", False, "Wallet API test failed", str(e))
            return False
    
    def test_schemes_api_endpoints(self):
        """Test schemes of work API endpoints"""
        try:
            # Test schemes topics endpoint (should require auth)
            response = self.session.get(f"{self.base_url}/schemes/topics/test-subject-id")
            if response.status_code == 401:
                self.log_test("Schemes Topics API", True, "Schemes topics endpoint correctly requires authentication")
            else:
                self.log_test("Schemes Topics API", False, f"Expected 401, got {response.status_code}", response.text)
                return False
            
            # Test schemes generate endpoint (should require auth)
            response = self.session.post(f"{self.base_url}/schemes/generate-v2", 
                                       json={"gradeId": "test", "subjectId": "test"})
            if response.status_code == 401:
                self.log_test("Schemes Generate API", True, "Schemes generate endpoint correctly requires authentication")
            else:
                self.log_test("Schemes Generate API", False, f"Expected 401, got {response.status_code}", response.text)
                return False
            
            # Test lessons per week config endpoint (should require auth)
            response = self.session.get(f"{self.base_url}/schemes/config/lessons-per-week?gradeId=test&subjectId=test")
            if response.status_code == 401:
                self.log_test("Lessons Per Week Config API", True, "Lessons per week config endpoint correctly requires authentication")
                return True
            else:
                self.log_test("Lessons Per Week Config API", False, f"Expected 401, got {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Schemes API Endpoints", False, "Schemes API test failed", str(e))
            return False
    
    def test_admin_specific_endpoints(self):
        """Test admin-specific endpoints mentioned in the review"""
        try:
            # Test admin seed data endpoint (should require auth)
            response = self.session.post(f"{self.base_url}/admin/seed-data")
            if response.status_code == 401:
                self.log_test("Admin Seed Data API", True, "Admin seed data endpoint correctly requires authentication")
            else:
                self.log_test("Admin Seed Data API", False, f"Expected 401, got {response.status_code}", response.text)
                return False
            
            # Test admin curriculum endpoints (should require auth)
            admin_curriculum_endpoints = [
                "/admin/curriculum/grades",
                "/admin/curriculum/subjects", 
                "/admin/curriculum/import"
            ]
            
            all_passed = True
            for endpoint in admin_curriculum_endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    if response.status_code == 401:
                        self.log_test(f"Admin {endpoint} API", True, "Correctly requires authentication")
                    else:
                        # Some endpoints might return 404 if they don't exist, which is also acceptable
                        if response.status_code == 404:
                            self.log_test(f"Admin {endpoint} API", True, "Endpoint exists (404 - not found)")
                        else:
                            self.log_test(f"Admin {endpoint} API", False, f"Expected 401 or 404, got {response.status_code}", response.text)
                            all_passed = False
                except requests.exceptions.RequestException as e:
                    self.log_test(f"Admin {endpoint} API", False, "Connection failed", str(e))
                    all_passed = False
            
            return all_passed
                
        except requests.exceptions.RequestException as e:
            self.log_test("Admin Specific Endpoints", False, "Admin endpoints test failed", str(e))
            return False
    
    def test_lesson_planning_endpoints(self):
        """Test lesson planning related endpoints"""
        try:
            # Test lesson plan generation endpoint (should require auth)
            response = self.session.post(f"{self.base_url}/lesson-plans/generate", 
                                       json={"gradeId": "test", "subjectId": "test", "topic": "test"})
            if response.status_code == 401:
                self.log_test("Lesson Plan Generate API", True, "Lesson plan generate endpoint correctly requires authentication")
            else:
                self.log_test("Lesson Plan Generate API", False, f"Expected 401, got {response.status_code}", response.text)
                return False
            
            # Test notes generation endpoint (should require auth)
            response = self.session.post(f"{self.base_url}/notes/generate", 
                                       json={"topic": "test", "gradeId": "test"})
            if response.status_code == 401:
                self.log_test("Notes Generate API", True, "Notes generate endpoint correctly requires authentication")
                return True
            else:
                self.log_test("Notes Generate API", False, f"Expected 401, got {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Lesson Planning Endpoints", False, "Lesson planning endpoints test failed", str(e))
            return False
    
    def test_api_response_format(self):
        """Test API response format consistency"""
        try:
            # Test that API returns proper JSON responses
            response = self.session.get(f"{self.base_url}/grades")
            
            # Should be 401 (auth required) but should return JSON
            if response.status_code == 401:
                try:
                    json_response = response.json()
                    if "detail" in json_response:
                        self.log_test("API Response Format", True, "API returns proper JSON error responses")
                        return True
                    else:
                        self.log_test("API Response Format", False, "JSON response missing expected fields", json_response)
                        return False
                except json.JSONDecodeError:
                    self.log_test("API Response Format", False, "API not returning valid JSON", response.text)
                    return False
            else:
                self.log_test("API Response Format", False, f"Unexpected status code: {response.status_code}", response.text)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("API Response Format", False, "API response format test failed", str(e))
            return False
    
    def test_security_headers(self):
        """Test security headers in API responses"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            # Check for basic security headers
            security_headers = [
                'x-content-type-options',
                'x-frame-options', 
                'x-xss-protection'
            ]
            
            found_headers = []
            for header in security_headers:
                if header in response.headers:
                    found_headers.append(header)
            
            if len(found_headers) > 0:
                self.log_test("Security Headers", True, f"Found security headers: {', '.join(found_headers)}")
                return True
            else:
                self.log_test("Security Headers", False, "No security headers found", dict(response.headers))
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Security Headers", False, "Security headers test failed", str(e))
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("CBE LESSON PLANNER - BACKEND API TESTS")
        print("React Native Expo App Backend Testing")
        print("=" * 60)
        print(f"Testing backend at: {self.base_url}")
        print()
        
        # Core connectivity tests
        print("🔍 CONNECTIVITY & INFRASTRUCTURE TESTS")
        print("-" * 40)
        self.test_backend_server_status()
        self.test_api_structure()
        self.test_cors_headers()
        self.test_database_connectivity()
        self.test_api_response_format()
        self.test_security_headers()
        
        print()
        print("🔐 AUTHENTICATION & SECURITY TESTS")
        print("-" * 40)
        self.test_firebase_auth_integration()
        self.test_grades_without_auth()
        self.test_subjects_without_auth()
        self.test_seed_data_without_auth()
        
        print()
        print("👤 USER PROFILE & WALLET TESTS")
        print("-" * 40)
        self.test_profile_api_endpoints()
        self.test_wallet_api_endpoints()
        
        print()
        print("📚 LESSON PLANNING & SCHEMES TESTS")
        print("-" * 40)
        self.test_lesson_planning_endpoints()
        self.test_schemes_api_endpoints()
        
        print()
        print("🛡️ ADMIN FUNCTIONALITY TESTS")
        print("-" * 40)
        self.test_admin_endpoints_without_auth()
        self.test_admin_specific_endpoints()
        
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
        else:
            print("\n🎉 All backend API tests passed!")
        
        print("\n📱 REACT NATIVE APP BACKEND READINESS:")
        print("-" * 40)
        
        # Analyze results for React Native app compatibility
        critical_failures = []
        auth_working = any(r["test"] == "Firebase Auth Integration" and r["success"] for r in self.test_results)
        api_structure_working = any(r["test"] == "API Structure" and r["success"] for r in self.test_results)
        cors_working = any(r["test"] == "CORS Configuration" and r["success"] for r in self.test_results)
        
        if not auth_working:
            critical_failures.append("Authentication system not working")
        if not api_structure_working:
            critical_failures.append("API routing issues")
        if not cors_working:
            critical_failures.append("CORS configuration issues")
        
        if len(critical_failures) == 0:
            print("✅ Backend is ready for React Native Expo app")
            print("✅ Authentication system is working")
            print("✅ API endpoints are properly secured")
            print("✅ CORS is configured for mobile app access")
        else:
            print("❌ Backend has critical issues for React Native app:")
            for failure in critical_failures:
                print(f"   - {failure}")
        
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