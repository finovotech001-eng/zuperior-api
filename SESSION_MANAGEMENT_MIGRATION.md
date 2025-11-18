# Session Management Database Migration

## Overview
This migration adds device tracking and session management features to the RefreshToken table.

## Changes Made

### Prisma Schema Updated
The `RefreshToken` model has been updated in `app/prisma db schema` with the following new fields:

- `deviceName` (String, nullable) - Device identifier/name
- `ipAddress` (String, nullable) - Client IP address  
- `userAgent` (String, nullable) - Browser/client user agent
- `lastActivity` (DateTime, nullable, default now()) - Last activity timestamp
- Added index on `lastActivity` for performance
- Added `@default(uuid())` to `id` field for consistency

## Migration Steps

### Option 1: Using Prisma Migrate (Recommended)
```bash
# Generate migration
npx prisma migrate dev --name add_session_tracking_fields

# Or if using Prisma CLI directly
prisma migrate dev --name add_session_tracking_fields
```

### Option 2: Manual SQL Migration
If you need to apply the changes manually, run this SQL:

```sql
-- Add new columns to RefreshToken table
ALTER TABLE "RefreshToken" 
ADD COLUMN IF NOT EXISTS "deviceName" VARCHAR,
ADD COLUMN IF NOT EXISTS "ipAddress" VARCHAR,
ADD COLUMN IF NOT EXISTS "userAgent" VARCHAR,
ADD COLUMN IF NOT EXISTS "lastActivity" TIMESTAMPTZ(6) DEFAULT NOW();

-- Create index on lastActivity for performance
CREATE INDEX IF NOT EXISTS "ix_RefreshToken_lastActivity" ON "RefreshToken"("lastActivity");

-- Update existing records to set lastActivity = createdAt (if needed)
UPDATE "RefreshToken" 
SET "lastActivity" = "createdAt" 
WHERE "lastActivity" IS NULL AND "createdAt" IS NOT NULL;
```

## Verification

After migration, verify the changes:
```sql
-- Check columns exist
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'RefreshToken' 
AND column_name IN ('deviceName', 'ipAddress', 'userAgent', 'lastActivity');

-- Check index exists
SELECT indexname 
FROM pg_indexes 
WHERE tablename = 'RefreshToken' 
AND indexname = 'ix_RefreshToken_lastActivity';
```

## Notes

- All new fields are nullable to maintain backward compatibility
- Existing refresh tokens will have NULL values for new fields (this is expected)
- New tokens created after migration will have device info populated
- The `lastActivity` field will default to `now()` for new records

