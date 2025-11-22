"""
Script to fix existing RefreshToken records that have revoked=None
This sets revoked=False for all tokens that are currently NULL
"""
from app.core.database import SessionLocal
from app.models.models import RefreshToken
from sqlalchemy import or_

def fix_revoked_tokens():
    """
    Update all RefreshToken records where revoked is None to False
    """
    db = SessionLocal()
    try:
        # Find all tokens where revoked is None
        tokens_to_fix = db.query(RefreshToken).filter(
            RefreshToken.revoked.is_(None)
        ).all()
        
        count = 0
        for token in tokens_to_fix:
            token.revoked = False
            count += 1
        
        db.commit()
        print(f"✅ Fixed {count} RefreshToken records (set revoked=None to revoked=False)")
        
        # Verify fix
        remaining_null = db.query(RefreshToken).filter(
            RefreshToken.revoked.is_(None)
        ).count()
        
        if remaining_null == 0:
            print("✅ Verification passed: No tokens with revoked=None remain")
        else:
            print(f"⚠️  Warning: {remaining_null} tokens still have revoked=None")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error fixing tokens: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting RefreshToken fix...")
    fix_revoked_tokens()
    print("Done!")





