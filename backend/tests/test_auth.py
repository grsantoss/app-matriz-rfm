import pytest
from unittest.mock import patch, MagicMock
import json

# Mock response for auth service
def mock_response(status_code=200, json_data=None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    return response

@pytest.mark.parametrize(
    "user_data,status_code,response_data",
    [
        (
            {"name": "New User", "email": "new@example.com", "password": "password123"},
            201,
            {"message": "User registered successfully", "user_id": 1}
        ),
        (
            {"name": "Existing User", "email": "existing@example.com", "password": "password123"},
            400,
            {"detail": "Email already in use"}
        ),
        (
            {"name": "Invalid", "email": "invalid-email", "password": "weak"},
            422,
            {"detail": "Validation error"}
        )
    ]
)
def test_register(client, user_data, status_code, response_data):
    """Test user registration endpoint"""
    with patch('requests.post') as mock_post:
        # Mock the response from auth service
        mock_post.return_value = mock_response(status_code, response_data)
        
        # Make request to register endpoint
        response = client.post("/auth/register", json=user_data)
        
        # Check response
        assert response.status_code == status_code
        assert response.json() == response_data

@pytest.mark.parametrize(
    "credentials,status_code,response_data",
    [
        (
            {"username": "valid@example.com", "password": "correct-password"},
            200,
            {
                "access_token": "jwt-token", 
                "token_type": "bearer",
                "user": {"id": 1, "name": "Test User", "email": "valid@example.com"}
            }
        ),
        (
            {"username": "invalid@example.com", "password": "wrong-password"},
            401,
            {"detail": "Invalid username or password"}
        )
    ]
)
def test_login(client, credentials, status_code, response_data):
    """Test login endpoint"""
    with patch('requests.post') as mock_post:
        # Mock the response from auth service
        mock_post.return_value = mock_response(status_code, response_data)
        
        # Make request to login endpoint using form data
        response = client.post(
            "/auth/login",
            data=credentials
        )
        
        # Check response
        assert response.status_code == status_code
        if status_code == 200:
            assert response.json() == response_data

def test_forgot_password(client):
    """Test forgot password endpoint"""
    with patch('requests.post') as mock_post:
        # Mock response for successful password reset request
        mock_post.return_value = mock_response(
            200, 
            {"message": "Password reset email sent"}
        )
        
        # Send request
        response = client.post(
            "/auth/forgot-password",
            json={"email": "user@example.com"}
        )
        
        # Check response
        assert response.status_code == 200
        assert response.json() == {"message": "Password reset email sent"}

def test_reset_password(client):
    """Test reset password endpoint"""
    with patch('requests.post') as mock_post:
        # Mock response for successful password reset
        mock_post.return_value = mock_response(
            200, 
            {"message": "Password reset successfully"}
        )
        
        # Send request
        response = client.post(
            "/auth/reset-password",
            json={
                "token": "reset-token-123",
                "password": "new-password123"
            }
        )
        
        # Check response
        assert response.status_code == 200
        assert response.json() == {"message": "Password reset successfully"}

def test_verify_token(client):
    """Test token verification endpoint"""
    with patch('requests.post') as mock_post:
        # Mock response for valid token
        mock_post.return_value = mock_response(
            200, 
            {
                "valid": True,
                "user": {"id": 1, "name": "Test User", "email": "test@example.com"}
            }
        )
        
        # Send request
        response = client.post(
            "/auth/verify-token",
            json={"token": "valid-jwt-token"}
        )
        
        # Check response
        assert response.status_code == 200
        assert response.json()["valid"] == True
        assert "user" in response.json() 