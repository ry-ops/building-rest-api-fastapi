"""Example API client for FastAPI REST API."""

import asyncio

import httpx


class FastAPIClient:
    """Client for interacting with the FastAPI REST API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the API.
        """
        self.base_url = base_url
        self.token = None

    async def create_user(self, email: str, username: str, password: str, full_name: str = None) -> dict:
        """
        Create a new user.

        Args:
            email: User email.
            username: Username.
            password: Password.
            full_name: Optional full name.

        Returns:
            dict: Created user data.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/users/",
                json={
                    "email": email,
                    "username": username,
                    "password": password,
                    "full_name": full_name,
                },
            )
            response.raise_for_status()
            return response.json()

    async def login(self, username: str, password: str) -> str:
        """
        Login and get access token.

        Args:
            username: Username.
            password: Password.

        Returns:
            str: Access token.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/token",
                data={"username": username, "password": password},
            )
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            return self.token

    async def get_current_user(self) -> dict:
        """
        Get current user information.

        Returns:
            dict: Current user data.
        """
        if not self.token:
            raise ValueError("Not authenticated. Please login first.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/auth/me",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            response.raise_for_status()
            return response.json()

    async def get_users(self, skip: int = 0, limit: int = 100) -> list:
        """
        Get list of users.

        Args:
            skip: Number of users to skip.
            limit: Maximum number of users to return.

        Returns:
            list: List of users.
        """
        if not self.token:
            raise ValueError("Not authenticated. Please login first.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/",
                params={"skip": skip, "limit": limit},
                headers={"Authorization": f"Bearer {self.token}"},
            )
            response.raise_for_status()
            return response.json()

    async def get_user(self, user_id: int) -> dict:
        """
        Get user by ID.

        Args:
            user_id: User ID.

        Returns:
            dict: User data.
        """
        if not self.token:
            raise ValueError("Not authenticated. Please login first.")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            response.raise_for_status()
            return response.json()

    async def update_user(self, user_id: int, **kwargs) -> dict:
        """
        Update user.

        Args:
            user_id: User ID.
            **kwargs: Fields to update.

        Returns:
            dict: Updated user data.
        """
        if not self.token:
            raise ValueError("Not authenticated. Please login first.")

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/users/{user_id}",
                json=kwargs,
                headers={"Authorization": f"Bearer {self.token}"},
            )
            response.raise_for_status()
            return response.json()


async def main():
    """Example usage of the API client."""
    client = FastAPIClient()

    # Create a new user
    print("Creating user...")
    user = await client.create_user(
        email="john@example.com",
        username="johndoe",
        password="secret123",
        full_name="John Doe",
    )
    print(f"Created user: {user}")

    # Login
    print("\nLogging in...")
    token = await client.login(username="johndoe", password="secret123")
    print(f"Access token: {token[:20]}...")

    # Get current user
    print("\nGetting current user...")
    current_user = await client.get_current_user()
    print(f"Current user: {current_user}")

    # Get all users
    print("\nGetting all users...")
    users = await client.get_users()
    print(f"Total users: {len(users)}")

    # Update user
    print("\nUpdating user...")
    updated_user = await client.update_user(
        user_id=current_user["id"],
        full_name="John Updated Doe",
    )
    print(f"Updated user: {updated_user}")


if __name__ == "__main__":
    asyncio.run(main())
