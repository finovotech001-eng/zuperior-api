from app.core.database import get_db
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def update_mt5_table():
    db = next(get_db())
    try:
        print("Adding new columns to MT5Account table...")
        
        columns = [
            "balance",
            "equity",
            "credit",
            "margin",
            "marginFree"
        ]
        
        for col in columns:
            try:
                # Check if column exists (PostgreSQL specific)
                check_sql = text(f"SELECT column_name FROM information_schema.columns WHERE table_name='MT5Account' AND column_name='{col}'")
                result = db.execute(check_sql)
                if not result.scalar():
                    print(f"Adding column '{col}'...")
                    # Add column with default value 0.0
                    add_sql = text(f"ALTER TABLE \"MT5Account\" ADD COLUMN \"{col}\" DOUBLE PRECISION DEFAULT 0.0")
                    db.execute(add_sql)
                    print(f"Column '{col}' added.")
                else:
                    print(f"Column '{col}' already exists.")
            except Exception as e:
                print(f"Error adding column '{col}': {e}")
                
        db.commit()
        print("Table update complete.")

    except Exception as e:
        print(f"Error updating table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_mt5_table()
