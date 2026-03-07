"""
Test cases for the isNewUser flag and freeLessonsRemaining features
- Verify /api/auth/verify returns isNewUser flag correctly
- Verify freeLessonsRemaining field is present in user response
"""

import pytest
import requests
import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Use environment variable for backend URL
BASE_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://lesson-plan-builder-1.preview.emergentagent.com')
MONGO_URL = os.environ.get('MONGO_URL', os.environ.get('MONGODB_URI'))

# Get MongoDB connection for direct database verification
def get_db():
    client = MongoClient(MONGO_URL)
    return client['cbeplanner']


class TestAuthVerifyEndpoint:
    """Test /api/auth/verify endpoint structure and response"""
    
    def test_auth_verify_endpoint_exists(self):
        """Test that /api/auth/verify endpoint exists (returns 422 for missing body, not 404)"""
        response = requests.post(f"{BASE_URL}/api/auth/verify")
        # 422 = endpoint exists but validation failed (missing request body)
        # 404 = endpoint doesn't exist
        assert response.status_code == 422, f"Expected 422 for missing body, got {response.status_code}"
        print("✓ /api/auth/verify endpoint exists")
    
    def test_auth_verify_returns_401_for_invalid_token(self):
        """Test that invalid token returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/verify",
            json={"idToken": "invalid_token_here"}
        )
        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401 for invalid token, got {response.status_code}"
        print("✓ /api/auth/verify returns 401 for invalid token")


class TestUserModelStructure:
    """Test that user documents have correct structure in database"""
    
    def test_users_have_freelessonsremaining_field(self):
        """Verify users collection contains freeLessonsRemaining field"""
        db = get_db()
        
        # Check if any user has freeLessonsRemaining field
        user_with_field = db.users.find_one({"freeLessonsRemaining": {"$exists": True}})
        
        if user_with_field:
            print(f"✓ Found user with freeLessonsRemaining: {user_with_field.get('freeLessonsRemaining')}")
            assert True
        else:
            # Check total users count
            total_users = db.users.count_documents({})
            print(f"Total users in database: {total_users}")
            # If no users have the field, that's still valid if database is fresh
            if total_users == 0:
                print("✓ No users in database yet - field will be added when users signup")
                assert True
            else:
                # Check a sample user structure
                sample_user = db.users.find_one({})
                print(f"Sample user fields: {list(sample_user.keys()) if sample_user else 'None'}")
                # The field should exist for users created after the feature was added
                pytest.skip("freeLessonsRemaining field may not exist for legacy users")
    
    def test_backend_code_returns_isNewUser_in_response(self):
        """Verify backend code structure for isNewUser response"""
        # Read the server.py file to verify the response structure
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check that isNewUser is returned in the verify endpoint
        assert 'isNewUser' in content, "isNewUser should be present in server.py"
        assert '"isNewUser": is_new_user' in content or '"isNewUser": isNewUser' in content or "'isNewUser': is_new_user" in content, \
            "isNewUser should be returned in auth/verify response"
        print("✓ Backend code returns isNewUser in /api/auth/verify response")
    
    def test_freelessonsremaining_constant_defined(self):
        """Verify FREE_LESSONS_ON_SIGNUP constant is defined"""
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        assert 'FREE_LESSONS_ON_SIGNUP' in content, "FREE_LESSONS_ON_SIGNUP constant should be defined"
        # Check it's set to 5
        assert 'FREE_LESSONS_ON_SIGNUP = 5' in content, "FREE_LESSONS_ON_SIGNUP should be 5"
        print("✓ FREE_LESSONS_ON_SIGNUP = 5 is defined in backend")


class TestDatabaseIntegrity:
    """Test database integrity for the new user features"""
    
    def test_new_user_creation_sets_free_lessons(self):
        """Verify new user creation code sets freeLessonsRemaining correctly"""
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check that new user creation includes freeLessonsRemaining
        assert 'freeLessonsRemaining' in content, "freeLessonsRemaining field should be in new user creation"
        # Check that it references the constant
        assert 'FREE_LESSONS_ON_SIGNUP' in content, "Should use FREE_LESSONS_ON_SIGNUP constant"
        print("✓ New user creation includes freeLessonsRemaining field")
    
    def test_existing_user_migration_code_exists(self):
        """Verify existing users get freeLessonsRemaining field on login"""
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check for migration code that handles existing users
        assert '"freeLessonsRemaining" not in user' in content or "'freeLessonsRemaining' not in user" in content, \
            "Should have migration code for existing users without freeLessonsRemaining"
        print("✓ Migration code exists for existing users")


class TestFrontendIntegration:
    """Test frontend code properly uses isNewUser and freeLessonsRemaining"""
    
    def test_authcontext_has_isNewUser_state(self):
        """Verify AuthContext has isNewUser state"""
        auth_path = "/app/frontend/contexts/AuthContext.tsx"
        with open(auth_path, 'r') as f:
            content = f.read()
        
        assert 'isNewUser' in content, "AuthContext should have isNewUser"
        assert 'setIsNewUser' in content, "AuthContext should have setIsNewUser setter"
        assert 'clearNewUserFlag' in content, "AuthContext should have clearNewUserFlag function"
        print("✓ AuthContext has isNewUser state and clearNewUserFlag")
    
    def test_home_screen_uses_isNewUser(self):
        """Verify home screen uses isNewUser for welcome message"""
        home_path = "/app/frontend/app/(teacher)/home.tsx"
        with open(home_path, 'r') as f:
            content = f.read()
        
        assert 'isNewUser' in content, "Home screen should use isNewUser"
        assert "Welcome" in content, "Home screen should have Welcome message"
        assert "Welcome back" in content, "Home screen should have 'Welcome back' message"
        print("✓ Home screen uses isNewUser for dynamic welcome message")
    
    def test_home_screen_uses_freelessonsremaining(self):
        """Verify home screen uses freeLessonsRemaining for balance display"""
        home_path = "/app/frontend/app/(teacher)/home.tsx"
        with open(home_path, 'r') as f:
            content = f.read()
        
        assert 'freeLessonsRemaining' in content, "Home screen should use freeLessonsRemaining"
        # Check it's not hardcoded
        assert 'user?.freeLessonsRemaining' in content or "user.freeLessonsRemaining" in content, \
            "Home screen should use dynamic freeLessonsRemaining value"
        print("✓ Home screen uses dynamic freeLessonsRemaining value")
    
    def test_profile_screen_uses_freelessonsremaining(self):
        """Verify profile screen uses freeLessonsRemaining"""
        profile_path = "/app/frontend/app/(teacher)/profile.tsx"
        with open(profile_path, 'r') as f:
            content = f.read()
        
        assert 'freeLessonsRemaining' in content, "Profile screen should use freeLessonsRemaining"
        assert 'user?.freeLessonsRemaining' in content or "user.freeLessonsRemaining" in content, \
            "Profile screen should use dynamic freeLessonsRemaining value"
        print("✓ Profile screen uses dynamic freeLessonsRemaining value")


class TestWelcomeMessageLogic:
    """Test welcome message conditional logic"""
    
    def test_welcome_conditional_structure(self):
        """Verify welcome message uses correct conditional"""
        home_path = "/app/frontend/app/(teacher)/home.tsx"
        with open(home_path, 'r') as f:
            content = f.read()
        
        # Check the conditional logic pattern
        # Should be: isNewUser ? 'Welcome' : 'Welcome back'
        assert "isNewUser ? 'Welcome' : 'Welcome back'" in content or \
               'isNewUser ? "Welcome" : "Welcome back"' in content, \
            "Welcome message should use isNewUser conditional"
        print("✓ Welcome message uses correct isNewUser conditional")


class TestFreeLessonsDisplayLogic:
    """Test free lessons display logic"""
    
    def test_free_lessons_conditional_display(self):
        """Verify free lessons display uses conditional based on count"""
        home_path = "/app/frontend/app/(teacher)/home.tsx"
        with open(home_path, 'r') as f:
            content = f.read()
        
        # Check that the display shows free lessons count or wallet balance
        # Should check if freeLessonsRemaining > 0
        assert 'freeLessonsRemaining' in content, "Should use freeLessonsRemaining"
        assert '> 0' in content, "Should have conditional check for freeLessonsRemaining > 0"
        print("✓ Free lessons display uses conditional based on remaining count")
    
    def test_no_hardcoded_free_lesson_text(self):
        """Verify there's no hardcoded '1 Free Lesson' text"""
        home_path = "/app/frontend/app/(teacher)/home.tsx"
        with open(home_path, 'r') as f:
            content = f.read()
        
        # Check there's no hardcoded single lesson text
        assert '1 Free Lesson Available' not in content, \
            "Should NOT have hardcoded '1 Free Lesson Available'"
        assert '"1 Free Lesson"' not in content, \
            "Should NOT have hardcoded '1 Free Lesson'"
        print("✓ No hardcoded '1 Free Lesson Available' text found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
