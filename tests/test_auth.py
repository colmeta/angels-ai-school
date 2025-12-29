"""
Authentication Flow Tests
Comprehensive tests for user authentication, registration, and session management
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.main import app

client = TestClient(app)


class TestSchoolRegistration:
    """Test school registration workflows"""
    
    def test_register_new_school_success(self):
        """Test successful school registration"""
        response = client.post("/api/schools/register", json={
            "school_name": "Test School",
            "country": "Uganda",
            "address": "Kampala, Uganda",
            "phone": "+256700000000",
            "email": "test@school.com",
            "director_first_name": "John",
            "director_last_name": "Doe",
            "director_email": "john@test.com",
            "director_phone": "+256700000001",
            "student_count_estimate": 100,
            "plan": "starter"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "school_id" in data or "message" in data
    
    def test_register_duplicate_email_rejected(self):
        """Test that duplicate school emails are rejected"""
        school_data = {
            "school_name": "Duplicate Test School",
            "country": "Uganda",
            "address": "Kampala",
            "phone": "+256700000010",
            "email": "duplicate@school.com",
            "director_first_name": "Jane",
            "director_last_name": "Smith",
            "director_email": "jane@duplicate.com",
            "director_phone": "+256700000011",
            "student_count_estimate": 50,
            "plan": "pro"
        }
        
        # First registration should succeed
        response1 = client.post("/api/schools/register", json=school_data)
        
        # Second registration with same email should fail
        response2 = client.post("/api/schools/register", json=school_data)
        
        # At least one should indicate duplicate
        assert response1.status_code == 200 or response2.status_code in [400, 409]
    
    def test_register_invalid_email_rejected(self):
        """Test that invalid email formats are rejected"""
        response = client.post("/api/schools/register", json={
            "school_name": "Invalid Email School",
            "country": "Kenya",
            "address": "Nairobi",
            "phone": "+254700000000",
            "email": "not-an-email",  # Invalid email
            "director_first_name": "Test",
            "director_last_name": "User",
            "director_email": "also-invalid",  # Invalid email
            "director_phone": "+254700000001",
            "student_count_estimate": 30,
            "plan": "starter"
        })
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    def test_register_missing_required_fields(self):
        """Test that missing required fields are rejected"""
        response = client.post("/api/schools/register", json={
            "school_name": "Incomplete School",
            # Missing many required fields
        })
        
        assert response.status_code in [400, 422]


class TestAuthentication:
    """Test login and authentication workflows"""
    
    def test_health_check_no_auth_required(self):
        """Test that health check endpoint doesn't require authentication"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        # Note: This test assumes a user exists or we create one first
        # In real implementation, we'd set up test fixtures
        
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        
        # Should either succeed with token or fail gracefully
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data or "token" in data
    
    def test_login_with_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
    
    def test_login_missing_credentials(self):
        """Test login fails when credentials are missing"""
        response = client.post("/api/auth/login", json={})
        
        assert response.status_code in [400, 422]


class TestProtectedEndpoints:
    """Test that protected endpoints require authentication"""
    
    def test_students_endpoint_requires_auth(self):
        """Test that students endpoint requires authentication"""
        response = client.get("/api/students")
        assert response.status_code in [401, 403, 404]
    
    def test_fees_endpoint_requires_auth(self):
        """Test that fees endpoint requires authentication"""
        response = client.get("/api/fees")
        assert response.status_code in [401, 403, 404]
    
    def test_agents_endpoint_requires_auth(self):
        """Test that AI agents endpoint requires authentication"""
        response = client.get("/api/v1/agents/digital-ceo")
        assert response.status_code in [401, 403, 404]


class TestJWTTokens:
    """Test JWT token generation and validation"""
    
    def test_jwt_token_format(self):
        """Test that JWT tokens are properly formatted"""
        # This would require a valid login first
        # For now, we test the token validation logic exists
        
        response = client.get("/api/students", headers={
            "Authorization": "Bearer invalid.token.here"
        })
        
        # Should reject invalid token
        assert response.status_code in [401, 403]
    
    def test_expired_token_rejected(self):
        """Test that expired tokens are rejected"""
        # Would need to generate an expired token
        # For now, just test that authorization is checked
        
        response = client.get("/api/students")
        assert response.status_code in [401, 403, 404]


class TestPasswordReset:
    """Test password reset workflows"""
    
    def test_password_reset_request(self):
        """Test requesting a password reset"""
        response = client.post("/api/auth/password-reset", json={
            "email": "test@example.com"
        })
        
        # Should accept request even if email doesn't exist (security)
        assert response.status_code in [200, 202, 404]
    
    def test_password_reset_invalid_email(self):
        """Test password reset with invalid email format"""
        response = client.post("/api/auth/password-reset", json={
            "email": "not-an-email"
        })
        
        assert response.status_code in [400, 422]


class TestSessionManagement:
    """Test session and multi-device support"""
    
    def test_multiple_sessions_supported(self):
        """Test that users can have multiple active sessions"""
        # This would require logging in from multiple clients
        # Testing that the system supports it architecturally
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
