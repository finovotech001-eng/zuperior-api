from app.core.database import get_db
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def activate_groups():
    db = next(get_db())
    try:
        print("Activating all groups in group_management...")
        result = db.execute(text("UPDATE group_management SET is_active = true"))
        db.commit()
        print(f"Updated {result.rowcount} rows.")
    except Exception as e:
        print(f"Error activating groups: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    activate_groups()
