-- Migration: Add password reset fields to User table
-- Date: 2024
-- Description: Adds resetToken and resetTokenExpires columns to support forgot password functionality

-- Add resetToken column (nullable, indexed for faster lookups)
ALTER TABLE "User" 
ADD COLUMN IF NOT EXISTS "resetToken" TEXT;

-- Add resetTokenExpires column (nullable, stores expiration timestamp)
ALTER TABLE "User" 
ADD COLUMN IF NOT EXISTS "resetTokenExpires" TIMESTAMP(3);

-- Create index on resetToken for faster token lookups during password reset
CREATE INDEX IF NOT EXISTS "idx_user_reset_token" ON "User"("resetToken");

-- Note: If you're using Prisma, you should also update your Prisma schema:
-- model User {
--   ...
--   resetToken        String?   @map("resetToken")
--   resetTokenExpires DateTime? @map("resetTokenExpires")
--   ...
-- }
-- Then run: npx prisma migrate dev --name add_password_reset_fields

