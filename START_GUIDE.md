# 🚀 Quick Start Guide - CRM API

## ✅ Application Status: RUNNING

Your API is currently running at: **http://localhost:8000**

---

## 📍 Important URLs

| Service | URL |
|---------|-----|
| **Swagger API Docs** | http://localhost:8000/docs |
| **ReDoc Documentation** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |
| **API Base** | http://localhost:8000/api |

---

## 🚀 How to Start the Application

### Option 1: Using Batch Script (Recommended)
```bash
.\start.bat
```

### Option 2: Manual PowerShell
```powershell
.\venv\Scripts\Activate.ps1
cd app
python main.py
```

### Option 3: Using start.sh (Linux/Mac)
```bash
./start.sh
```

---

## ⚠️ Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution:** Virtual environment not activated. Always use `.\start.bat` or activate manually:
```powershell
.\venv\Scripts\Activate.ps1
```

### Issue: "Port 8000 already in use"
**Solution:** Kill existing process:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Issue: Database connection error
**Solution:** Check your `.env` file in the `app` folder. Database URL should be:
```
DATABASE_URL=postgresql://postgres:zuperiorPass123@zuperiorcrm.cbqwscegmst5.eu-west-2.rds.amazonaws.com:5432/zuperiorcrm
```

---

## 🔧 MT5Account CRUD with New Fields

### ✅ New Fields Added
- `password` (String, optional)
- `leverage` (Integer, optional)

### Create MT5 Account
```bash
POST /api/mt5-accounts/
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "accountId": "MT5-12345678",
  "password": "SecurePassword123",
  "leverage": 100
}
```

### Update MT5 Account
```bash
PUT /api/mt5-accounts/{id}
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "accountId": "MT5-87654321",
  "password": "NewPassword456",
  "leverage": 200
}
```

### Get MT5 Account (Returns all fields including password & leverage)
```bash
GET /api/mt5-accounts/{id}
Authorization: Bearer <your-token>
```

---

## 🔐 Authentication Flow

### 1. Register New User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword",
  "name": "Your Name"
}
```

### 2. Login
```bash
POST /api/auth/login/json
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

### 3. Use Access Token
Copy the `access_token` from the login response and use it in requests:
```
Authorization: Bearer <access_token>
```

---

## 📊 Database Configuration

**Location:** `D:\CRMApiS\app\.env`

```env
DATABASE_URL=postgresql://postgres:zuperiorPass123@zuperiorcrm.cbqwscegmst5.eu-west-2.rds.amazonaws.com:5432/zuperiorcrm
SECRET_KEY=1mPRpGxA0S3nFUusecMSIwcmag7xSGx4PAHdlhwkoKY
```

✅ **Database Status:** Connected to AWS RDS PostgreSQL 17.4

---

## 🧪 Testing the API

### Option 1: Swagger UI (Easiest)
1. Open: http://localhost:8000/docs
2. Click "Authorize" button
3. Login to get token
4. Test any endpoint interactively

### Option 2: cURL
```bash
# Health check
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Option 3: PowerShell
```powershell
# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Register user
$body = @{email="test@example.com";password="test123";name="Test User"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" -Method Post -Body $body -ContentType "application/json"
```

---

## 📝 Environment Variables

| Variable | Description | Current Value |
|----------|-------------|---------------|
| `DATABASE_URL` | PostgreSQL connection string | AWS RDS (configured) |
| `SECRET_KEY` | JWT secret key | Generated secure key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | 30 minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | 7 days |
| `API_V1_STR` | API prefix | /api |

---

## 🎯 Next Steps

1. ✅ Application is running
2. ✅ Database is connected
3. ✅ MT5Account has password & leverage fields
4. 👉 **Visit http://localhost:8000/docs to start using the API!**

---

## 💡 Tips

- Always use `.\start.bat` to ensure virtual environment is activated
- Use Swagger UI at `/docs` for easy API testing
- Check `/health` endpoint to verify server is running
- Tokens expire after 30 minutes - use refresh token to get new access token

---

## 🆘 Need Help?

- Check logs in terminal where you started the app
- Visit `/docs` for interactive API documentation
- Test `/health` endpoint to verify server status
- Ensure virtual environment is activated before running Python commands

---

**🎉 Your CRM API is ready to use! Happy coding!**

