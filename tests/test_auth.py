"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_token_login_success(client: AsyncClient) -> None:
    """Test successful login returns access token."""
    # First create a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User",
    }
    await client.post("/users/", json=user_data)

    # Login with credentials
    login_data = {
        "username": "testuser",
        "password": "testpass123",
    }
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_token_login_invalid_credentials(client: AsyncClient) -> None:
    """Test login with invalid credentials fails."""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword",
    }
    response = await client.post("/auth/token", data=login_data)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect username or password"


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient) -> None:
    """Test getting current user information."""
    # Create and login user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User",
    }
    await client.post("/users/", json=user_data)

    login_data = {
        "username": "testuser",
        "password": "testpass123",
    }
    token_response = await client.post("/auth/token", data=login_data)
    token = token_response.json()["access_token"]

    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient) -> None:
    """Test getting current user with invalid token fails."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient) -> None:
    """Test getting current user without token fails."""
    response = await client.get("/auth/me")
    assert response.status_code == 401
