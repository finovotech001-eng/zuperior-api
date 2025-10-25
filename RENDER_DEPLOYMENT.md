# Render Deployment Guide - CRM API

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Deployment](#quick-start-deployment)
3. [Basic Configuration](#basic-configuration)
4. [Environment Variables](#environment-variables)
5. [Database Setup](#database-setup)
6. [Advanced Configuration](#advanced-configuration)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Custom Domains](#custom-domains)
9. [Performance Optimization](#performance-optimization)
10. [Monitoring & Logging](#monitoring--logging)
11. [Security Best Practices](#security-best-practices)
12. [Deployment Checklist](#deployment-checklist)
13. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying to Render, ensure you have:

- A [Render account](https://render.com/) (free tier available)
- Your code in a Git repository (GitHub, GitLab, or Bitbucket)
- Python 3.13 runtime requirements
- PostgreSQL database (Render provides managed PostgreSQL)

---

## Quick Start Deployment

### Step 1: Connect Your Repository

1. Log in to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your Git repository
4. Select the repository containing your CRM API

### Step 2: Configure Service

| Setting | Value |
|---------|-------|
| **Name** | `crm-api` (or your preferred name) |
| **Region** | Choose closest to your users |
| **Branch** | `main` (or your default branch) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r app/requirements.txt` |
| **Start Command** | `cd app && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT` |

### Step 3: Set Environment Variables

Add these environment variables in the Render dashboard:

```
DATABASE_URL=<your-postgresql-connection-string>
SECRET_KEY=<generate-secure-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
API_V1_STR=/api
PROJECT_NAME=CRM API
BACKEND_CORS_ORIGINS=*
```

### Step 4: Deploy

Click **"Create Web Service"** and Render will:
1. Clone your repository
2. Install dependencies
3. Start your application
4. Provide a public URL (e.g., `https://crm-api.onrender.com`)

---

## Basic Configuration

### Build Command

The build command installs all dependencies:

```bash
pip install -r app/requirements.txt
```

**Important:** Ensure `app/requirements.txt` includes:
```txt
fastapi==0.115.4
uvicorn[standard]==0.32.0
gunicorn==23.0.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.10
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
pydantic==2.10.0
pydantic-settings==2.6.1
python-dotenv==1.0.1
bcrypt==4.2.1
email-validator==2.3.0
```

### Start Command Options

#### Option 1: Production (Recommended)
```bash
cd app && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```
- Uses Gunicorn for process management
- 4 worker processes for handling concurrent requests
- Automatic worker restart on failure

#### Option 2: Development (Not Recommended for Production)
```bash
cd app && uvicorn main:app --host 0.0.0.0 --port $PORT
```
- Single worker process
- Good for testing only

#### Option 3: High Traffic
```bash
cd app && gunicorn main:app --workers 8 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5
```
- More workers for higher concurrency
- Increased timeout for long-running requests
- Keep-alive connections

### Python Version

Render auto-detects Python version from your repository. To specify explicitly:

Create `runtime.txt` in project root:
```txt
python-3.13.1
```

Or use `.python-version`:
```txt
3.13.1
```

---

## Environment Variables

### Required Variables

```bash
# Database - PostgreSQL connection string
DATABASE_URL=postgresql://user:password@host:5432/database

# Security - JWT secret key (MUST be changed in production)
SECRET_KEY=<your-secure-random-key-here>

# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_V1_STR=/api
PROJECT_NAME=CRM API

# CORS - For production, specify allowed origins
BACKEND_CORS_ORIGINS=*
```

### Generating Secure SECRET_KEY

Use one of these methods:

**Method 1: Python**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Method 2: OpenSSL**
```bash
openssl rand -base64 32
```

**Method 3: Online** (use with caution)
- Visit [RandomKeygen](https://randomkeygen.com/)
- Use "CodeIgniter Encryption Keys" or similar

### Setting Environment Variables in Render

1. Go to your Web Service dashboard
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Enter **Key** and **Value**
5. Click **"Save Changes"**

Render will automatically redeploy when environment variables change.

### Production CORS Configuration

For production, replace `*` with specific origins:

```bash
# Single origin
BACKEND_CORS_ORIGINS=https://your-frontend.com

# Multiple origins (JSON array format)
BACKEND_CORS_ORIGINS=["https://your-frontend.com","https://admin.your-frontend.com"]
```

---

## Database Setup

### Option 1: Render PostgreSQL (Recommended)

#### Create Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `crm-db`
   - **Database**: `crm_db`
   - **User**: Auto-generated
   - **Region**: Same as your web service
   - **Plan**: Free (for development) or Paid (for production)

3. Click **"Create Database"**

#### Connect to Web Service

1. Go to your Web Service's **"Environment"** tab
2. Click **"Add Environment Variable"**
3. **Key**: `DATABASE_URL`
4. **Value**: Copy **Internal Database URL** from PostgreSQL dashboard
   ```
   postgresql://user:password@hostname:5432/crm_db
   ```

**Important:** Use **Internal Database URL** (not External) for faster connections within Render's network.

#### Initialize Database

The application automatically creates tables on startup via:
```python
Base.metadata.create_all(bind=engine)
```

To manually initialize:
```bash
# SSH into your web service
cd app
python init_db.py
```

### Option 2: External Database (AWS RDS, etc.)

If using an external PostgreSQL database:

1. Ensure database is accessible from Render's IP addresses
2. Configure security groups to allow connections
3. Use **External Database URL** with SSL:
   ```
   postgresql://user:password@rds-hostname.region.rds.amazonaws.com:5432/crm_db?sslmode=require
   ```

#### Database Connection Pooling

For production, update `app/core/database.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,        # Verify connections before using
    pool_size=10,              # Connection pool size
    max_overflow=20,           # Max overflow connections
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=False                 # Disable SQL logging in production
)
```

### Database Migrations

For schema changes, use Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add password and leverage to MT5Account"

# Apply migration
alembic upgrade head
```

---

## Advanced Configuration

### Health Checks

Render automatically monitors your `/health` endpoint:

**Configuration in Render Dashboard:**
- **Health Check Path**: `/health`
- **Port**: Auto-detected from `$PORT`

The API already includes a health check endpoint:
```python
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "CRM API"}
```

### Auto-Deploy from Git

**Enable Auto-Deploy:**
1. Go to **"Settings"** tab
2. Under **"Build & Deploy"**
3. Enable **"Auto-Deploy"**
4. Select branch (e.g., `main`)

Now every push to the selected branch automatically triggers a deployment.

**Deploy Hooks** (for CI/CD):
```bash
# Trigger deploy via webhook
curl -X POST https://api.render.com/deploy/srv-xxx?key=your-deploy-key
```

### Background Jobs & Cron Jobs

If you need scheduled tasks:

1. Create `cron.py` in `app/` directory:
```python
# app/cron.py
from sqlalchemy.orm import Session
from core.database import SessionLocal
from datetime import datetime, timedelta

def cleanup_expired_tokens():
    """Remove expired refresh tokens"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        db.query(RefreshToken).filter(
            RefreshToken.expiresAt < cutoff
        ).delete()
        db.commit()
        print(f"Cleaned up tokens older than {cutoff}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_expired_tokens()
```

2. Create a **Cron Job** in Render:
   - **Command**: `cd app && python cron.py`
   - **Schedule**: `0 0 * * *` (daily at midnight)

### Instance Types & Scaling

#### Free Tier
- 512 MB RAM
- 0.1 CPU
- Spins down after 15 minutes of inactivity
- Good for: Development, testing

#### Starter ($7/month)
- 512 MB RAM
- 0.5 CPU
- Always on
- Good for: Small production apps

#### Standard ($25/month)
- 2 GB RAM
- 1 CPU
- Good for: Medium traffic

#### Pro ($85/month)
- 4 GB RAM
- 2 CPU
- Good for: High traffic

**Horizontal Scaling:**
For high availability, deploy multiple instances behind a load balancer.

---

## SSL/TLS Configuration

### Automatic HTTPS

Render provides **automatic HTTPS** with Let's Encrypt certificates:
- Enabled by default
- Auto-renewal
- HTTP to HTTPS redirect

Your API is automatically available at:
```
https://your-app.onrender.com
```

### Custom SSL Certificates

For custom domains with your own certificates:

1. Go to **"Settings"** → **"Custom Domains"**
2. Add your domain
3. Choose **"Use my own certificate"**
4. Upload:
   - Certificate file (`.crt`)
   - Private key (`.key`)
   - Certificate chain (optional)

---

## Custom Domains

### Adding a Custom Domain

1. In Render Dashboard, go to **"Settings"** → **"Custom Domains"**
2. Click **"Add Custom Domain"**
3. Enter your domain: `api.yourdomain.com`
4. Render provides DNS records to configure

### DNS Configuration

#### Option A: CNAME (Recommended)
```
Type: CNAME
Name: api
Value: your-app.onrender.com
TTL: 3600
```

#### Option B: A Record (for root domain)
```
Type: A
Name: @
Value: <Render's IP address>
TTL: 3600
```

**Wait for DNS propagation** (can take up to 48 hours, usually within 1 hour)

### Verify Custom Domain

```bash
# Check DNS resolution
nslookup api.yourdomain.com

# Test HTTPS
curl https://api.yourdomain.com/health
```

---

## Performance Optimization

### Gunicorn Configuration

Create `gunicorn.conf.py` in `app/` directory:

```python
# app/gunicorn.conf.py
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "crm_api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload application
preload_app = True
```

Update Start Command:
```bash
cd app && gunicorn main:app -c gunicorn.conf.py
```

### Database Connection Pooling

Optimize database connections in `app/core/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Number of permanent connections
    max_overflow=40,         # Max temporary connections
    pool_timeout=30,         # Timeout waiting for connection
    pool_recycle=1800,       # Recycle connections after 30 min
    pool_pre_ping=True,      # Test connections before use
    echo=False
)
```

### Redis Caching (Optional)

For high-traffic applications, add Redis caching:

1. Add Redis to Render (New + → Redis)
2. Install `redis` package:
```bash
pip install redis
```

3. Configure caching:
```python
# app/core/cache.py
import redis
from core.config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

def cache_get(key):
    return redis_client.get(key)

def cache_set(key, value, expiry=300):
    redis_client.setex(key, expiry, value)
```

### Static File Compression

Enable Gzip compression in FastAPI:

```python
# app/main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## Monitoring & Logging

### Render Dashboard Metrics

Render provides built-in monitoring:
- **CPU Usage**
- **Memory Usage**
- **Response Time**
- **Request Count**
- **Error Rate**

Access via **"Metrics"** tab in your service dashboard.

### Application Logs

View logs in Render Dashboard:
```bash
# In Dashboard → Logs tab
# Or via CLI
render logs -s srv-xxxxx
```

### Structured Logging

Implement structured logging in `app/`:

```python
# app/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger("crm_api")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### External Monitoring Tools

#### Sentry (Error Tracking)

1. Sign up at [sentry.io](https://sentry.io/)
2. Install SDK:
```bash
pip install sentry-sdk[fastapi]
```

3. Configure in `app/main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxxxx@sentry.io/xxxxx",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

#### New Relic (APM)

1. Sign up at [newrelic.com](https://newrelic.com/)
2. Install agent:
```bash
pip install newrelic
```

3. Add to Start Command:
```bash
cd app && newrelic-admin run-program gunicorn main:app -c gunicorn.conf.py
```

#### Uptime Monitoring

Use external services:
- [Uptime Robot](https://uptimerobot.com/) (Free)
- [Pingdom](https://www.pingdom.com/)
- [StatusCake](https://www.statuscake.com/)

Configure to ping `/health` endpoint every 5 minutes.

### Alerts

**Set up in Render Dashboard:**
1. Go to **"Notifications"**
2. Add **Slack**, **Email**, or **Webhook**
3. Configure alerts for:
   - Deploy failures
   - Service crashes
   - High CPU/memory usage

---

## Security Best Practices

### Environment Variable Security

- **Never commit** `.env` files to Git
- **Rotate secrets** regularly (especially `SECRET_KEY`)
- Use **Render's secret management** for sensitive data
- **Audit access** to environment variables

### Database Security

#### Security Groups
For external databases:
- Restrict to Render's IP addresses
- Use SSL/TLS connections (`sslmode=require`)

#### Connection Strings
- Store in environment variables only
- Never log connection strings
- Use read-only users where possible

### CORS Policy

For production, restrict CORS:

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Rate Limiting

Install rate limiting:

```bash
pip install slowapi
```

Configure in `app/main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/auth/login/json")
@limiter.limit("5/minute")
async def login_json(...):
    ...
```

### API Key Management

For service-to-service authentication:

```python
# app/api/deps.py
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key
```

### Security Headers

Add security headers:

```python
# app/middleware/security.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

# In main.py
app.add_middleware(SecurityHeadersMiddleware)
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Code committed to Git repository
- [ ] `requirements.txt` includes all dependencies with versions
- [ ] `.env.example` created (without sensitive values)
- [ ] `.gitignore` includes `.env` and `__pycache__`
- [ ] Database migrations tested locally
- [ ] All tests passing
- [ ] API documentation updated

### Configuration

- [ ] Render Web Service created
- [ ] Build command configured: `pip install -r app/requirements.txt`
- [ ] Start command configured: `cd app && gunicorn ...`
- [ ] Python version specified (if needed)
- [ ] Region selected (close to users)

### Environment Variables

- [ ] `DATABASE_URL` set (with Internal URL if using Render PostgreSQL)
- [ ] `SECRET_KEY` generated and set (strong random value)
- [ ] `ALGORITHM` = `HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` = `30`
- [ ] `REFRESH_TOKEN_EXPIRE_DAYS` = `7`
- [ ] `API_V1_STR` = `/api`
- [ ] `PROJECT_NAME` set
- [ ] `BACKEND_CORS_ORIGINS` configured for production

### Database

- [ ] PostgreSQL database created (Render or external)
- [ ] Database connection tested
- [ ] Tables created/migrated
- [ ] Initial data seeded (if needed)

### Post-Deployment

- [ ] Service deployed successfully
- [ ] Health check endpoint responding: `GET /health`
- [ ] API documentation accessible: `/docs`
- [ ] Authentication working (register/login)
- [ ] Test all critical endpoints
- [ ] Monitor logs for errors
- [ ] Set up monitoring/alerts

### Production Readiness

- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate verified
- [ ] CORS properly configured (not `*`)
- [ ] Rate limiting enabled
- [ ] Error tracking set up (Sentry)
- [ ] Uptime monitoring configured
- [ ] Backup strategy in place
- [ ] Rollback plan documented

---

## Troubleshooting

### Deployment Fails

**Error: Build command failed**
```
Solution: Check build logs for Python/package errors
- Verify requirements.txt syntax
- Ensure all dependencies are available for Python 3.13
- Check for system dependencies (e.g., PostgreSQL drivers)
```

**Error: Start command failed**
```
Solution: Test start command locally
- Verify main.py path
- Check import errors
- Ensure $PORT variable is used
```

### Application Won't Start

**Error: Database connection failed**
```
Solution: Verify DATABASE_URL
- Check database is running
- Verify connection string format
- Test with psql: psql $DATABASE_URL
- Ensure SSL mode is correct
```

**Error: Import errors**
```
Solution: Check Python path and imports
- Verify all files in app/ directory
- Check __init__.py files exist
- Test imports locally
```

### Performance Issues

**Slow response times**
```
Solutions:
- Increase worker count in gunicorn
- Upgrade Render instance type
- Add database connection pooling
- Implement caching (Redis)
- Optimize database queries
```

**High memory usage**
```
Solutions:
- Reduce worker count
- Upgrade instance
- Fix memory leaks
- Implement pagination
```

### Database Issues

**Too many connections**
```
Solution: Configure connection pooling
- Set pool_size and max_overflow
- Use connection recycling
- Close connections properly
```

**Slow queries**
```
Solutions:
- Add database indexes
- Optimize queries
- Use database query logging
- Consider read replicas
```

### SSL/HTTPS Issues

**Mixed content warnings**
```
Solution: Ensure all resources use HTTPS
- Update API URLs to use https://
- Check CORS configuration
- Verify SSL certificate
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 503 Service Unavailable | App not started | Check logs, verify start command |
| 500 Internal Server Error | Application error | Check logs, fix code errors |
| 502 Bad Gateway | App crashed | Check logs, restart service |
| 404 Not Found | Wrong URL/route | Verify endpoint paths |
| 401 Unauthorized | Auth issues | Check token, verify SECRET_KEY |

### Getting Help

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com/
- **API Logs**: Dashboard → Logs
- **Support**: support@render.com (for paid plans)

---

## Additional Resources

### Render CLI

Install Render CLI for command-line management:

```bash
# Install
curl -fsSL https://render.com/install-cli.sh | bash

# Login
render login

# Deploy
render deploy --service your-service-name

# View logs
render logs --service your-service-name --tail
```

### Render Blueprint

Create `render.yaml` for infrastructure as code:

```yaml
services:
  - type: web
    name: crm-api
    runtime: python
    buildCommand: pip install -r app/requirements.txt
    startCommand: cd app && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.1
      - key: DATABASE_URL
        fromDatabase:
          name: crm-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ALGORITHM
        value: HS256

databases:
  - name: crm-db
    databaseName: crm_db
    plan: starter
```

Deploy with:
```bash
render blueprint launch
```

---

**Deployment Complete!** 🚀

Your CRM API is now live on Render. Visit your service URL to access the API documentation at `/docs`.

For production deployments, ensure all security best practices are implemented and monitoring is configured.

**Need Help?** Check the [Troubleshooting](#troubleshooting) section or contact Render support.

