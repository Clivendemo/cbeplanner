"""
CBE Planner API Tests - Iteration 5
Tests for authentication, grades, and health endpoints
"""
import pytest
import requests
import os

# Get backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://magical-shannon-6.preview.emergentagent.com')

class TestHealthEndpoints:
    """Health check endpoint tests"""
    
    def test_health_check_api(self):
        """Test API health check endpoint with database status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "database" in data
        assert data.get("database") == "connected"
        print(f"✅ API health check passed: {data}")


class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    def test_auth_verify_rejects_invalid_token(self):
        """Test that /api/auth/verify rejects invalid tokens"""
        response = requests.post(
            f"{BASE_URL}/api/auth/verify",
            json={"idToken": "invalid_token_12345"}
        )
        # Should return 401 for invalid token
        assert response.status_code == 401
        print(f"✅ Auth verify correctly rejects invalid token: {response.status_code}")
    
    def test_auth_verify_rejects_empty_token(self):
        """Test that /api/auth/verify rejects empty token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/verify",
            json={"idToken": ""}
        )
        # Should return 401 for empty token
        assert response.status_code == 401
        print(f"✅ Auth verify correctly rejects empty token: {response.status_code}")
    
    def test_auth_verify_rejects_missing_token(self):
        """Test that /api/auth/verify rejects missing token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/verify",
            json={}
        )
        # Should return 422 (validation error) or 401
        assert response.status_code in [401, 422]
        print(f"✅ Auth verify correctly rejects missing token: {response.status_code}")


class TestProtectedEndpoints:
    """Tests for protected endpoints requiring authentication"""
    
    def test_grades_requires_auth(self):
        """Test that /api/grades requires authentication"""
        response = requests.get(f"{BASE_URL}/api/grades")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✅ Grades endpoint correctly requires auth: {response.status_code}")
    
    def test_profile_requires_auth(self):
        """Test that /api/profile requires authentication"""
        response = requests.get(f"{BASE_URL}/api/profile")
        assert response.status_code == 401
        print(f"✅ Profile endpoint correctly requires auth: {response.status_code}")
    
    def test_wallet_balance_requires_auth(self):
        """Test that /api/wallet/balance requires authentication"""
        response = requests.get(f"{BASE_URL}/api/wallet/balance")
        assert response.status_code == 401
        print(f"✅ Wallet balance endpoint correctly requires auth: {response.status_code}")
    
    def test_lesson_plans_generate_requires_auth(self):
        """Test that /api/lesson-plans/generate requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/lesson-plans/generate",
            json={
                "duration": 40,
                "gradeId": "test",
                "subjectId": "test",
                "strandId": "test",
                "substrandId": "test",
                "sloId": "test"
            }
        )
        assert response.status_code == 401
        print(f"✅ Lesson plans generate endpoint correctly requires auth: {response.status_code}")
    
    def test_subjects_requires_auth(self):
        """Test that /api/subjects requires authentication"""
        response = requests.get(f"{BASE_URL}/api/subjects?gradeId=test")
        assert response.status_code == 401
        print(f"✅ Subjects endpoint correctly requires auth: {response.status_code}")
    
    def test_strands_requires_auth(self):
        """Test that /api/strands requires authentication"""
        response = requests.get(f"{BASE_URL}/api/strands?subjectId=test")
        assert response.status_code == 401
        print(f"✅ Strands endpoint correctly requires auth: {response.status_code}")


class TestSecurityHeaders:
    """Tests for security headers"""
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        # Check for security headers
        headers = response.headers
        
        # X-Content-Type-Options
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"
        
        # X-Frame-Options
        assert "x-frame-options" in headers
        assert headers["x-frame-options"] == "DENY"
        
        # X-XSS-Protection
        assert "x-xss-protection" in headers
        
        print(f"✅ Security headers present: x-content-type-options, x-frame-options, x-xss-protection")


class TestCORSConfiguration:
    """Tests for CORS configuration"""
    
    def test_cors_allows_frontend_origin(self):
        """Test that CORS allows the frontend origin"""
        response = requests.options(
            f"{BASE_URL}/api/health",
            headers={
                "Origin": "https://magical-shannon-6.preview.emergentagent.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        # Should return 200 or 204 for preflight
        assert response.status_code in [200, 204]
        print(f"✅ CORS preflight passed: {response.status_code}")


class TestAdminEndpoints:
    """Tests for admin endpoints"""
    
    def test_admin_wallet_transactions_requires_auth(self):
        """Test that /api/admin/wallet-transactions requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/wallet-transactions")
        assert response.status_code == 401
        print(f"✅ Admin wallet transactions endpoint correctly requires auth: {response.status_code}")
    
    def test_admin_reconciliation_requires_auth(self):
        """Test that /api/admin/wallet-reconciliation requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/wallet-reconciliation")
        assert response.status_code == 401
        print(f"✅ Admin reconciliation endpoint correctly requires auth: {response.status_code}")


class TestSchemeEndpoints:
    """Tests for scheme of work endpoints"""
    
    def test_schemes_topics_requires_auth(self):
        """Test that /api/schemes/topics requires authentication"""
        response = requests.get(f"{BASE_URL}/api/schemes/topics?subjectId=test&gradeId=test")
        assert response.status_code == 401
        print(f"✅ Schemes topics endpoint correctly requires auth: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
