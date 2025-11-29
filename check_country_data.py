from app.core.database import get_db
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def check_country_data():
    db = next(get_db())
    try:
        # Check Country table
        result = db.execute(text("SELECT count(*) FROM \"Country\""))
        count = result.scalar()
        print(f"Rows in 'Country': {count}")
        
        if count > 0:
            result = db.execute(text("SELECT * FROM \"Country\" LIMIT 1"))
            row = result.mappings().first()
            print(f"Sample row from 'Country': {dict(row)}")

    except Exception as e:
        print(f"Error checking data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_country_data()
