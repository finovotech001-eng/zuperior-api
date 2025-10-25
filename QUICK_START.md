# Quick Start Guide

## 1. Prerequisites

- Python 3.8+
- PostgreSQL database
- pip

## 2. Installation (5 minutes)

### Step 1: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r app/requirements.txt
```

### Step 3: Configure Environment

Copy and edit the environment file:

```bash
# Windows
copy app\.env.example app\.env

# Linux/Mac
cp app/.env.example app/.env
```

Edit `app/.env` with your database credentials:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/crm_db
SECRET_KEY=your-secret-key-here
```

### Step 4: Create Database

```sql
CREATE DATABASE crm_db;
```

### Step 5: Initialize Database

```bash
cd app
python init_db.py
```

This will:
- Create all database tables
- Create an admin user
- Optionally create a test user

### Step 6: Start the Server

```bash
# Option 1: Using start script (Windows)
..\start.bat

# Option 2: Using start script (Linux/Mac)
chmod +x ../start.sh
../start.sh

# Option 3: Direct command
python main.py

# Option 4: With uvicorn
uvicorn main:app --reload
```

## 3. Access the API

- **API Base**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 4. Test the API

### Option 1: Using Swagger UI

1. Go to http://localhost:8000/docs
2. Click on "POST /api/auth/login/json"
3. Click "Try it out"
4. Enter credentials:
   ```json
   {
     "email": "test@example.com",
     "password": "test123"
   }
   ```
5. Copy the `access_token` from response
6. Click "Authorize" button at top
7. Enter: `Bearer <your-access-token>`
8. Now you can test all endpoints!

### Option 2: Using Test Script

```bash
# Make sure API is running, then:
cd app
python test_api.py
```

### Option 3: Using cURL

```bash
# Register
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Use the access_token from login response
TOKEN="<your-access-token-here>"

# Get Profile
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

## 5. Common Operations

### Create MT5 Account

```bash
curl -X POST "http://localhost:8000/api/mt5-accounts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "MT5-12345678"
  }'
```

### Create Deposit

```bash
curl -X POST "http://localhost:8000/api/deposits/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mt5AccountId": "<mt5-account-id>",
    "amount": 1000.00,
    "currency": "USD",
    "method": "bank_transfer"
  }'
```

### List Deposits with Filters

```bash
curl -X GET "http://localhost:8000/api/deposits/?page=1&per_page=10&status=pending&currency=USD" \
  -H "Authorization: Bearer $TOKEN"
```

### Submit KYC

```bash
curl -X POST "http://localhost:8000/api/kyc/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documentReference": "DOC-123456",
    "addressReference": "ADDR-123456"
  }'
```

## 6. Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL: database "crm_db" does not exist
```

**Solution**: Create the database first:
```sql
CREATE DATABASE crm_db;
```

### Module Not Found Error

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**: Install dependencies:
```bash
pip install -r app/requirements.txt
```

### Port Already in Use

```
Error: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solution**: Change port or kill the process:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Token Expired

```
{"detail": "Could not validate credentials"}
```

**Solution**: Use refresh token or login again:
```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<your-refresh-token>"
  }'
```

## 7. Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Customize the models in `app/models/models.py`
- Add custom endpoints in `app/api/endpoints/`
- Configure production settings for deployment

## 8. Production Deployment

### Generate Strong Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Run with Gunicorn (Production)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables for Production

```env
DATABASE_URL=postgresql://user:pass@prod-db:5432/crm_db
SECRET_KEY=<strong-secret-key-here>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Support

For issues or questions:
- Check the [README.md](README.md)
- Review API docs at /docs
- Check linter errors: Files should be error-free

## Summary

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r app/requirements.txt

# 2. Configure
cp app/.env.example app/.env
# Edit app/.env with your settings

# 3. Initialize
cd app
python init_db.py

# 4. Run
python main.py

# 5. Test
# Visit http://localhost:8000/docs
```

**That's it! You're ready to go! 🚀**

