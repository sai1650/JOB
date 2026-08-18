# Authentication Setup Guide

## Overview

The Candidate Screening AI backend now includes JWT-based authentication. Users must log in to access protected endpoints.

## Default Credentials

After running the database migration and seed script, the following default credentials are available:

### Admin User
- **Email**: `admin@screening-ai.com`
- **Password**: `Admin123!@#`
- **Role**: Administrator

### Test User
- **Email**: `test@screening-ai.com`
- **Password**: `Test123!@#`
- **Role**: Regular User

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file in the project root:

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_EMAIL=admin@screening-ai.com
ADMIN_PASSWORD=Admin123!@#
TEST_USER_EMAIL=test@screening-ai.com
TEST_USER_PASSWORD=Test123!@#
```

⚠️ **IMPORTANT**: Change the `SECRET_KEY` in production!

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Seed Default Users

```bash
python scripts/seed_users.py
```

You should see output like:
```
✓ Created admin user: admin@screening-ai.com
✓ Created test user: test@screening-ai.com

✓ Database seeding completed successfully!

Login credentials:
  Admin: admin@screening-ai.com / Admin123!@#
  Test:  test@screening-ai.com / Test123!@#
```

## API Endpoints

### Login

**Endpoint**: `POST /api/auth/login`

**Request Body**:
```json
{
  "email": "admin@screening-ai.com",
  "password": "Admin123!@#"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-id-here",
    "name": "System Administrator",
    "email": "admin@screening-ai.com",
    "is_admin": true,
    "is_active": true
  }
}
```

### Get Current User

**Endpoint**: `GET /api/auth/me`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "id": "user-id-here",
  "name": "System Administrator",
  "email": "admin@screening-ai.com",
  "is_admin": true,
  "is_active": true
}
```

## Using Tokens

All protected endpoints require the `Authorization` header with a Bearer token:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Testing with cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@screening-ai.com",
    "password": "Admin123!@#"
  }'

# Get current user (replace TOKEN with actual token)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

## Testing with Postman

1. Login endpoint returns access token
2. Copy the `access_token` value
3. In Postman, set Authorization type to "Bearer Token"
4. Paste the token
5. Make requests to protected endpoints

## Password Security

- Passwords are hashed using bcrypt
- Tokens expire after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Always use HTTPS in production
- Change default credentials in production environments

## Adding New Users

Use the `UserRepository` to programmatically add users:

```python
from app.db.session import SessionLocal
from app.repositories.user_repo import UserRepository

db = SessionLocal()
repo = UserRepository(db)

new_user = repo.create(
    name="John Doe",
    email="john@example.com",
    password="SecurePassword123!",
    is_admin=False
)

db.close()
```

## Security Checklist

- [ ] Change `SECRET_KEY` in `.env` for production
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS in production
- [ ] Use strong, unique passwords for default accounts
- [ ] Regularly rotate access tokens
- [ ] Monitor authentication logs
- [ ] Implement rate limiting on login endpoint
