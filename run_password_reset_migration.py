#!/usr/bin/env python3
"""
Script to run password reset migration directly on the database
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent / "app"))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Run the password reset migration"""
    print("Connecting to database...")
    print(f"Database URL: {settings.DATABASE_URL[:50]}...")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("\n1. Adding resetToken column...")
                conn.execute(text("""
                    ALTER TABLE "User" 
                    ADD COLUMN IF NOT EXISTS "resetToken" TEXT;
                """))
                print("   ✓ resetToken column added")
                
                print("\n2. Adding resetTokenExpires column...")
                conn.execute(text("""
                    ALTER TABLE "User" 
                    ADD COLUMN IF NOT EXISTS "resetTokenExpires" TIMESTAMP(3);
                """))
                print("   ✓ resetTokenExpires column added")
                
                print("\n3. Creating index on resetToken...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS "idx_user_reset_token" 
                    ON "User"("resetToken");
                """))
                print("   ✓ Index created")
                
                # Commit transaction
                trans.commit()
                print("\n✅ Migration completed successfully!")
                
            except Exception as e:
                trans.rollback()
                print(f"\n❌ Error during migration: {e}")
                raise
                
    except Exception as e:
        print(f"\n❌ Failed to connect to database: {e}")
        print("\nPlease check:")
        print("1. DATABASE_URL is set correctly in .env")
        print("2. Database is accessible")
        print("3. You have proper permissions")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()

