"""Tests for user endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    """Test creating a new user."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User",
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_username(client: AsyncClient) -> None:
    """Test creating user with duplicate username fails."""
    user_data = {
        "email": "test1@example.com",
        "username": "testuser",
        "password": "testpass123",
    }
    await client.post("/users/", json=user_data)

    # Try to create another user with same username
    user_data2 = {
        "email": "test2@example.com",
        "username": "testuser",
        "password": "testpass123",
    }
    response = await client.post("/users/", json=user_data2)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient) -> None:
    """Test creating user with duplicate email fails."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser1",
        "password": "testpass123",
    }
    await client.post("/users/", json=user_data)

    # Try to create another user with same email
    user_data2 = {
        "email": "test@example.com",
        "username": "testuser2",
        "password": "testpass123",
    }
    response = await client.post("/users/", json=user_data2)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_read_users(client: AsyncClient) -> None:
    """Test reading users list."""
    # Create a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    }
    await client.post("/users/", json=user_data)

    # Login to get token
    login_data = {"username": "testuser", "password": "testpass123"}
    token_response = await client.post("/auth/token", data=login_data)
    token = token_response.json()["access_token"]

    # Read users
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_read_users_unauthorized(client: AsyncClient) -> None:
    """Test reading users without authentication fails."""
    response = await client.get("/users/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_read_user_by_id(client: AsyncClient) -> None:
    """Test reading a specific user by ID."""
    # Create a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    }
    create_response = await client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Login to get token
    login_data = {"username": "testuser", "password": "testpass123"}
    token_response = await client.post("/auth/token", data=login_data)
    token = token_response.json()["access_token"]

    # Read user by ID
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_read_user_not_found(client: AsyncClient) -> None:
    """Test reading non-existent user returns 404."""
    # Create and login user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    }
    await client.post("/users/", json=user_data)

    login_data = {"username": "testuser", "password": "testpass123"}
    token_response = await client.post("/auth/token", data=login_data)
    token = token_response.json()["access_token"]

    # Try to read non-existent user
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/users/99999", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient) -> None:
    """Test updating a user."""
    # Create a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    }
    create_response = await client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Login to get token
    login_data = {"username": "testuser", "password": "testpass123"}
    token_response = await client.post("/auth/token", data=login_data)
    token = token_response.json()["access_token"]

    # Update user
    update_data = {"full_name": "Updated Name"}
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.put(f"/users/{user_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_user_forbidden(client: AsyncClient) -> None:
    """Test updating another user's profile is forbidden."""
    # Create two users
    user1_data = {
        "email": "user1@example.com",
        "username": "user1",
        "password": "testpass123",
    }
    await client.post("/users/", json=user1_data)

    user2_data = {
        "email": "user2@example.com",
        "username": "user2",
        "password": "testpass123",
    }
    user2_response = await client.post("/users/", json=user2_data)
    user2_id = user2_response.json()["id"]

    # Login as user1
    login_data = {"username": "user1", "password": "testpass123"}
    token_response = await client.post("/auth/token", data=login_data)
    token = token_response.json()["access_token"]

    # Try to update user2
    update_data = {"full_name": "Hacker"}
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.put(f"/users/{user2_id}", json=update_data, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_as_superuser(client: AsyncClient) -> None:
    """Test deleting a user as superuser."""
    # Create a superuser
    superuser_data = {
        "email": "admin@example.com",
        "username": "admin",
        "password": "adminpass123",
        "is_superuser": True,
    }
    await client.post("/users/", json=superuser_data)

    # Create a regular user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    }
    user_response = await client.post("/users/", json=user_data)
    user_id = user_response.json()["id"]

    # Login as superuser
    login_data = {"username": "admin", "password": "adminpass123"}
    token_response = await client.post("/auth/token", data=login_data)
    token = token_response.json()["access_token"]

    # Delete user
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_forbidden(client: AsyncClient) -> None:
    """Test deleting a user as regular user is forbidden."""
    # Create a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
    }
    user_response = await client.post("/users/", json=user_data)
    user_id = user_response.json()["id"]

    # Login as regular user
    login_data = {"username": "testuser", "password": "testpass123"}
    token_response = await client.post("/auth/token", data=login_data)
    token = token_response.json()["access_token"]

    # Try to delete user (should fail, not superuser)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 403
