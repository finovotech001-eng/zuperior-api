# CRM API - Complete Documentation

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
   - [Authentication Endpoints](#authentication-endpoints)
   - [User Management](#user-management)
   - [MT5 Accounts](#mt5-accounts)
   - [Deposits](#deposits)
   - [Withdrawals](#withdrawals)
   - [Payment Methods](#payment-methods)
   - [MT5 Transactions](#mt5-transactions)
   - [KYC Verification](#kyc-verification)
4. [Common Workflows](#common-workflows)
5. [Error Handling](#error-handling)
6. [Pagination & Filtering](#pagination--filtering)
7. [Code Examples](#code-examples)

---

## Getting Started

### Base URL

```
Production: https://your-app.onrender.com
Development: http://localhost:8000
```

### API Version

All API endpoints are prefixed with `/api`

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "CRM API"
}
```

---

## Authentication

### Overview

The API uses **JWT (JSON Web Tokens)** for authentication. Each request to protected endpoints requires a valid access token in the `Authorization` header.

### Token Types

1. **Access Token**: Short-lived token (30 minutes) for API requests
2. **Refresh Token**: Long-lived token (7 days) for obtaining new access tokens

### Authentication Flow

1. Register a new user or login with existing credentials
2. Receive `access_token` and `refresh_token`
3. Use `access_token` in the `Authorization` header: `Bearer <access_token>`
4. When access token expires, use `refresh_token` to get a new one

---

## API Endpoints

### Authentication Endpoints

#### 1. Register New User

**Endpoint:** `POST /api/auth/register`

**Description:** Create a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe",
  "phone": "+1234567890",
  "country": "United States",
  "role": "user"
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "clientId": "c1a2b3c4d5e6f7g8h9i0j1k2",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "country": "United States",
  "createdAt": "2025-10-25T12:00:00Z",
  "emailVerified": false,
  "lastLoginAt": null,
  "role": "user",
  "status": "active"
}
```

**Error Responses:**
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Invalid email format or password too short

---

#### 2. Login (Form Data)

**Endpoint:** `POST /api/auth/login`

**Description:** Login with OAuth2 form data (for compatibility with OAuth2 clients)

**Request Body:** (application/x-www-form-urlencoded)
```
username=user@example.com
password=SecurePass123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Incorrect email or password
- `403 Forbidden`: Account is not active

---

#### 3. Login (JSON)

**Endpoint:** `POST /api/auth/login/json`

**Description:** Login with JSON body (recommended for modern applications)

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### 4. Refresh Token

**Endpoint:** `POST /api/auth/refresh`

**Description:** Get a new access token using refresh token

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Note:** The old refresh token is revoked and a new one is issued.

---

#### 5. Logout

**Endpoint:** `POST /api/auth/logout`

**Description:** Revoke refresh token and logout

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

### User Management

#### 1. Get Current User

**Endpoint:** `GET /api/users/me`

**Description:** Get currently authenticated user's profile

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "clientId": "c1a2b3c4d5e6f7g8h9i0j1k2",
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "country": "United States",
  "createdAt": "2025-10-25T12:00:00Z",
  "emailVerified": false,
  "lastLoginAt": "2025-10-25T14:30:00Z",
  "role": "user",
  "status": "active"
}
```

---

#### 2. Update Current User

**Endpoint:** `PUT /api/users/me`

**Description:** Update current user's profile

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "John Smith",
  "phone": "+9876543210",
  "country": "United Kingdom"
}
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "clientId": "c1a2b3c4d5e6f7g8h9i0j1k2",
  "email": "user@example.com",
  "name": "John Smith",
  "phone": "+9876543210",
  "country": "United Kingdom",
  "createdAt": "2025-10-25T12:00:00Z",
  "emailVerified": false,
  "lastLoginAt": "2025-10-25T14:30:00Z",
  "role": "user",
  "status": "active"
}
```

---

### MT5 Accounts

#### 1. List MT5 Accounts

**Endpoint:** `GET /api/mt5-accounts/`

**Description:** Get all MT5 accounts for the current user with pagination

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `per_page` (integer, default: 20): Items per page (max: 100)
- `sort_by` (string, optional): Field to sort by
- `order` (string, default: "desc"): Sort order ("asc" or "desc")
- `search` (string, optional): Search by account ID

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "userId": "550e8400-e29b-41d4-a716-446655440000",
      "accountId": "MT5-12345678",
      "password": "SecurePass123",
      "leverage": 100,
      "createdAt": "2025-10-25T10:00:00Z",
      "updatedAt": "2025-10-25T10:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

#### 2. Get MT5 Account by ID

**Endpoint:** `GET /api/mt5-accounts/{account_id}`

**Description:** Get a specific MT5 account

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "accountId": "MT5-12345678",
  "password": "SecurePass123",
  "leverage": 100,
  "createdAt": "2025-10-25T10:00:00Z",
  "updatedAt": "2025-10-25T10:00:00Z"
}
```

**Error Responses:**
- `404 Not Found`: MT5 account not found
- `403 Forbidden`: Not authorized to access this account

---

#### 3. Create MT5 Account

**Endpoint:** `POST /api/mt5-accounts/`

**Description:** Create a new MT5 account

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "accountId": "MT5-12345678",
  "password": "SecurePass123",
  "leverage": 100
}
```

**Response:** `201 Created`
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "accountId": "MT5-12345678",
  "password": "SecurePass123",
  "leverage": 100,
  "createdAt": "2025-10-25T10:00:00Z",
  "updatedAt": "2025-10-25T10:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: MT5 account ID already exists

---

#### 4. Update MT5 Account

**Endpoint:** `PUT /api/mt5-accounts/{account_id}`

**Description:** Update an existing MT5 account

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "accountId": "MT5-87654321",
  "password": "NewSecurePass456",
  "leverage": 200
}
```

**Response:** `200 OK`
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "accountId": "MT5-87654321",
  "password": "NewSecurePass456",
  "leverage": 200,
  "createdAt": "2025-10-25T10:00:00Z",
  "updatedAt": "2025-10-25T15:30:00Z"
}
```

**Error Responses:**
- `404 Not Found`: MT5 account not found
- `403 Forbidden`: Not authorized to update this account

---

#### 5. Delete MT5 Account

**Endpoint:** `DELETE /api/mt5-accounts/{account_id}`

**Description:** Delete an MT5 account

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found`: MT5 account not found
- `403 Forbidden`: Not authorized to delete this account

---

### Deposits

#### 1. List Deposits

**Endpoint:** `GET /api/deposits/`

**Description:** Get all deposits for the current user with pagination and filtering

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `per_page` (integer, default: 20): Items per page
- `sort_by` (string, optional): Field to sort by
- `order` (string, default: "desc"): Sort order
- `status` (string, optional): Filter by status ("pending", "approved", "rejected")
- `currency` (string, optional): Filter by currency
- `method` (string, optional): Filter by payment method
- `search` (string, optional): Search by transaction hash or external ID

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "d1e2f3g4-h5i6-7890-jklm-nop123456789",
      "userId": "550e8400-e29b-41d4-a716-446655440000",
      "mt5AccountId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "amount": 1000.00,
      "currency": "USD",
      "method": "bank_transfer",
      "paymentMethod": "SWIFT",
      "transactionHash": "TXN123456789",
      "proofFileUrl": "https://example.com/proof.pdf",
      "bankDetails": "Account: 123456789",
      "cryptoAddress": null,
      "depositAddress": null,
      "status": "pending",
      "externalTransactionId": "EXT123456",
      "rejectionReason": null,
      "approvedBy": null,
      "approvedAt": null,
      "rejectedAt": null,
      "processedAt": null,
      "createdAt": "2025-10-25T11:00:00Z",
      "updatedAt": "2025-10-25T11:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

#### 2. Get Deposit by ID

**Endpoint:** `GET /api/deposits/{deposit_id}`

**Description:** Get a specific deposit

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "d1e2f3g4-h5i6-7890-jklm-nop123456789",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "mt5AccountId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "amount": 1000.00,
  "currency": "USD",
  "method": "bank_transfer",
  "paymentMethod": "SWIFT",
  "transactionHash": "TXN123456789",
  "proofFileUrl": "https://example.com/proof.pdf",
  "bankDetails": "Account: 123456789",
  "cryptoAddress": null,
  "depositAddress": null,
  "status": "pending",
  "externalTransactionId": "EXT123456",
  "rejectionReason": null,
  "approvedBy": null,
  "approvedAt": null,
  "rejectedAt": null,
  "processedAt": null,
  "createdAt": "2025-10-25T11:00:00Z",
  "updatedAt": "2025-10-25T11:00:00Z"
}
```

---

#### 3. Create Deposit

**Endpoint:** `POST /api/deposits/`

**Description:** Create a new deposit request

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "mt5AccountId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "amount": 1000.00,
  "currency": "USD",
  "method": "bank_transfer",
  "paymentMethod": "SWIFT",
  "transactionHash": "TXN123456789",
  "proofFileUrl": "https://example.com/proof.pdf",
  "bankDetails": "Account: 123456789"
}
```

**Response:** `201 Created`
```json
{
  "id": "d1e2f3g4-h5i6-7890-jklm-nop123456789",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "mt5AccountId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "amount": 1000.00,
  "currency": "USD",
  "method": "bank_transfer",
  "paymentMethod": "SWIFT",
  "transactionHash": "TXN123456789",
  "proofFileUrl": "https://example.com/proof.pdf",
  "bankDetails": "Account: 123456789",
  "cryptoAddress": null,
  "depositAddress": null,
  "status": "pending",
  "externalTransactionId": null,
  "rejectionReason": null,
  "approvedBy": null,
  "approvedAt": null,
  "rejectedAt": null,
  "processedAt": null,
  "createdAt": "2025-10-25T11:00:00Z",
  "updatedAt": "2025-10-25T11:00:00Z"
}
```

---

#### 4. Update Deposit

**Endpoint:** `PUT /api/deposits/{deposit_id}`

**Description:** Update a deposit (user can only update their own pending deposits)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "amount": 1500.00,
  "transactionHash": "TXN987654321",
  "proofFileUrl": "https://example.com/new-proof.pdf"
}
```

**Response:** `200 OK`

---

#### 5. Delete Deposit

**Endpoint:** `DELETE /api/deposits/{deposit_id}`

**Description:** Delete a deposit (only pending deposits can be deleted)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

### Withdrawals

#### 1. List Withdrawals

**Endpoint:** `GET /api/withdrawals/`

**Description:** Get all withdrawals for the current user with pagination and filtering

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `per_page` (integer, default: 20): Items per page
- `sort_by` (string, optional): Field to sort by
- `order` (string, default: "desc"): Sort order
- `status` (string, optional): Filter by status
- `currency` (string, optional): Filter by currency
- `method` (string, optional): Filter by payment method
- `search` (string, optional): Search by external ID or wallet address

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "w1x2y3z4-a5b6-7890-cdef-ghi123456789",
      "userId": "550e8400-e29b-41d4-a716-446655440000",
      "mt5AccountId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "amount": 500.00,
      "method": "crypto",
      "currency": "USD",
      "bankDetails": null,
      "cryptoAddress": "0x1234567890abcdef",
      "paymentMethod": "USDT",
      "walletAddress": "0x1234567890abcdef",
      "status": "pending",
      "externalTransactionId": null,
      "rejectionReason": null,
      "approvedBy": null,
      "approvedAt": null,
      "rejectedAt": null,
      "processedAt": null,
      "createdAt": "2025-10-25T12:00:00Z",
      "updatedAt": "2025-10-25T12:00:00Z"
    }
  ],
  "total": 3,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

#### 2. Get Withdrawal by ID

**Endpoint:** `GET /api/withdrawals/{withdrawal_id}`

**Description:** Get a specific withdrawal

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

---

#### 3. Create Withdrawal

**Endpoint:** `POST /api/withdrawals/`

**Description:** Create a new withdrawal request

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "mt5AccountId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "amount": 500.00,
  "method": "crypto",
  "currency": "USD",
  "cryptoAddress": "0x1234567890abcdef",
  "paymentMethod": "USDT",
  "walletAddress": "0x1234567890abcdef"
}
```

**Response:** `201 Created`

---

#### 4. Update Withdrawal

**Endpoint:** `PUT /api/withdrawals/{withdrawal_id}`

**Description:** Update a withdrawal (only pending withdrawals)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "amount": 600.00,
  "walletAddress": "0xabcdef1234567890"
}
```

**Response:** `200 OK`

---

#### 5. Delete Withdrawal

**Endpoint:** `DELETE /api/withdrawals/{withdrawal_id}`

**Description:** Delete a withdrawal (only pending withdrawals)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

### Payment Methods

#### 1. List Payment Methods

**Endpoint:** `GET /api/payment-methods/`

**Description:** Get all payment methods for the current user

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`, `per_page`, `sort_by`, `order` (pagination)
- `status` (string): Filter by status
- `currency` (string): Filter by currency
- `network` (string): Filter by network
- `search` (string): Search by address

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "p1m2n3o4-p5q6-7890-rstu-vwx123456789",
      "userId": "550e8400-e29b-41d4-a716-446655440000",
      "address": "TXyz123456789ABCDEFGH",
      "currency": "USDT",
      "network": "TRC20",
      "status": "approved",
      "submittedAt": "2025-10-25T09:00:00Z",
      "approvedAt": "2025-10-25T10:00:00Z",
      "approvedBy": "admin-id",
      "rejectionReason": null,
      "createdAt": "2025-10-25T09:00:00Z",
      "updatedAt": "2025-10-25T10:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

#### 2. Get Payment Method by ID

**Endpoint:** `GET /api/payment-methods/{payment_method_id}`

**Description:** Get a specific payment method

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

---

#### 3. Create Payment Method

**Endpoint:** `POST /api/payment-methods/`

**Description:** Add a new payment method

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "address": "TXyz123456789ABCDEFGH",
  "currency": "USDT",
  "network": "TRC20"
}
```

**Response:** `201 Created`

---

#### 4. Update Payment Method

**Endpoint:** `PUT /api/payment-methods/{payment_method_id}`

**Description:** Update a payment method

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "address": "TNew987654321ZYXWVU",
  "currency": "USDT",
  "network": "ERC20"
}
```

**Response:** `200 OK`

---

#### 5. Delete Payment Method

**Endpoint:** `DELETE /api/payment-methods/{payment_method_id}`

**Description:** Delete a payment method

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

### MT5 Transactions

#### 1. List MT5 Transactions

**Endpoint:** `GET /api/mt5-transactions/`

**Description:** Get all MT5 transactions for current user's accounts

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page`, `per_page`, `sort_by`, `order` (pagination)
- `status` (string): Filter by status
- `type` (string): Filter by transaction type
- `currency` (string): Filter by currency
- `search` (string): Search by comment or transaction ID

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "t1r2a3n4-s5a6-7890-ctio-nab123456789",
      "mt5AccountId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "type": "deposit",
      "amount": 1000.00,
      "currency": "USD",
      "paymentMethod": "bank_transfer",
      "comment": "Initial deposit",
      "status": "completed",
      "transactionId": "MT5TXN123456",
      "depositId": "d1e2f3g4-h5i6-7890-jklm-nop123456789",
      "withdrawalId": null,
      "userId": "550e8400-e29b-41d4-a716-446655440000",
      "processedBy": "admin-id",
      "processedAt": "2025-10-25T11:30:00Z",
      "createdAt": "2025-10-25T11:00:00Z",
      "updatedAt": "2025-10-25T11:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

#### 2. Get MT5 Transaction by ID

**Endpoint:** `GET /api/mt5-transactions/{transaction_id}`

**Description:** Get a specific MT5 transaction

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`

---

#### 3. Create MT5 Transaction

**Endpoint:** `POST /api/mt5-transactions/`

**Description:** Create a new MT5 transaction

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "mt5AccountId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "type": "deposit",
  "amount": 1000.00,
  "currency": "USD",
  "paymentMethod": "bank_transfer",
  "comment": "Initial deposit"
}
```

**Response:** `201 Created`

---

#### 4. Update MT5 Transaction

**Endpoint:** `PUT /api/mt5-transactions/{transaction_id}`

**Description:** Update an MT5 transaction

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "status": "completed",
  "comment": "Updated deposit information"
}
```

**Response:** `200 OK`

---

#### 5. Delete MT5 Transaction

**Endpoint:** `DELETE /api/mt5-transactions/{transaction_id}`

**Description:** Delete an MT5 transaction

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

---

### KYC Verification

#### 1. Get KYC Status

**Endpoint:** `GET /api/kyc/`

**Description:** Get current user's KYC verification status

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "k1y2c3v4-e5r6-7890-ific-ati123456789",
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "isDocumentVerified": false,
  "isAddressVerified": false,
  "verificationStatus": "Pending",
  "documentReference": "DOC123456",
  "addressReference": "ADDR123456",
  "amlReference": null,
  "documentSubmittedAt": "2025-10-25T08:00:00Z",
  "addressSubmittedAt": "2025-10-25T08:00:00Z",
  "rejectionReason": null,
  "createdAt": "2025-10-25T08:00:00Z",
  "updatedAt": "2025-10-25T08:00:00Z"
}
```

---

#### 2. Submit KYC Documents

**Endpoint:** `POST /api/kyc/`

**Description:** Submit KYC verification documents

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "documentReference": "DOC123456",
  "addressReference": "ADDR123456",
  "amlReference": "AML123456"
}
```

**Response:** `201 Created`

---

#### 3. Update KYC Information

**Endpoint:** `PUT /api/kyc/`

**Description:** Update KYC information

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "documentReference": "DOC789012",
  "addressReference": "ADDR789012"
}
```

**Response:** `200 OK`

---

## Common Workflows

### Workflow 1: Complete User Registration and First Deposit

```
1. Register User
   POST /api/auth/register

2. Login
   POST /api/auth/login/json

3. Create MT5 Account
   POST /api/mt5-accounts/
   Body: {
     "accountId": "MT5-12345678",
     "password": "TradingPass123",
     "leverage": 100
   }

4. Submit KYC Documents
   POST /api/kyc/
   Body: {
     "documentReference": "DOC123456",
     "addressReference": "ADDR123456"
   }

5. Create Deposit
   POST /api/deposits/
   Body: {
     "mt5AccountId": "<id-from-step-3>",
     "amount": 1000.00,
     "currency": "USD",
     "method": "bank_transfer"
   }
```

### Workflow 2: Check Account Status

```
1. Login
   POST /api/auth/login/json

2. Get User Profile
   GET /api/users/me

3. Get MT5 Accounts
   GET /api/mt5-accounts/

4. Get KYC Status
   GET /api/kyc/

5. Get Recent Deposits
   GET /api/deposits/?page=1&per_page=10&order=desc
```

### Workflow 3: Request Withdrawal

```
1. Login
   POST /api/auth/login/json

2. List MT5 Accounts
   GET /api/mt5-accounts/

3. Create Withdrawal Request
   POST /api/withdrawals/
   Body: {
     "mt5AccountId": "<account-id>",
     "amount": 500.00,
     "method": "crypto",
     "walletAddress": "0x1234567890abcdef"
   }

4. Check Withdrawal Status
   GET /api/withdrawals/{withdrawal_id}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Resource deleted successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Common Error Scenarios

#### Authentication Errors

```json
{
  "detail": "Could not validate credentials"
}
```
**Solution:** Ensure access token is valid and included in Authorization header

#### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```
**Solution:** Check request body format and field types

#### Resource Not Found

```json
{
  "detail": "MT5 account not found"
}
```
**Solution:** Verify the resource ID exists and belongs to your user

#### Permission Denied

```json
{
  "detail": "Not authorized to access this MT5 account"
}
```
**Solution:** Ensure you're accessing your own resources

---

## Pagination & Filtering

### Pagination Parameters

All list endpoints support pagination:

- `page` (integer, default: 1): Page number (minimum: 1)
- `per_page` (integer, default: 20): Items per page (max: 100)

### Sorting Parameters

- `sort_by` (string): Field name to sort by (e.g., "createdAt", "amount")
- `order` (string): "asc" (ascending) or "desc" (descending)

### Filtering Parameters

Varies by endpoint, common filters include:

- `status`: Filter by status (e.g., "pending", "approved", "rejected")
- `currency`: Filter by currency (e.g., "USD", "EUR")
- `method`: Filter by payment method
- `search`: Full-text search in relevant fields

### Example: Advanced Query

```bash
GET /api/deposits/?page=2&per_page=10&status=approved&currency=USD&order=desc&sort_by=createdAt
```

### Pagination Response Structure

```json
{
  "items": [...],
  "total": 45,
  "page": 2,
  "per_page": 10,
  "total_pages": 5
}
```

---

## Code Examples

### cURL Examples

#### Register and Login

```bash
# Register
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "name": "John Doe"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'

# Save the access_token from response
TOKEN="<your-access-token>"
```

#### Create MT5 Account

```bash
curl -X POST "http://localhost:8000/api/mt5-accounts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "MT5-12345678",
    "password": "TradingPass123",
    "leverage": 100
  }'
```

#### List Deposits with Filters

```bash
curl -X GET "http://localhost:8000/api/deposits/?page=1&per_page=10&status=pending" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "email": "user@example.com",
        "password": "SecurePass123",
        "name": "John Doe"
    }
)
print("Register:", response.json())

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login/json",
    json={
        "email": "user@example.com",
        "password": "SecurePass123"
    }
)
tokens = response.json()
access_token = tokens["access_token"]

# Headers with authorization
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Get user profile
response = requests.get(
    f"{BASE_URL}/api/users/me",
    headers=headers
)
print("User Profile:", response.json())

# Create MT5 Account
response = requests.post(
    f"{BASE_URL}/api/mt5-accounts/",
    headers=headers,
    json={
        "accountId": "MT5-12345678",
        "password": "TradingPass123",
        "leverage": 100
    }
)
mt5_account = response.json()
print("MT5 Account:", mt5_account)

# List MT5 Accounts
response = requests.get(
    f"{BASE_URL}/api/mt5-accounts/",
    headers=headers,
    params={"page": 1, "per_page": 20}
)
print("MT5 Accounts:", response.json())

# Create Deposit
response = requests.post(
    f"{BASE_URL}/api/deposits/",
    headers=headers,
    json={
        "mt5AccountId": mt5_account["id"],
        "amount": 1000.00,
        "currency": "USD",
        "method": "bank_transfer",
        "bankDetails": "Account: 123456789"
    }
)
print("Deposit:", response.json())
```

---

### JavaScript/TypeScript Example

```javascript
const BASE_URL = "http://localhost:8000";

// Register
async function register() {
  const response = await fetch(`${BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "user@example.com",
      password: "SecurePass123",
      name: "John Doe"
    })
  });
  return response.json();
}

// Login
async function login() {
  const response = await fetch(`${BASE_URL}/api/auth/login/json`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "user@example.com",
      password: "SecurePass123"
    })
  });
  const data = await response.json();
  return data.access_token;
}

// Create MT5 Account
async function createMT5Account(token) {
  const response = await fetch(`${BASE_URL}/api/mt5-accounts/`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      accountId: "MT5-12345678",
      password: "TradingPass123",
      leverage: 100
    })
  });
  return response.json();
}

// List MT5 Accounts
async function listMT5Accounts(token) {
  const response = await fetch(
    `${BASE_URL}/api/mt5-accounts/?page=1&per_page=20`,
    {
      headers: { "Authorization": `Bearer ${token}` }
    }
  );
  return response.json();
}

// Usage
(async () => {
  await register();
  const token = await login();
  const mt5Account = await createMT5Account(token);
  const accounts = await listMT5Accounts(token);
  console.log("MT5 Accounts:", accounts);
})();
```

---

### TypeScript with Types

```typescript
interface UserCreate {
  email: string;
  password: string;
  name?: string;
  phone?: string;
  country?: string;
}

interface MT5AccountCreate {
  accountId: string;
  password?: string;
  leverage?: number;
}

interface MT5AccountResponse {
  id: string;
  userId: string;
  accountId: string;
  password: string | null;
  leverage: number | null;
  createdAt: string;
  updatedAt: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

class CRMAPIClient {
  constructor(private baseURL: string, private token?: string) {}

  async register(userData: UserCreate) {
    const response = await fetch(`${this.baseURL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData)
    });
    return response.json();
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await fetch(`${this.baseURL}/api/auth/login/json`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  async createMT5Account(
    accountData: MT5AccountCreate
  ): Promise<MT5AccountResponse> {
    const response = await fetch(`${this.baseURL}/api/mt5-accounts/`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(accountData)
    });
    return response.json();
  }

  async listMT5Accounts(page = 1, perPage = 20) {
    const response = await fetch(
      `${this.baseURL}/api/mt5-accounts/?page=${page}&per_page=${perPage}`,
      {
        headers: { "Authorization": `Bearer ${this.token}` }
      }
    );
    return response.json();
  }
}

// Usage
const client = new CRMAPIClient("http://localhost:8000");
await client.register({
  email: "user@example.com",
  password: "SecurePass123",
  name: "John Doe"
});
await client.login("user@example.com", "SecurePass123");
const account = await client.createMT5Account({
  accountId: "MT5-12345678",
  password: "TradingPass123",
  leverage: 100
});
```

---

## Support

For additional help:
- Interactive API Documentation: `/docs`
- OpenAPI Specification: `/api/openapi.json`
- Health Check: `/health`

---

**API Version:** 1.0  
**Last Updated:** October 2025

