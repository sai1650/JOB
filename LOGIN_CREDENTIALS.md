# 🔐 Login Credentials & Authentication Setup

## Quick Reference

### Default Accounts

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@screening-ai.com` | `Admin123!@#` |
| **Test User** | `test@screening-ai.com` | `Test123!@#` |

## What Was Added

### 1. **Authentication Infrastructure**
- ✅ JWT token-based authentication
- ✅ Password hashing with bcrypt
- ✅ User model and database table
- ✅ User repository for database operations
- ✅ Authentication service for token management

### 2. **API Endpoints**
```
POST   /api/auth/login    → Login with email/password
GET    /api/auth/me       → Get current user info (requires token)
```

### 3. **Files Created/Modified**
- ✅ `.env` - Added JWT and credential configuration
- ✅ `backend/requirements.txt` - Added auth libraries
- ✅ `backend/app/models/user.py` - User model
- ✅ `backend/app/services/auth.py` - Authentication logic
- ✅ `backend/app/repositories/user_repo.py` - User database operations
- ✅ `backend/app/schemas/auth.py` - Request/response schemas
- ✅ `backend/app/api/routes/auth.py` - Login endpoints
- ✅ `backend/app/core/config.py` - JWT configuration
- ✅ `backend/alembic/versions/0002_add_users_table.py` - Database migration
- ✅ `backend/scripts/seed_users.py` - Initialize default users
- ✅ `AUTHENTICATION.md` - Complete authentication guide

## How to Get Started

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Run Migrations
```bash
cd backend
alembic upgrade head
```

### Step 3: Seed Users
```bash
python scripts/seed_users.py
```

### Step 4: Start Backend
```bash
python -m uvicorn app.main:app --reload --port 8000
```

## Testing Login

### Via API
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@screening-ai.com",
    "password": "Admin123!@#"
  }'
```

### Via FastAPI Docs
1. Go to `http://localhost:8000/docs`
2. Find the `/api/auth/login` endpoint
3. Click "Try it out"
4. Enter credentials and click "Execute"

## Frontend Integration (React/TypeScript)

```typescript
// Login request
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@screening-ai.com',
    password: 'Admin123!@#'
  })
});

const data = await response.json();
const token = data.access_token;

// Use token for authenticated requests
const userResponse = await fetch('http://localhost:8000/api/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

## Environment Variables

```env
# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Default Credentials
ADMIN_EMAIL=admin@screening-ai.com
ADMIN_PASSWORD=Admin123!@#
ADMIN_NAME=System Administrator

TEST_USER_EMAIL=test@screening-ai.com
TEST_USER_PASSWORD=Test123!@#
TEST_USER_NAME=Test User
```

## Security Notes

- 🔑 **Change SECRET_KEY** in production environment
- 🔒 Passwords are hashed with bcrypt
- ⏱️ Tokens expire after 30 minutes by default
- 🔐 Use HTTPS in production
- 📝 Each user account is independent with unique email

## Common Issues

**Q: "Invalid email or password" error?**  
A: Make sure you've run `python scripts/seed_users.py` to create the default users.

**Q: "User not found" after running migrations?**  
A: Run `python scripts/seed_users.py` to populate the users table.

**Q: Can't connect to API?**  
A: Ensure the backend is running on `http://localhost:8000`

## Next Steps

1. ✅ Users can now log in with credentials
2. 📋 Frontend can store and send JWT tokens
3. 🔐 Protected endpoints can verify user authentication
4. 👤 User information is available in API responses
