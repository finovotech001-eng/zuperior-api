# Cregis USDT-TRC20 Deposit API Documentation

This document provides comprehensive documentation for using the Cregis cryptocurrency deposit API endpoints for mobile applications.

## Table of Contents

1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Endpoints](#endpoints)
   - [Create Deposit](#1-create-deposit)
   - [Callback Handler](#2-callback-handler)
4. [Request/Response Examples](#requestresponse-examples)
5. [Status Mapping](#status-mapping)
6. [Error Handling](#error-handling)
7. [Testing](#testing)
8. [Security](#security)

## Overview

The Cregis deposit API allows mobile applications to create USDT-TRC20 deposits for MT5 accounts. The backend handles all communication with Cregis payment gateway, keeping API keys secure and out of the mobile app.

### Key Features

- **Secure**: All Cregis API keys are stored on the backend
- **Mobile-First**: Returns QR codes and payment addresses for easy display
- **Automatic**: Automatically credits MT5 balance when payment is confirmed
- **Verified**: Signature verification for all callbacks

## Environment Variables

Before using the API, configure the following environment variables in your `.env` file:

```env
# Cregis Payment Configuration
CREGIS_PAYMENT_PROJECT_ID=1435226128711680
CREGIS_PAYMENT_API_KEY=your_api_key_here
CREGIS_PAYMENT_SECRET=your_secret_here
CREGIS_GATEWAY_URL=https://t-rwwagnvw.cregis.io

# MT5 API Configuration (for crediting balance)
MT5_API_URL=http://your-mt5-api-url.com
MT5_API_TOKEN=your_mt5_api_token_here

# Application Configuration
CLIENT_URL=https://dashboard.zuperior.com
API_V1_STR=/api
```

### Notes

- **Test Mode**: The default `CREGIS_GATEWAY_URL` points to Cregis test environment (`https://t-rwwagnvw.cregis.io`)
- **Production**: For production, update `CREGIS_GATEWAY_URL` to production endpoint
- **IP Whitelisting**: Ensure your server IP is whitelisted in Cregis dashboard

## Endpoints

### 1. Create Deposit

Creates a new Cregis cryptocurrency deposit order for an MT5 account.

**Endpoint:** `POST /api/deposits/cregis-crypto`

**Authentication:** Required (Bearer token)

**Request Body:**

```json
{
  "mt5AccountId": "account-uuid-here",
  "amount": "100.00",
  "currency": "USDT"
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mt5AccountId` | string | Yes | UUID of the MT5 account |
| `amount` | string | Yes | Deposit amount (e.g., "100.00") |
| `currency` | string | Yes | Currency code (e.g., "USDT") |

**Response (201 Created):**

```json
{
  "id": "deposit-uuid-here",
  "amount": "100.00",
  "currency": "USDT",
  "payment_info": [
    {
      "currency": "USDT",
      "network": "TRC20",
      "address": "Txxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "amount": "100.00",
      "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ],
  "expire_time": 1735689600
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Deposit record ID |
| `amount` | string | Deposit amount |
| `currency` | string | Currency code |
| `payment_info` | array | Payment information array |
| `payment_info[].currency` | string | Payment currency |
| `payment_info[].network` | string | Blockchain network (e.g., "TRC20") |
| `payment_info[].address` | string | Crypto address to send funds to |
| `payment_info[].amount` | string | Payment amount |
| `payment_info[].qr_code` | string | Base64 encoded QR code image (data URI) |
| `expire_time` | integer | Unix timestamp when payment expires |

**Error Responses:**

```json
// 400 Bad Request - Invalid amount
{
  "detail": "Invalid amount: Amount must be greater than 0"
}

// 404 Not Found - MT5 account not found
{
  "detail": "MT5 account not found"
}

// 403 Forbidden - Unauthorized access
{
  "detail": "Not authorized to create deposit for this MT5 account"
}

// 500 Internal Server Error - Cregis API error
{
  "detail": "Failed to create Cregis payment order: Cregis API error: IP whitelist error..."
}
```

**cURL Example:**

```bash
curl -X POST "https://api.zuperior.com/api/deposits/cregis-crypto" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mt5AccountId": "account-uuid-here",
    "amount": "100.00",
    "currency": "USDT"
  }'
```

**JavaScript/TypeScript Example:**

```typescript
const createCregisDeposit = async (mt5AccountId: string, amount: string, currency: string = "USDT") => {
  const response = await fetch(`${API_BASE_URL}/api/deposits/cregis-crypto`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      mt5AccountId,
      amount,
      currency,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create deposit');
  }

  return await response.json();
};

// Usage
const depositInfo = await createCregisDeposit(
  'account-uuid-here',
  '100.00',
  'USDT'
);

// Display QR code
const qrCodeDataUri = depositInfo.payment_info[0].qr_code;
// Use qrCodeDataUri as image source
```

**React Native Example:**

```javascript
import React from 'react';
import { View, Image, Text } from 'react-native';

const DepositScreen = ({ depositInfo }) => {
  const paymentInfo = depositInfo.payment_info[0];
  
  return (
    <View>
      <Text>Send {paymentInfo.amount} {paymentInfo.currency}</Text>
      <Text>Network: {paymentInfo.network}</Text>
      <Text>Address: {paymentInfo.address}</Text>
      <Image 
        source={{ uri: paymentInfo.qr_code }} 
        style={{ width: 200, height: 200 }}
      />
      <Text>Expires: {new Date(depositInfo.expire_time * 1000).toLocaleString()}</Text>
    </View>
  );
};
```

### 2. Callback Handler

This endpoint receives payment status updates from Cregis. **Do not call this endpoint directly from your mobile app.** It is a webhook endpoint that Cregis calls automatically.

**Endpoint:** `POST /api/deposits/cregis-callback`

**Authentication:** Not required (signature verification is used instead)

**Callback URL Configuration:**

The callback URL is automatically generated when creating a deposit:
```
https://your-api-domain.com/api/deposits/cregis-callback
```

**Callback Payload (from Cregis):**

```json
{
  "cregis_id": "cregis_payment_id",
  "third_party_id": "order_id_from_deposit",
  "status": "paid",
  "order_amount": "100.00",
  "order_currency": "USDT",
  "received_amount": "100.00",
  "paid_currency": "USDT",
  "tx_hash": "transaction_hash_here",
  "txid": "transaction_hash_here",
  "from_address": "sender_address",
  "to_address": "receiver_address",
  "block_height": 123456,
  "block_time": 1735689600,
  "payment_detail": [
    {
      "receive_amount": "100.00",
      "tx_id": "transaction_hash_here"
    }
  ],
  "sign": "md5_signature_here"
}
```

**What Happens on Callback:**

1. **Signature Verification**: The backend verifies the callback signature
2. **Find Deposit**: Looks up the deposit by `externalTransactionId` (matches `cregis_id` or `third_party_id`)
3. **Status Mapping**: Maps Cregis status to internal deposit status (see [Status Mapping](#status-mapping))
4. **Update Deposit**: Updates deposit record with:
   - New status
   - Transaction hash
   - Deposit address
   - Timestamps (approvedAt/rejectedAt/processedAt)
5. **Update MT5Transaction**: Updates or creates MT5Transaction record
6. **Credit Balance**: If approved, automatically credits MT5 account balance

**Response:**

```json
{
  "success": true,
  "message": "Callback processed successfully",
  "data": {
    "depositId": "deposit-uuid-here",
    "status": "approved"
  }
}
```

## Status Mapping

Cregis payment statuses are automatically mapped to internal deposit statuses:

| Cregis Status | Internal Status | Description |
|---------------|----------------|-------------|
| `paid`, `complete`, `success`, `confirmed` | `approved` → `completed` | Payment confirmed, MT5 balance credited |
| `rejected`, `failed`, `cancelled`, `expired` | `rejected` | Payment rejected or failed |
| Others | `pending` | Payment still processing |

**Status Flow:**

```
pending → approved → completed (when MT5 balance credited)
pending → rejected (if payment fails)
```

## Error Handling

### Common Errors

#### 1. Invalid Amount
```json
{
  "detail": "Invalid amount: Amount must be greater than 0"
}
```
**Solution**: Ensure amount is a valid positive number.

#### 2. MT5 Account Not Found
```json
{
  "detail": "MT5 account not found"
}
```
**Solution**: Verify the `mt5AccountId` exists and belongs to the authenticated user.

#### 3. Cregis API Error - IP Whitelist
```json
{
  "detail": "Failed to create Cregis payment order: IP whitelist error: Your server IP needs to be added to Cregis whitelist..."
}
```
**Solution**: Add your server IP address to the Cregis dashboard whitelist.

#### 4. Cregis API Error - Currency Not Enabled
```json
{
  "detail": "Failed to create Cregis payment order: Cregis API error: Currency not enabled..."
}
```
**Solution**: Contact Cregis support to enable the currency for your project.

#### 5. Invalid Signature (Callback)
```json
{
  "detail": "Invalid signature"
}
```
**Solution**: This error occurs if callback signature verification fails. Check that `CREGIS_PAYMENT_API_KEY` matches your Cregis configuration.

## Testing

### Test Mode

The API uses Cregis test environment by default:
- Gateway URL: `https://t-rwwagnvw.cregis.io`
- Use test API keys from Cregis test dashboard

### Test Deposit Flow

1. **Create Deposit**:
   ```bash
   curl -X POST "http://localhost:8000/api/deposits/cregis-crypto" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "mt5AccountId": "test-account-uuid",
       "amount": "10.00",
       "currency": "USDT"
     }'
   ```

2. **Verify Deposit Created**:
   - Check database for deposit record with status `pending`
   - Verify `externalTransactionId` matches Cregis `order_id`
   - Verify `depositAddress` is populated

3. **Simulate Callback** (for testing):
   ```bash
   curl -X POST "http://localhost:8000/api/deposits/cregis-callback" \
     -H "Content-Type: application/json" \
     -d '{
       "cregis_id": "test_cregis_id",
       "third_party_id": "order_id_from_step_1",
       "status": "paid",
       "order_amount": "10.00",
       "order_currency": "USDT",
       "received_amount": "10.00",
       "tx_hash": "test_transaction_hash",
       "to_address": "test_address",
       "sign": "generated_signature"
     }'
   ```

4. **Verify Results**:
   - Deposit status should be `completed`
   - MT5Transaction status should be `completed`
   - MT5 account balance should be credited

### Manual Testing Checklist

- [ ] Deposit creation returns payment info with QR code
- [ ] Deposit record is created with correct status
- [ ] MT5Transaction record is created
- [ ] Callback updates deposit status correctly
- [ ] Approved deposits credit MT5 balance
- [ ] Rejected deposits do not credit balance
- [ ] Signature verification works on callbacks

## Security

### Authentication

- **Create Deposit**: Requires valid JWT Bearer token
- **Callback Handler**: No authentication required (uses signature verification)

### Signature Verification

All callbacks from Cregis are verified using MD5 signature:

1. Filter out null/empty values from callback parameters
2. Sort parameters by key alphabetically
3. Create signature string: `api_key + sorted_key_value_pairs`
4. Generate MD5 hash (lowercase hex)
5. Compare with received signature

### Best Practices

1. **Never expose Cregis keys**: All Cregis API keys stay on the backend
2. **Use HTTPS**: Always use HTTPS in production
3. **IP Whitelisting**: Configure IP whitelist in Cregis dashboard
4. **Validate amounts**: Always validate amounts on both client and server
5. **Monitor callbacks**: Log all callbacks for audit purposes
6. **Handle failures**: Implement retry logic for MT5 balance crediting failures

## Database Schema

### Deposit Record

When a deposit is created, the following fields are populated:

| Field | Value | Description |
|-------|-------|-------------|
| `id` | UUID | Unique deposit ID |
| `userId` | UUID | User who created deposit |
| `mt5AccountId` | UUID | MT5 account receiving deposit |
| `amount` | Float | Deposit amount |
| `currency` | String | Currency code (e.g., "USDT") |
| `method` | String | Always "crypto" |
| `paymentMethod` | String | Always "cregis_usdt" |
| `depositAddress` | String | Crypto address from Cregis |
| `externalTransactionId` | String | Cregis order_id (for callback matching) |
| `status` | String | "pending" initially |
| `transactionHash` | String | Set on callback (tx_hash) |
| `approvedAt` | DateTime | Set when status becomes "approved" |
| `rejectedAt` | DateTime | Set when status becomes "rejected" |
| `processedAt` | DateTime | Set when payment is processed |

### MT5Transaction Record

Created alongside deposit:

| Field | Value | Description |
|-------|-------|-------------|
| `type` | String | Always "Deposit" |
| `amount` | Float | Deposit amount |
| `currency` | String | Currency code |
| `status` | String | "pending" → "approved" → "completed" |
| `paymentMethod` | String | "cregis_usdt" |
| `transactionId` | String | Transaction hash (from callback) |
| `depositId` | UUID | Link to deposit record |
| `mt5AccountId` | UUID | MT5 account |
| `userId` | UUID | User ID |
| `processedBy` | String | "cregis_webhook" |
| `processedAt` | DateTime | When MT5 balance was credited |

## Mobile App Integration Guide

### Step 1: Get User's MT5 Accounts

First, fetch the user's MT5 accounts:

```typescript
const getMT5Accounts = async () => {
  const response = await fetch(`${API_BASE_URL}/api/mt5-accounts/`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });
  return await response.json();
};
```

### Step 2: Create Deposit

Create a deposit order:

```typescript
const createDeposit = async (mt5AccountId: string, amount: string) => {
  const response = await fetch(`${API_BASE_URL}/api/deposits/cregis-crypto`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      mt5AccountId,
      amount,
      currency: 'USDT',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};
```

### Step 3: Display Payment Info

Display the payment information to the user:

```typescript
const DepositPaymentScreen = ({ depositInfo }) => {
  const paymentInfo = depositInfo.payment_info[0];
  const expiresAt = new Date(depositInfo.expire_time * 1000);

  return (
    <View>
      <Text>Send {paymentInfo.amount} {paymentInfo.currency}</Text>
      <Text>Network: {paymentInfo.network}</Text>
      <Text>Address: {paymentInfo.address}</Text>
      
      {/* QR Code */}
      <Image 
        source={{ uri: paymentInfo.qr_code }} 
        style={{ width: 250, height: 250 }}
      />
      
      {/* Copy address button */}
      <Button 
        title="Copy Address" 
        onPress={() => Clipboard.setString(paymentInfo.address)}
      />
      
      <Text>Expires: {expiresAt.toLocaleString()}</Text>
      
      {/* Status polling (optional) */}
      <PollDepositStatus depositId={depositInfo.id} />
    </View>
  );
};
```

### Step 4: Poll Deposit Status (Optional)

Poll the deposit status to check if payment is confirmed:

```typescript
const pollDepositStatus = async (depositId: string) => {
  const response = await fetch(`${API_BASE_URL}/api/deposits/${depositId}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });
  
  const deposit = await response.json();
  return deposit.status; // 'pending', 'approved', 'completed', 'rejected'
};

// Poll every 5 seconds
const PollDepositStatus = ({ depositId }) => {
  const [status, setStatus] = useState('pending');

  useEffect(() => {
    const interval = setInterval(async () => {
      const newStatus = await pollDepositStatus(depositId);
      setStatus(newStatus);
      
      if (newStatus === 'completed' || newStatus === 'rejected') {
        clearInterval(interval);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [depositId]);

  return <Text>Status: {status}</Text>;
};
```

## Support

For issues or questions:

1. **Cregis API Issues**: Contact Cregis support or check [Cregis Documentation](https://developer.cregis.com/api-reference)
2. **Backend Issues**: Check server logs for detailed error messages
3. **Integration Issues**: Verify all environment variables are set correctly

## Additional Resources

- [Cregis API Documentation](https://developer.cregis.com/api-reference)
- [Cregis Dashboard](https://dashboard.cregis.com)
- FastAPI Documentation: `/docs` endpoint (Swagger UI)
- API Schema: `/openapi.json`


