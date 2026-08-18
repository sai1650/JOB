# 🚀 Complete Setup & Launch Guide

## ✅ Setup Status

All authentication is configured and ready to use!

**Login Credentials (Verified & Working):**
| Role | Email | Password | Status |
|------|-------|----------|--------|
| Admin | `admin@screening-ai.com` | `Admin123!@#` | ✅ Active |
| Test User | `test@screening-ai.com` | `Test123!@#` | ✅ Active |

---

## 🏃 Quick Start (3 Steps)

### Step 1: Start Backend

**Option A - Auto Start (Recommended)**
```powershell
cd C:\Users\gadda\OneDrive\Desktop\job\candidate-screening-ai
.\start_backend.bat
```

**Option B - Manual Start**
```powershell
cd C:\Users\gadda\OneDrive\Desktop\job\candidate-screening-ai\backend
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Step 2: Start Frontend

Open a new terminal:
```powershell
cd C:\Users\gadda\OneDrive\Desktop\job\candidate-screening-ai\frontend
npm install    # Only needed first time
npm run dev
```

Frontend will be at: `http://localhost:5173`

### Step 3: Test Login

**Via Browser:**
1. Go to `http://localhost:8000/docs` (Swagger UI)
2. Find `/api/auth/login` endpoint
3. Click "Try it out"
4. Enter:
   - email: `admin@screening-ai.com`
   - password: `Admin123!@#`
5. Click "Execute"

**Via cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@screening-ai.com\",\"password\":\"Admin123!@#\"}"
```

---

## 📝 API Documentation

### Login Endpoint
**POST** `/api/auth/login`

**Request:**
```json
{
  "email": "admin@screening-ai.com",
  "password": "Admin123!@#"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-id",
    "name": "System Administrator",
    "email": "admin@screening-ai.com",
    "is_admin": true,
    "is_active": true
  }
}
```

### Get Current User
**GET** `/api/auth/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "user-id",
  "name": "System Administrator",
  "email": "admin@screening-ai.com",
  "is_admin": true,
  "is_active": true
}
```

---

## 🗂️ File Structure

```
candidate-screening-ai/
├── .env                                 ← Configuration & credentials
├── start_backend.bat                    ← Quick start script
├── AUTHENTICATION.md                    ← Detailed auth docs
├── LOGIN_CREDENTIALS.md                 ← Credentials reference
│
├── backend/
│   ├── requirements.txt                 ← Python dependencies
│   ├── test_login.py                   ← Credential test script
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── 0001_create_initial_tables.py
│   │   │   └── 0002_add_users_table.py ← User table migration
│   │   └── env.py
│   ├── app/
│   │   ├── main.py                      ← FastAPI app
│   │   ├── api/routes/
│   │   │   └── auth.py                  ← Login endpoints
│   │   ├── models/
│   │   │   └── user.py                  ← User database model
│   │   ├── schemas/
│   │   │   └── auth.py                  ← Request/response schemas
│   │   ├── services/
│   │   │   └── auth.py                  ← JWT & password logic
│   │   ├── repositories/
│   │   │   └── user_repo.py             ← User database operations
│   │   └── core/
│   │       └── config.py                ← Configuration
│   └── scripts/
│       └── seed_users.py                ← Initialize default users
│
└── frontend/
    ├── src/
    │   ├── App.tsx
    │   ├── main.tsx
    │   └── services/api.ts              ← API client (add auth here)
    └── package.json
```

---

## 🔧 Environment Configuration

**File:** `.env`

```env
# Database (SQLite for local dev)
DATABASE_URL=sqlite:///./candidate_db.db

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend
FRONTEND_PORT=5173

# CORS
CORS_ALLOW_ORIGINS=http://localhost:5173

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Default Admin User
ADMIN_EMAIL=admin@screening-ai.com
ADMIN_PASSWORD=Admin123!@#
ADMIN_NAME=System Administrator

# Test User
TEST_USER_EMAIL=test@screening-ai.com
TEST_USER_PASSWORD=Test123!@#
TEST_USER_NAME=Test User

# AI/LLM
OPENAI_API_KEY=sk-your-actual-key-here
```

---

## 🧪 Testing Credentials

Run the credential test script:
```powershell
cd C:\Users\gadda\OneDrive\Desktop\job\candidate-screening-ai\backend
python test_login.py
```

Expected output:
```
✅ Admin login: SUCCESS
✅ Test user login: SUCCESS
✅ All credentials are valid and ready to use!
```

---

## 🔐 Security Checklist for Production

- [ ] Change `SECRET_KEY` in `.env` to a strong random string
- [ ] Use HTTPS instead of HTTP
- [ ] Disable debug mode in production
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong passwords for admin accounts
- [ ] Enable rate limiting on login endpoint
- [ ] Set up proper logging and monitoring
- [ ] Use environment-specific `.env` files
- [ ] Add CSRF protection if using cookies
- [ ] Implement password reset functionality

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'app'"
- **Cause:** Running uvicorn from wrong directory
- **Fix:** Make sure you're in `backend/` directory before running `python -m uvicorn`

### "Invalid email or password"
- **Cause:** Credentials don't match database
- **Fix:** Run `python test_login.py` to verify, or re-run `python scripts/seed_users.py`

### "Connection refused" on port 8000
- **Cause:** Backend not running
- **Fix:** Start backend with `.\start_backend.bat` or manual uvicorn command

### "Database locked"
- **Cause:** SQLite database is in use
- **Fix:** Close all other Python processes accessing the database

### Can't connect to PostgreSQL
- **Cause:** Docker container not running or PostgreSQL password wrong
- **Fix:** Use SQLite (current setup) or start Docker: `docker-compose up -d db`

---

## 📚 Next Steps

1. **Frontend Integration**
   - Store JWT token from login response
   - Send token in `Authorization: Bearer {token}` header for protected endpoints
   - Implement logout (token expiration)

2. **Protected Endpoints**
   - Add `current_user: User = Depends(get_current_user)` to routes
   - Only authenticated users can access them

3. **Add More Users**
   - Use `/api/auth/register` endpoint (needs implementation)
   - Or add directly via UserRepository

4. **Role-Based Access**
   - Use `is_admin` flag to restrict endpoints
   - Implement permission decorators

---

## 📞 Support

For detailed documentation, see:
- [AUTHENTICATION.md](./AUTHENTICATION.md) - Complete authentication guide
- [LOGIN_CREDENTIALS.md](./LOGIN_CREDENTIALS.md) - Credentials reference

Database: `candidate_db.db` (SQLite - auto-created in backend directory)
