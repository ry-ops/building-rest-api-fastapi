# API Documentation

Complete API reference for the FastAPI REST API.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Create a user account via `POST /users/`
2. Obtain an access token via `POST /auth/token`
3. Include the token in the Authorization header: `Authorization: Bearer <token>`

## Endpoints

### Root

#### GET /

Get API information.

**Response:**
```json
{
  "message": "Welcome to FastAPI REST API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### Authentication

#### POST /auth/token

Login and obtain an access token.

**Request Body (form-data):**
- `username` (string, required): Username
- `password` (string, required): Password

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK`: Successfully authenticated
- `401 Unauthorized`: Invalid credentials

#### GET /auth/me

Get current authenticated user information.

**Headers:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-01-27T12:00:00Z",
  "updated_at": "2026-01-27T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: Invalid or missing token

### Users

#### POST /users/

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-01-27T12:00:00Z",
  "updated_at": "2026-01-27T12:00:00Z"
}
```

**Status Codes:**
- `201 Created`: User created successfully
- `400 Bad Request`: Username or email already exists

#### GET /users/

Get a list of users (requires authentication).

**Headers:**
- `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (integer, optional): Number of users to skip (default: 0)
- `limit` (integer, optional): Maximum number of users to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2026-01-27T12:00:00Z",
    "updated_at": "2026-01-27T12:00:00Z"
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: Not authenticated

#### GET /users/{user_id}

Get a specific user by ID (requires authentication).

**Headers:**
- `Authorization: Bearer <token>`

**Path Parameters:**
- `user_id` (integer, required): User ID

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-01-27T12:00:00Z",
  "updated_at": "2026-01-27T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: User not found

#### PUT /users/{user_id}

Update a user (requires authentication, users can only update their own profile unless they're superuser).

**Headers:**
- `Authorization: Bearer <token>`

**Path Parameters:**
- `user_id` (integer, required): User ID

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "New Full Name",
  "password": "newpassword123",
  "is_active": true
}
```

All fields are optional. Only provide fields you want to update.

**Response:**
```json
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "New Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-01-27T12:00:00Z",
  "updated_at": "2026-01-27T12:30:00Z"
}
```

**Status Codes:**
- `200 OK`: User updated successfully
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not enough permissions
- `404 Not Found`: User not found

#### DELETE /users/{user_id}

Delete a user (requires superuser authentication).

**Headers:**
- `Authorization: Bearer <token>`

**Path Parameters:**
- `user_id` (integer, required): User ID

**Status Codes:**
- `204 No Content`: User deleted successfully
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not a superuser
- `404 Not Found`: User not found

## Interactive Documentation

The API provides interactive documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. Consider adding rate limiting for production use.

## CORS

CORS is configured to allow requests from:
- `http://localhost:3000`
- `http://localhost:8000`

Configure additional origins in `.env` file.
