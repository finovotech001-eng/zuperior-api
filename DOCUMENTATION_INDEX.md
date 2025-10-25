# CRM API - Documentation Index

Welcome! This document provides an overview of all available documentation for the CRM API.

---

## 📚 Documentation Files

### 1. API_DOCUMENTATION.md
**Comprehensive API User Guide**

Complete reference for all API endpoints with:
- Getting started guide
- Authentication flow
- All endpoints (8 categories):
  - Authentication
  - Users
  - MT5 Accounts (with password & leverage)
  - Deposits
  - Withdrawals
  - Payment Methods
  - MT5 Transactions
  - KYC Verification
- Common workflows
- Error handling
- Pagination & filtering
- Code examples (cURL, Python, JavaScript/TypeScript)

**Who should read this:** Developers integrating with the API, Frontend developers, API users

---

### 2. openapi.json
**OpenAPI 3.1.0 Specification**

Machine-readable API specification including:
- All endpoint definitions
- Request/response schemas
- Authentication schemes
- Error responses
- Example values

**How to use:**
- Import into Postman, Insomnia, or other API clients
- Generate client libraries using OpenAPI Generator
- View in Swagger Editor: https://editor.swagger.io/
- Access live at: `http://localhost:8000/api/openapi.json`

**Who should read this:** API integration tools, automated code generators, API documentation platforms

---

### 3. RENDER_DEPLOYMENT.md
**Complete Render Deployment Guide**

Step-by-step deployment instructions covering:

**Basic Setup:**
- Quick start deployment (5 minutes)
- Build & start commands
- Environment variables
- Database setup

**Advanced Configuration:**
- SSL/TLS (automatic HTTPS)
- Custom domains with DNS setup
- Performance optimization (Gunicorn, workers, connection pooling)
- Monitoring & logging (Render dashboard, Sentry, New Relic)
- Security best practices (CORS, rate limiting, security headers)

**Production Features:**
- Horizontal scaling
- Health checks
- Auto-deploy from Git
- Cron jobs & background tasks
- Redis caching (optional)

**Includes:**
- Pre-deployment checklist
- Post-deployment verification
- Troubleshooting guide
- Common errors and solutions

**Who should read this:** DevOps engineers, System administrators, Deployment teams

---

## 🚀 Quick Links

| Need | Documentation | Location |
|------|---------------|----------|
| **API Reference** | Complete endpoint documentation | `API_DOCUMENTATION.md` |
| **OpenAPI Spec** | Machine-readable API spec | `openapi.json` |
| **Deploy to Render** | Deployment guide | `RENDER_DEPLOYMENT.md` |
| **Interactive Docs** | Swagger UI | `http://localhost:8000/docs` |
| **Alternative Docs** | ReDoc | `http://localhost:8000/redoc` |
| **Quick Start** | Getting started locally | `START_GUIDE.md` |
| **Project README** | Project overview | `README.md` |

---

## 📖 Documentation by Role

### For Frontend Developers
1. Start with `API_DOCUMENTATION.md`
2. Read "Getting Started" and "Authentication" sections
3. Review code examples (JavaScript/TypeScript)
4. Test endpoints using Swagger UI at `/docs`

### For Backend Developers
1. Review `API_DOCUMENTATION.md` for endpoint details
2. Check `openapi.json` for schema definitions
3. Use `START_GUIDE.md` for local development

### For DevOps/Deployment
1. Read `RENDER_DEPLOYMENT.md` from start to finish
2. Follow the deployment checklist
3. Configure monitoring and alerts
4. Set up security best practices

### For API Integration
1. Import `openapi.json` into your API client (Postman, Insomnia)
2. Review `API_DOCUMENTATION.md` for authentication flow
3. Test with code examples
4. Generate client libraries if needed

---

## 🎯 Common Tasks

### Task: First Time API User

```
1. Read API_DOCUMENTATION.md → "Getting Started" section
2. Open http://localhost:8000/docs in browser
3. Try "Register" endpoint
4. Try "Login" endpoint and get token
5. Click "Authorize" button and paste token
6. Test other endpoints
```

### Task: Deploy to Production

```
1. Read RENDER_DEPLOYMENT.md → "Quick Start Deployment"
2. Follow steps 1-4
3. Review "Environment Variables" section
4. Complete "Deployment Checklist"
5. Verify deployment with "Post-Deployment" checks
```

### Task: Integrate API in Application

```
1. Review API_DOCUMENTATION.md → Your language section
2. Copy code examples
3. Implement authentication flow
4. Test with your credentials
5. Build your features
```

### Task: Create MT5 Account with Password & Leverage

```
1. Login to get access token
2. POST /api/mt5-accounts/
   Body: {
     "accountId": "MT5-12345678",
     "password": "TradingPass123",
     "leverage": 100
   }
3. Verify response includes password and leverage fields
```

---

## 🔑 Key Features Documented

### Authentication
- ✅ JWT-based authentication
- ✅ Access & refresh tokens
- ✅ Token refresh flow
- ✅ Logout functionality

### MT5 Accounts
- ✅ Create account with password & leverage
- ✅ Update account details
- ✅ List with pagination
- ✅ Delete account

### Deposits & Withdrawals
- ✅ Create requests
- ✅ Track status
- ✅ Filter by status, currency, method
- ✅ Search functionality

### Payment Methods
- ✅ Add crypto/bank details
- ✅ Approval workflow
- ✅ Multiple payment methods per user

### KYC Verification
- ✅ Submit documents
- ✅ Track verification status
- ✅ Rejection reasons

---

## 📊 API Statistics

| Category | Endpoints | Methods |
|----------|-----------|---------|
| Authentication | 5 | POST |
| Users | 2 | GET, PUT |
| MT5 Accounts | 5 | GET, POST, PUT, DELETE |
| Deposits | 5 | GET, POST, PUT, DELETE |
| Withdrawals | 5 | GET, POST, PUT, DELETE |
| Payment Methods | 5 | GET, POST, PUT, DELETE |
| MT5 Transactions | 5 | GET, POST, PUT, DELETE |
| KYC | 3 | GET, POST, PUT |
| **Total** | **35** | **Multiple** |

---

## 🛠️ Tools & Technologies

### Local Development
- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication

### Production (Render)
- Gunicorn WSGI server
- Uvicorn workers
- Automatic HTTPS
- Health monitoring
- Auto-scaling

### Optional Integrations
- Sentry (Error tracking)
- New Relic (APM)
- Redis (Caching)
- Uptime Robot (Monitoring)

---

## 💡 Tips

1. **Start Local:** Test API locally before deploying
2. **Use Swagger:** Interactive documentation at `/docs` is the fastest way to test
3. **Read Examples:** Code examples in multiple languages help quick integration
4. **Follow Checklist:** Use deployment checklist to ensure nothing is missed
5. **Monitor Logs:** Check Render logs regularly after deployment
6. **Test Everything:** Verify all critical endpoints work after deployment

---

## 📞 Support

- **Documentation Issues:** Check troubleshooting sections
- **API Questions:** Review API_DOCUMENTATION.md
- **Deployment Issues:** See RENDER_DEPLOYMENT.md troubleshooting
- **Local Setup:** Check START_GUIDE.md

---

## 🔄 Updates

- **API Version:** 1.0.0
- **Last Updated:** October 2025
- **OpenAPI Version:** 3.1.0
- **Python Version:** 3.13

---

## ✅ Checklist: Have You Read?

Before starting development:
- [ ] API_DOCUMENTATION.md → Getting Started
- [ ] API_DOCUMENTATION.md → Authentication
- [ ] Tested API at /docs

Before deployment:
- [ ] RENDER_DEPLOYMENT.md → Quick Start
- [ ] RENDER_DEPLOYMENT.md → Environment Variables
- [ ] RENDER_DEPLOYMENT.md → Deployment Checklist

Before production:
- [ ] RENDER_DEPLOYMENT.md → Security Best Practices
- [ ] RENDER_DEPLOYMENT.md → Monitoring & Logging
- [ ] All tests passing

---

**Ready to get started?** Open `API_DOCUMENTATION.md` or `RENDER_DEPLOYMENT.md` based on your needs!

**Need quick access?** Visit `http://localhost:8000/docs` for interactive API documentation.

