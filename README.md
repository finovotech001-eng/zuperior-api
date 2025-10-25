# CRM API - FastAPI Backend

A fully-featured FastAPI backend with JWT authentication, role-based access control (RBAC), and complete CRUD operations for CRM management.

## Features

- **JWT Authentication** with access and refresh tokens
- **Role-Based Access Control (RBAC)** - User and Admin roles
- **Complete CRUD Operations** for:
  - Users (Profile Management)
  - MT5 Accounts
  - MT5 Transactions
  - Deposits
  - Withdrawals
  - KYC (Know Your Customer)
  - Payment Methods
- **Advanced Query Features**:
  - Pagination
  - Filtering by multiple fields
  - Sorting (ascending/descending)
  - Full-text search
- **Security**:
  - Password hashing with bcrypt
  - Token expiration and refresh
  - User data isolation (users can only access their own data)
  - SQL injection prevention via SQLAlchemy ORM

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Database
- **Pydantic** - Data validation
- **Python-Jose** - JWT token handling
- **Passlib** - Password hashing

## Prerequisites

- Python 3.8+
- PostgreSQL database
- pip or poetry for package management

## Installation

1. **Clone the repository**

```bash
cd CRMApiS
```

2. **Create a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r app/requirements.txt
```

4. **Set up environment variables**

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials and secret key:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/crm_db
SECRET_KEY=your-super-secret-key-here
```

5. **Initialize the database**

The application will automatically create tables on first run. Ensure your PostgreSQL database exists:

```sql
CREATE DATABASE crm_db;
```

## Running the Application

### Development Mode

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:

```bash
python app/main.py
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (form-data)
- `POST /api/auth/login/json` - Login (JSON)
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout and revoke refresh token

### Users

- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update current user profile
- `GET /api/users/{user_id}` - Get user by ID

### MT5 Accounts

- `GET /api/mt5-accounts/` - List MT5 accounts (with pagination)
- `GET /api/mt5-accounts/{id}` - Get MT5 account by ID
- `POST /api/mt5-accounts/` - Create MT5 account
- `PUT /api/mt5-accounts/{id}` - Update MT5 account
- `DELETE /api/mt5-accounts/{id}` - Delete MT5 account

### MT5 Transactions

- `GET /api/mt5-transactions/` - List transactions (with filters)
- `GET /api/mt5-transactions/{id}` - Get transaction by ID
- `POST /api/mt5-transactions/` - Create transaction
- `PUT /api/mt5-transactions/{id}` - Update transaction
- `DELETE /api/mt5-transactions/{id}` - Delete transaction

### Deposits

- `GET /api/deposits/` - List deposits (with filters)
- `GET /api/deposits/{id}` - Get deposit by ID
- `POST /api/deposits/` - Create deposit
- `PUT /api/deposits/{id}` - Update deposit
- `DELETE /api/deposits/{id}` - Delete deposit

### Withdrawals

- `GET /api/withdrawals/` - List withdrawals (with filters)
- `GET /api/withdrawals/{id}` - Get withdrawal by ID
- `POST /api/withdrawals/` - Create withdrawal
- `PUT /api/withdrawals/{id}` - Update withdrawal
- `DELETE /api/withdrawals/{id}` - Delete withdrawal

### KYC

- `GET /api/kyc/` - Get KYC for current user
- `POST /api/kyc/` - Create/Submit KYC
- `PUT /api/kyc/` - Update KYC
- `DELETE /api/kyc/` - Delete KYC

### Payment Methods

- `GET /api/payment-methods/` - List payment methods (with filters)
- `GET /api/payment-methods/{id}` - Get payment method by ID
- `POST /api/payment-methods/` - Create payment method
- `PUT /api/payment-methods/{id}` - Update payment method
- `DELETE /api/payment-methods/{id}` - Delete payment method

## Query Parameters

Most list endpoints support the following query parameters:

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20, max: 100)
- `sort_by` - Field to sort by (e.g., "createdAt")
- `order` - Sort order: "asc" or "desc" (default: "desc")
- `search` - Search term for text fields
- `status` - Filter by status
- `currency` - Filter by currency
- `method` - Filter by method
- `type` - Filter by type

Example:
```
GET /api/deposits/?page=1&per_page=10&sort_by=createdAt&order=desc&status=pending&currency=USD
```

## Authentication Flow

1. **Register**: Create a new user account
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "name": "John Doe"
  }'
```

2. **Login**: Get access and refresh tokens
```bash
curl -X POST "http://localhost:8000/api/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

3. **Use Access Token**: Include in Authorization header
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

4. **Refresh Token**: Get new access token when expired
```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

## Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **JWT Tokens**: 
  - Access tokens expire after 30 minutes (configurable)
  - Refresh tokens expire after 7 days (configurable)
- **Token Revocation**: Refresh tokens can be revoked on logout
- **User Isolation**: Users can only access their own data
- **HTTPS Ready**: Enable HTTPS in production for secure token transmission

## Project Structure

```
app/
├── core/
│   ├── config.py          # Settings & environment variables
│   ├── security.py        # JWT, password hashing
│   └── database.py        # SQLAlchemy setup
├── models/
│   └── models.py          # SQLAlchemy ORM models
├── schemas/
│   └── schemas.py         # Pydantic validation schemas
├── crud/
│   └── crud.py            # CRUD operations
├── api/
│   ├── deps.py            # Dependencies (auth, db)
│   ├── auth.py            # Auth endpoints
│   └── endpoints/         # API endpoints
├── middleware/
│   └── rbac.py            # Role-based access control
├── main.py                # App initialization
└── requirements.txt       # Python dependencies
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | Required |
| SECRET_KEY | Secret key for JWT signing | Required |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token expiry | 30 |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token expiry | 7 |
| API_V1_STR | API prefix | /api |
| PROJECT_NAME | Project name | CRM API |

## Development

### Database Migrations

If you need to modify the database schema:

1. Update the models in `app/models/models.py`
2. Consider using Alembic for migrations in production:

```bash
pip install alembic
alembic init alembic
# Configure alembic.ini and env.py
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Testing

Create a test user for development:

```python
# In Python shell or script
from app.core.database import SessionLocal
from app.crud.crud import user_crud
from app.schemas.schemas import UserCreate
from app.core.security import get_password_hash

db = SessionLocal()
user = user_crud.create(db, obj_in=UserCreate(
    email="test@example.com",
    password="testpassword123",
    name="Test User",
    role="user"
))
```

## Production Deployment

1. **Use environment variables** for sensitive configuration
2. **Enable HTTPS** with reverse proxy (nginx, Caddy)
3. **Use production ASGI server** (uvicorn with workers)
4. **Set strong SECRET_KEY** (generate with `openssl rand -hex 32`)
5. **Configure CORS** properly for your frontend domain
6. **Set up database backups**
7. **Monitor logs and errors**
8. **Use connection pooling** for database

Example production command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

## Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL format: `postgresql://user:password@host:port/database`
- Ensure database exists

### Import Errors
- Activate virtual environment
- Install all requirements: `pip install -r app/requirements.txt`

### Token Errors
- Ensure SECRET_KEY is set in .env
- Check token hasn't expired
- Verify token format in Authorization header: `Bearer <token>`

## License

This project is provided as-is for educational and commercial use.

## Support

For issues and questions, please create an issue in the repository.



