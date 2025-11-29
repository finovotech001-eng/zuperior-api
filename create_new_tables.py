from app.core.database import engine, Base
from app.models.models import Country, GroupManagement
import logging

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def create_tables():
    print("Creating tables for Country and GroupManagement...")
    try:
        Base.metadata.create_all(bind=engine, tables=[Country.__table__, GroupManagement.__table__])
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
