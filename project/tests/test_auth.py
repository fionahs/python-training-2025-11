"""
API tests for authentication endpoints
"""
import pytest


class TestAuthenticationEndpoints:
    """Test authentication API endpoints"""

    def test_login_success(self, client, test_users):
        """Test successful login"""
        response = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "AdminTest123!"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_users):
        """Test login with wrong password"""
        response = client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "WrongPassword"
        })

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client, test_users):
        """Test login with non-existent user"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "Password123!"
        })

        assert response.status_code == 401

    def test_get_current_user(self, client, admin_token):
        """Test getting current user info"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["full_name"] == "Admin User"

    def test_get_current_user_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/auth/me")

        assert response.status_code == 403  # FastAPI HTTPBearer returns 403

    def test_get_current_user_invalid_token(self, client):
        """Test with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        assert response.status_code == 401

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid_refresh_token"
        })

        assert response.status_code == 401
