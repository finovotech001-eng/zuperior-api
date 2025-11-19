# Forgot Password Implementation

This document describes the forgot password functionality that has been added to the zuperior-api.

## Overview

The forgot password feature allows users to reset their password by:
1. Requesting a password reset via email
2. Receiving a secure reset token via email
3. Using the token to set a new password

## API Endpoints

### 1. Request Password Reset
**Endpoint:** `POST /api/auth/forgot-password`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If an account with that email exists, a password reset link has been sent."
}
```

**Notes:**
- Always returns the same message to prevent email enumeration attacks
- Generates a secure token that expires in 1 hour
- Sends an email with the reset link in the background

### 2. Reset Password
**Endpoint:** `POST /api/auth/reset-password`

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "newPassword": "newSecurePassword123"
}
```

**Response:**
```json
{
  "message": "Password has been reset successfully. You can now login with your new password."
}
```

**Error Response (Invalid/Expired Token):**
```json
{
  "detail": "Invalid or expired reset token"
}
```

## Database Changes

Two new columns have been added to the `User` table:

1. **resetToken** (TEXT, nullable, indexed)
   - Stores the password reset token
   - Cleared after successful password reset

2. **resetTokenExpires** (TIMESTAMP, nullable)
   - Stores the expiration time of the reset token
   - Default expiration: 1 hour from generation

## Migration Steps

### Option 1: Direct SQL Migration
Run the SQL migration file:
```bash
psql -d your_database -f PASSWORD_RESET_MIGRATION.sql
```

### Option 2: Prisma Migration
If using Prisma, update your schema and run:
```bash
npx prisma migrate dev --name add_password_reset_fields
```

The Prisma schema should include:
```prisma
model User {
  ...
  resetToken        String?   @map("resetToken")
  resetTokenExpires DateTime? @map("resetTokenExpires")
  ...
}
```

## Email Configuration

The password reset email includes:
- Branded HTML email template
- Reset link with token
- Security warnings
- 1-hour expiration notice

The reset URL format: `{CLIENT_URL}/reset-password?token={reset_token}`

Make sure `CLIENT_URL` is set correctly in your `.env` file:
```
CLIENT_URL=https://dashboard.zuperior.com
```

## Security Features

1. **Email Enumeration Prevention**: The API always returns the same message regardless of whether the email exists
2. **Token Expiration**: Reset tokens expire after 1 hour
3. **Secure Token Generation**: Uses `secrets.token_urlsafe(32)` for cryptographically secure tokens
4. **Single Use**: Tokens are cleared after successful password reset
5. **Password Hashing**: New passwords are hashed using bcrypt before storage

## Testing

### Test Forgot Password Flow

1. **Request Reset:**
```bash
curl -X POST http://localhost:8000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

2. **Check Email** for the reset link

3. **Reset Password:**
```bash
curl -X POST http://localhost:8000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "token-from-email",
    "newPassword": "newPassword123"
  }'
```

4. **Login with New Password:**
```bash
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "newPassword123"
  }'
```

## Files Modified

1. **app/models/models.py**
   - Added `resetToken` and `resetTokenExpires` fields to User model

2. **app/schemas/schemas.py**
   - Added `ForgotPasswordRequest` schema
   - Added `ResetPasswordRequest` schema
   - Added `MessageResponse` schema

3. **app/core/security.py**
   - Added `generate_password_reset_token()` function

4. **app/api/auth.py**
   - Added `send_password_reset_email_task()` function
   - Added `/forgot-password` endpoint
   - Added `/reset-password` endpoint

## Frontend Integration

The frontend should:

1. **Forgot Password Page:**
   - Form with email input
   - Call `POST /api/auth/forgot-password`
   - Show success message

2. **Reset Password Page:**
   - Extract token from URL query parameter
   - Form with new password input
   - Call `POST /api/auth/reset-password` with token and new password
   - Redirect to login on success

Example reset password page route: `/reset-password?token=...`

## Troubleshooting

### Email Not Sending
- Check SMTP configuration in `.env`
- Verify `CLIENT_URL` is set correctly
- Check application logs for email errors

### Token Invalid/Expired
- Tokens expire after 1 hour
- Tokens are single-use (cleared after reset)
- Request a new reset if token expires

### Database Errors
- Ensure migration has been run
- Verify columns exist: `resetToken`, `resetTokenExpires`
- Check database connection

