# 🎯 Quick Reference - Login & Launch

## ✅ Credentials Ready to Use

```
┌─────────────────────────────────────────┐
│  ADMIN ACCOUNT                          │
├─────────────────────────────────────────┤
│  Email:    admin@screening-ai.com       │
│  Password: Admin123!@#                  │
│  Role:     Administrator                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  TEST USER ACCOUNT                      │
├─────────────────────────────────────────┤
│  Email:    test@screening-ai.com        │
│  Password: Test123!@#                   │
│  Role:     Regular User                 │
└─────────────────────────────────────────┘
```

---

## 🚀 3-Step Launch

### Terminal 1: Start Backend
```powershell
cd C:\Users\gadda\OneDrive\Desktop\job\candidate-screening-ai
.\start_backend.bat
```
✅ Backend runs at: http://localhost:8000

### Terminal 2: Start Frontend  
```powershell
cd C:\Users\gadda\OneDrive\Desktop\job\candidate-screening-ai\frontend
npm install  # First time only
npm run dev
```
✅ Frontend runs at: http://localhost:5173

### Browser: Test API
Visit: http://localhost:8000/docs
- Click "Try it out" on `/api/auth/login`
- Enter credentials above
- Copy the `access_token` from response

---

## 🔗 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend** | http://localhost:8000 | API server |
| **API Docs** | http://localhost:8000/docs | Swagger UI - test endpoints |
| **API ReDoc** | http://localhost:8000/redoc | ReDoc documentation |
| **Frontend** | http://localhost:5173 | React app |
| **Health** | http://localhost:8000/api/health | Server status |

---

## 📁 Key Files

| File | Location | Purpose |
|------|----------|---------|
| **Credentials** | `.env` | JWT & user config |
| **Database** | `backend/candidate_db.db` | SQLite (auto-created) |
| **Login Endpoint** | `backend/app/api/routes/auth.py` | Authentication logic |
| **User Model** | `backend/app/models/user.py` | Database schema |
| **Test Script** | `backend/test_login.py` | Verify credentials |

---

## 🧪 Test Credentials Anytime

```powershell
cd C:\Users\gadda\OneDrive\Desktop\job\candidate-screening-ai\backend
python test_login.py
```

Expected output:
```
✅ Admin login: SUCCESS
✅ Test user login: SUCCESS
```

---

## 🌐 Frontend Integration (Next Step)

**File:** `frontend/src/services/api.ts`

```typescript
// Login function
async function login(email: string, password: string) {
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  return data.user;
}

// Use token for authenticated requests
async function getCurrentUser() {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:8000/api/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

---

## 📊 System Status

- ✅ Database: SQLite (ready)
- ✅ Authentication: JWT with bcrypt (configured)
- ✅ Users: Admin + Test user (created)
- ✅ Backend: FastAPI app (ready)
- ✅ Frontend: React/TypeScript (ready)
- ✅ API Documentation: Swagger UI (ready)

---

## ⚠️ Remember

1. **Always start backend BEFORE testing login**
2. **Token expires in 30 minutes** (configurable in `.env`)
3. **Change SECRET_KEY before production**
4. **Use HTTPS in production, not HTTP**
5. **Store token in browser localStorage or cookie**

---

## 🎉 You're Ready!

Everything is set up. Just run the 3-step launch above and you're good to go!

For detailed docs, see:
- `SETUP_AND_LAUNCH.md` - Complete setup guide
- `AUTHENTICATION.md` - Auth documentation  
- `LOGIN_CREDENTIALS.md` - Credentials reference
