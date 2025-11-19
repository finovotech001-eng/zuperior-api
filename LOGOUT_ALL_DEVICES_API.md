# Logout from All Devices API Documentation

## Overview

This document describes how to implement and use the "Logout from All Devices" functionality in the Zuperior API (FastAPI backend). This feature allows users to revoke all active sessions across all devices, providing enhanced security control.

## Table of Contents

1. [Current Implementation](#current-implementation)
2. [API Endpoint](#api-endpoint)
3. [How It Works](#how-it-works)
4. [Enhancing the Implementation](#enhancing-the-implementation)
5. [Active Sessions Endpoint](#active-sessions-endpoint)
6. [Authentication Middleware Enhancement](#authentication-middleware-enhancement)
7. [Usage Examples](#usage-examples)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Current Implementation

The logout from all devices endpoint is already implemented in `app/api/auth.py` at line 607-634.

### Endpoint Details

- **URL**: `/api/auth/logout-all`
- **Method**: `POST`
- **Authentication**: Required (Bearer Token)
- **Response**: JSON with success message and count of revoked sessions

---

## API Endpoint

### Logout from All Devices

Revokes all refresh tokens for the authenticated user, effectively logging them out from all devices.

#### Request

```http
POST /api/auth/logout-all
Authorization: Bearer <access_token>
Content-Type: application/json
```

**No request body required** - The user is identified from the JWT token.

#### Response

**Success (200 OK)**
```json
{
  "message": "Successfully logged out from all devices",
  "sessions_revoked": 3
}
```

**Error Responses**

- **401 Unauthorized**: Invalid or missing access token
  ```json
  {
    "detail": "Could not validate credentials"
  }
  ```

- **403 Forbidden**: User account is inactive
  ```json
  {
    "detail": "Inactive user"
  }
  ```

#### Current Implementation Code

```python
@router.post("/logout-all", status_code=status.HTTP_200_OK)
def logout_all_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout from all devices by revoking all refresh tokens for the current user
    """
    # Get all non-revoked refresh tokens for the user
    active_tokens = db.query(RefreshToken).filter(
        RefreshToken.userId == current_user.id,
        RefreshToken.revoked == False
    ).all()
    
    # Revoke all tokens
    count = 0
    now = datetime.utcnow()
    for token in active_tokens:
        token.lastActivity = now
        token.revoked = True
        count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully logged out from all devices",
        "sessions_revoked": count
    }
```

---

## How It Works

### Token Revocation Flow

1. **User Authentication**: When a user logs in, a refresh token is created and stored in the `RefreshToken` table with:
   - `userId`: Links token to user
   - `token`: The actual refresh token string
   - `revoked`: Boolean flag (False by default)
   - `expiresAt`: Token expiration timestamp
   - `deviceName`, `ipAddress`, `userAgent`: Device information

2. **Logout All Devices**: When called:
   - Finds all non-revoked refresh tokens for the user
   - Sets `revoked = True` for each token
   - Updates `lastActivity` timestamp
   - Commits changes to database

3. **Token Validation**: On subsequent requests:
   - Refresh token endpoint checks if token is revoked
   - Revoked tokens are rejected with 401 Unauthorized
   - Access tokens remain valid until expiration (typically 15-30 minutes)

### Important Notes

- **Access Tokens**: Access tokens (JWT) are stateless and cannot be immediately revoked. They remain valid until expiration.
- **Refresh Tokens**: Refresh tokens are stored in the database and can be revoked immediately.
- **Immediate Effect**: After revoking refresh tokens, users cannot get new access tokens, effectively logging them out.

---

## Enhancing the Implementation

### Option 1: Enhanced Logout All (Recommended)

Add better error handling and null-safe checks:

```python
@router.post("/logout-all", status_code=status.HTTP_200_OK)
def logout_all_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout from all devices by revoking all refresh tokens for the current user
    """
    try:
        # Get all non-revoked, non-expired refresh tokens for the user
        now = datetime.utcnow()
        active_tokens = db.query(RefreshToken).filter(
            RefreshToken.userId == current_user.id,
            RefreshToken.revoked != True,  # Handles None values
            RefreshToken.expiresAt > now  # Only active tokens
        ).all()
        
        # Revoke all tokens
        count = 0
        for token in active_tokens:
            token.lastActivity = now
            token.revoked = True
            count += 1
        
        db.commit()
        
        logger.info(f"Revoked {count} refresh tokens for user {current_user.id}")
        
        return {
            "message": "Successfully logged out from all devices",
            "sessions_revoked": count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error revoking tokens for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout from all devices"
        )
```

### Option 2: Add Response Schema

Create a proper response schema in `app/schemas/schemas.py`:

```python
class LogoutAllResponse(BaseModel):
    message: str
    sessions_revoked: int
```

Then update the endpoint:

```python
@router.post("/logout-all", response_model=LogoutAllResponse, status_code=status.HTTP_200_OK)
def logout_all_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # ... implementation
```

---

## Active Sessions Endpoint

To display currently logged-in devices, create an endpoint to list active sessions.

### Implementation

Add this endpoint to `app/api/auth.py`:

```python
from typing import List
from app.schemas.schemas import ActiveSessionResponse

class ActiveSessionResponse(BaseModel):
    id: str
    device: Optional[str]
    browser: Optional[str]
    ipAddress: Optional[str]
    createdAt: datetime
    lastActivity: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ActiveSessionsResponse(BaseModel):
    success: bool
    data: dict
    count: int

@router.get("/active-sessions", response_model=ActiveSessionsResponse)
def get_active_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all active (non-revoked, non-expired) sessions for the current user
    """
    now = datetime.utcnow()
    
    # Get all non-revoked, non-expired refresh tokens
    active_tokens = db.query(RefreshToken).filter(
        RefreshToken.userId == current_user.id,
        RefreshToken.revoked != True,  # Handles None values
        RefreshToken.expiresAt > now
    ).order_by(RefreshToken.lastActivity.desc()).all()
    
    # Transform to response format
    sessions = []
    for token in active_tokens:
        # Parse device and browser from deviceName
        device = "Desktop"
        browser = "Unknown Browser"
        
        if token.deviceName:
            parts = token.deviceName.split(" - ")
            device = parts[0] if parts else "Desktop"
            browser = parts[1] if len(parts) > 1 else "Unknown Browser"
        elif token.userAgent:
            # Fallback: parse from user agent
            ua = token.userAgent.lower()
            if "mobile" in ua or "android" in ua or "iphone" in ua:
                device = "Mobile"
            elif "tablet" in ua or "ipad" in ua:
                device = "Tablet"
            
            if "chrome" in ua:
                browser = "Chrome"
            elif "firefox" in ua:
                browser = "Firefox"
            elif "safari" in ua:
                browser = "Safari"
            elif "edge" in ua:
                browser = "Edge"
        
        sessions.append({
            "id": token.id,
            "device": device,
            "browser": browser,
            "ipAddress": token.ipAddress,
            "createdAt": token.createdAt or token.lastActivity,
            "lastActivity": token.lastActivity
        })
    
    return {
        "success": True,
        "data": {
            "sessions": sessions
        },
        "count": len(sessions)
    }
```

### Add Schema to schemas.py

```python
class ActiveSession(BaseModel):
    id: str
    device: Optional[str]
    browser: Optional[str]
    ipAddress: Optional[str]
    createdAt: datetime
    lastActivity: datetime

class ActiveSessionsResponse(BaseModel):
    success: bool
    data: dict
    count: int
```

---

## Authentication Middleware Enhancement

To ensure revoked tokens are immediately invalidated, enhance the authentication dependency to check for valid refresh tokens.

### Enhanced get_current_user

Update `app/api/deps.py`:

```python
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current user from JWT token
    Also checks if user has at least one valid refresh token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    if user_id is None or token_type != "access":
        raise credentials_exception
    
    user = user_crud.get_by_id(db, id=user_id)
    if user is None:
        raise credentials_exception
    
    # Check if user has at least one valid (non-revoked, non-expired) refresh token
    # This ensures that if all tokens are revoked via "logout all devices",
    # the access token is also invalidated
    now = datetime.utcnow()
    valid_token_count = db.query(RefreshToken).filter(
        RefreshToken.userId == user.id,
        RefreshToken.revoked != True,  # Handles None values
        RefreshToken.expiresAt > now
    ).count()
    
    if valid_token_count == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
```

**Note**: This adds a database query on every authenticated request. Consider caching or using a more efficient approach for high-traffic applications.

---

## Usage Examples

### Python (requests)

```python
import requests

# Your API base URL
BASE_URL = "http://localhost:8000/api"

# Login to get access token
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={
        "username": "user@example.com",
        "password": "password123"
    }
)
tokens = login_response.json()
access_token = tokens["access_token"]

# Logout from all devices
logout_response = requests.post(
    f"{BASE_URL}/auth/logout-all",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
)

print(logout_response.json())
# Output: {"message": "Successfully logged out from all devices", "sessions_revoked": 3}
```

### JavaScript (fetch)

```javascript
const API_URL = 'http://localhost:8000/api';

// Login
const loginResponse = await fetch(`${API_URL}/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: 'user@example.com',
    password: 'password123'
  })
});

const tokens = await loginResponse.json();
const accessToken = tokens.access_token;

// Logout from all devices
const logoutResponse = await fetch(`${API_URL}/auth/logout-all`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});

const result = await logoutResponse.json();
console.log(result);
// Output: {message: "Successfully logged out from all devices", sessions_revoked: 3}
```

### cURL

```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"

# Extract access_token from response, then:
curl -X POST "http://localhost:8000/api/auth/logout-all" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### React/Next.js Example

```typescript
// services/api.ts
export const logoutAllDevices = async (accessToken: string) => {
  const response = await fetch(`${API_URL}/auth/logout-all`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to logout from all devices');
  }
  
  return await response.json();
};

// Component usage
const handleLogoutAll = async () => {
  try {
    const result = await logoutAllDevices(accessToken);
    console.log(`Revoked ${result.sessions_revoked} sessions`);
    // Clear local storage and redirect to login
    localStorage.clear();
    router.push('/login');
  } catch (error) {
    console.error('Error:', error);
  }
};
```

---

## Testing

### Manual Testing

1. **Login from multiple devices/browsers**:
   ```bash
   # Device 1
   curl -X POST "http://localhost:8000/api/auth/login" \
     -d "username=user@example.com&password=password123"
   
   # Device 2 (different browser or incognito)
   # Login again with same credentials
   ```

2. **Check active sessions**:
   ```bash
   curl -X GET "http://localhost:8000/api/auth/active-sessions" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

3. **Logout from all devices**:
   ```bash
   curl -X POST "http://localhost:8000/api/auth/logout-all" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

4. **Verify tokens are revoked**:
   ```bash
   # Try to refresh token from Device 1
   curl -X POST "http://localhost:8000/api/auth/refresh" \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "DEVICE_1_REFRESH_TOKEN"}'
   # Should return 401 Unauthorized
   ```

### Automated Testing

```python
# tests/test_logout_all.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_logout_all_devices():
    # Login
    login_response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "testpass"}
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # Logout from all devices
    logout_response = client.post(
        "/api/auth/logout-all",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_response.status_code == 200
    result = logout_response.json()
    assert result["sessions_revoked"] >= 1
    
    # Verify refresh token is revoked
    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 401
```

---

## Troubleshooting

### Issue: Sessions still showing after logout-all

**Problem**: Active sessions list still shows devices after calling logout-all.

**Solution**: 
1. Ensure the active sessions endpoint filters by `revoked != True` and `expiresAt > now`
2. Check that the logout-all endpoint is properly setting `revoked = True`
3. Verify database transactions are being committed

### Issue: Access tokens still work after logout-all

**Problem**: Access tokens continue to work for a period after logout-all.

**Explanation**: This is expected behavior. Access tokens (JWT) are stateless and cannot be immediately revoked. They remain valid until expiration (typically 15-30 minutes).

**Solution**: 
- Implement the enhanced `get_current_user` dependency that checks for valid refresh tokens
- This will invalidate access tokens immediately when all refresh tokens are revoked

### Issue: Database query performance

**Problem**: Checking for valid refresh tokens on every request is slow.

**Solutions**:
1. **Cache the check**: Cache the result for a short period (e.g., 30 seconds)
2. **Use Redis**: Store revoked token IDs in Redis for fast lookups
3. **Token blacklist**: Maintain a blacklist of revoked access tokens (requires additional storage)

### Issue: Null values in revoked field

**Problem**: Some tokens have `revoked = None` instead of `False`.

**Solution**: Use `RefreshToken.revoked != True` instead of `RefreshToken.revoked == False` in queries. This handles `None` values correctly.

---

## Security Considerations

1. **Immediate Revocation**: Refresh tokens are revoked immediately, but access tokens remain valid until expiration.

2. **Token Expiration**: Set appropriate expiration times:
   - Access tokens: 15-30 minutes (short-lived)
   - Refresh tokens: 7-30 days (long-lived)

3. **Rate Limiting**: Consider rate limiting the logout-all endpoint to prevent abuse.

4. **Audit Logging**: Log all logout-all actions for security auditing.

5. **Notification**: Consider sending email notifications when logout-all is performed.

---

## Additional Features

### Email Notification on Logout All

Add email notification when user logs out from all devices:

```python
def send_logout_all_notification_task(email: str, name: str, sessions_revoked: int):
    """Send email notification about logout from all devices"""
    # Implementation similar to other email tasks
    pass

@router.post("/logout-all", status_code=status.HTTP_200_OK)
def logout_all_devices(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # ... existing code ...
    
    # Send notification email
    background_tasks.add_task(
        send_logout_all_notification_task,
        current_user.email,
        current_user.name,
        count
    )
    
    return {
        "message": "Successfully logged out from all devices",
        "sessions_revoked": count
    }
```

### Revoke Specific Session

Add endpoint to revoke a specific session:

```python
@router.delete("/sessions/{session_id}", status_code=status.HTTP_200_OK)
def revoke_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Revoke a specific session by session ID"""
    token = db.query(RefreshToken).filter(
        RefreshToken.id == session_id,
        RefreshToken.userId == current_user.id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    token.revoked = True
    token.lastActivity = datetime.utcnow()
    db.commit()
    
    return {"message": "Session revoked successfully"}
```

---

## Summary

The logout from all devices feature is already implemented in the Zuperior API. Key points:

- ✅ Endpoint exists at `/api/auth/logout-all`
- ✅ Revokes all refresh tokens for the user
- ✅ Returns count of revoked sessions
- ⚠️ Access tokens remain valid until expiration (by design)
- 📝 Consider adding active sessions endpoint for better UX
- 🔒 Consider enhancing auth middleware for immediate access token invalidation

For questions or issues, refer to the troubleshooting section or check the implementation in `app/api/auth.py`.

