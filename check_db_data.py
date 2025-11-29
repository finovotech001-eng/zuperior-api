from app.core.database import get_db
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def check_data():
    db = next(get_db())
    try:
        with open("db_counts.txt", "w") as f:
            # Check group_management
            result = db.execute(text("SELECT count(*) FROM group_management"))
            count_gm = result.scalar()
            f.write(f"Rows in 'group_management': {count_gm}\n")
            print(f"Rows in 'group_management': {count_gm}")

            # Check mt5_groups
            result = db.execute(text("SELECT count(*) FROM mt5_groups"))
            count_mt5 = result.scalar()
            f.write(f"Rows in 'mt5_groups': {count_mt5}\n")
            print(f"Rows in 'mt5_groups': {count_mt5}")
            
            # Check if there are any rows in group_management, print the first one
            if count_gm > 0:
                result = db.execute(text("SELECT * FROM group_management LIMIT 1"))
                row = result.mappings().first()
                f.write(f"Sample row from 'group_management': {dict(row)}\n")
            
            if count_mt5 > 0:
                result = db.execute(text("SELECT * FROM mt5_groups LIMIT 1"))
                row = result.mappings().first()
                f.write(f"Sample row from 'mt5_groups': {dict(row)}\n")

    except Exception as e:
        with open("db_counts.txt", "w") as f:
            f.write(f"Error checking data: {e}\n")
        print(f"Error checking data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
