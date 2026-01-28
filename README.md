# Building REST APIs with FastAPI

A production-ready FastAPI application demonstrating best practices for building high-performance REST APIs with automatic documentation, type safety, and modern Python features.

## Features

- **Fast Performance**: Built on Starlette and Pydantic for blazing-fast request handling
- **Automatic Documentation**: Interactive API docs with Swagger UI and ReDoc
- **Type Safety**: Full type hints with Pydantic models for request/response validation
- **Async Support**: Async/await for high concurrency
- **Database Integration**: SQLAlchemy ORM with async support
- **Authentication**: JWT-based authentication
- **Testing**: Comprehensive test suite with pytest
- **Docker Ready**: Multi-stage Dockerfile for production deployment

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/ry-ops/building-rest-api-fastapi.git
cd building-rest-api-fastapi
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
uvicorn app.main:app --reload
```

5. Access the API:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Docker Deployment

```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database setup
│   ├── dependencies.py         # Dependency injection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── token.py
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── users.py
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── security.py
│       └── validation.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_auth.py
│   └── test_users.py
├── examples/
│   ├── client.py               # Example API client
│   └── load_test.py            # Load testing script
├── documentation/
│   ├── API.md                  # API endpoint documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── DEVELOPMENT.md          # Development guide
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive JWT token
- `POST /auth/refresh` - Refresh access token

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `GET /users/{user_id}` - Get user by ID (admin only)
- `GET /users` - List all users (admin only)

### Health
- `GET /health` - Health check endpoint
- `GET /` - API information

## Configuration

Copy `.env.example` to `.env` and configure:

```env
# Application
APP_NAME=FastAPI Application
APP_VERSION=1.0.0
DEBUG=False

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_users.py
```

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Linting
ruff check app/ tests/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Examples

### Using the API Client

```python
from examples.client import APIClient

# Initialize client
client = APIClient(base_url="http://localhost:8000")

# Register a user
user = client.register(
    email="user@example.com",
    password="securepassword",
    full_name="John Doe"
)

# Login
token = client.login(email="user@example.com", password="securepassword")

# Get current user
profile = client.get_current_user(token)
```

### Making Direct Requests

```python
import requests

# Register
response = requests.post(
    "http://localhost:8000/auth/register",
    json={
        "email": "user@example.com",
        "password": "securepassword",
        "full_name": "John Doe"
    }
)

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    data={
        "username": "user@example.com",
        "password": "securepassword"
    }
)
token = response.json()["access_token"]

# Get profile
response = requests.get(
    "http://localhost:8000/users/me",
    headers={"Authorization": f"Bearer {token}"}
)
```

## Deployment

See [documentation/DEPLOYMENT.md](documentation/DEPLOYMENT.md) for detailed deployment instructions including:

- Docker deployment
- Kubernetes deployment
- Cloud platform deployment (AWS, GCP, Azure)
- Environment configuration
- SSL/TLS setup
- Monitoring and logging

## Performance

FastAPI is one of the fastest Python frameworks available:

- Handles 10,000+ requests/second on modest hardware
- Sub-millisecond response times for simple endpoints
- Efficient async I/O for database and external API calls
- Automatic JSON serialization with Pydantic

See `examples/load_test.py` for performance benchmarking.

## Security

- Password hashing with bcrypt
- JWT token-based authentication
- CORS middleware configured
- SQL injection protection via SQLAlchemy
- Input validation with Pydantic
- Rate limiting (recommended for production)

## Documentation

- [API Documentation](documentation/API.md) - Detailed API endpoint reference
- [Development Guide](documentation/DEVELOPMENT.md) - Development best practices
- [Deployment Guide](documentation/DEPLOYMENT.md) - Production deployment instructions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## Support

For issues and questions:
- Check the [API Documentation](documentation/API.md)
- Review existing GitHub issues
- Open a new issue with detailed information
