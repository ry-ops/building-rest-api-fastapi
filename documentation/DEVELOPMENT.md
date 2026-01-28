# Development Guide

Guide for setting up and developing the FastAPI REST API.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Docker and Docker Compose (optional)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd building-rest-api-fastapi
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
APP_NAME=FastAPI REST API
DEBUG=True
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Setup Database

Start PostgreSQL database:

```bash
# Using Docker
docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15-alpine

# Or use your local PostgreSQL instance
```

Create database:

```bash
createdb fastapi_db
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Using Docker Compose

For a complete development environment with database:

```bash
docker-compose up
```

This will:
- Start PostgreSQL database
- Start FastAPI application with hot reload
- Expose API on `http://localhost:8000`
- Expose PostgreSQL on `localhost:5432`

## Project Structure

```
building-rest-api-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User database model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          # User Pydantic schemas
│   │   └── token.py         # Token schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   └── users.py         # User CRUD endpoints
│   └── utils/
│       ├── __init__.py
│       └── security.py      # Security utilities (JWT, hashing)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_main.py         # Main app tests
│   ├── test_auth.py         # Authentication tests
│   └── test_users.py        # User endpoint tests
├── examples/
│   └── client.py            # Example API client
├── documentation/
│   ├── API.md               # API documentation
│   ├── DEVELOPMENT.md       # This file
│   └── DEPLOYMENT.md        # Deployment guide
├── .env.example             # Example environment variables
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker Compose configuration
└── README.md                # Project README

```

## Running Tests

### Run all tests:

```bash
pytest
```

### Run with coverage:

```bash
pytest --cov=app tests/
```

### Run specific test file:

```bash
pytest tests/test_auth.py
```

### Run with verbose output:

```bash
pytest -v
```

## Code Quality

### Format code with Black:

```bash
black app/ tests/
```

### Lint with Flake8:

```bash
flake8 app/ tests/
```

### Type checking with MyPy:

```bash
mypy app/
```

## Database Migrations

This project uses SQLAlchemy with auto-initialization. For production, consider using Alembic for migrations:

### Install Alembic:

```bash
pip install alembic
```

### Initialize Alembic:

```bash
alembic init alembic
```

### Create migration:

```bash
alembic revision --autogenerate -m "Initial migration"
```

### Apply migration:

```bash
alembic upgrade head
```

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Common Development Tasks

### Create a new user via API:

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### Login and get token:

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### Access protected endpoint:

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <your-token-here>"
```

## Debugging

### Enable debug mode:

Set `DEBUG=True` in `.env` file.

### View SQL queries:

SQLAlchemy will echo all SQL queries when debug mode is enabled.

### Use Python debugger:

```python
import pdb; pdb.set_trace()
```

Or use VS Code debugger with this launch configuration:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

## Adding New Features

### 1. Create a new model:

Add to `app/models/`:

```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
```

### 2. Create schemas:

Add to `app/schemas/`:

```python
from pydantic import BaseModel

class MyModelBase(BaseModel):
    name: str

class MyModelCreate(MyModelBase):
    pass

class MyModel(MyModelBase):
    id: int

    class Config:
        from_attributes = True
```

### 3. Create router:

Add to `app/routers/`:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/mymodel", tags=["mymodel"])

@router.get("/")
async def read_items():
    return {"items": []}
```

### 4. Include router in main app:

In `app/main.py`:

```python
from app.routers import mymodel
app.include_router(mymodel.router)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | FastAPI REST API |
| `APP_VERSION` | Application version | 1.0.0 |
| `DEBUG` | Debug mode | False |
| `DATABASE_URL` | Database connection URL | postgresql+asyncpg://... |
| `SECRET_KEY` | JWT secret key | (must be set) |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `BACKEND_CORS_ORIGINS` | CORS allowed origins | [...] |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

## Troubleshooting

### Database connection errors:

- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify database exists

### Import errors:

- Ensure virtual environment is activated
- Install requirements: `pip install -r requirements.txt`

### Port already in use:

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

## Contributing

1. Create a new branch for your feature
2. Make changes and write tests
3. Ensure all tests pass: `pytest`
4. Format code: `black app/ tests/`
5. Submit a pull request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
