from app.core.database import get_db
from app.models.models import Country
from sqlalchemy.orm import Session
import logging

# Configure logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def seed_countries():
    db = next(get_db())
    try:
        countries_data = [
            {"code": "US", "name": "United States", "phoneCode": "1", "currency": "USD", "region": "Americas"},
            {"code": "GB", "name": "United Kingdom", "phoneCode": "44", "currency": "GBP", "region": "Europe"},
            {"code": "CA", "name": "Canada", "phoneCode": "1", "currency": "CAD", "region": "Americas"},
            {"code": "AU", "name": "Australia", "phoneCode": "61", "currency": "AUD", "region": "Oceania"},
            {"code": "IN", "name": "India", "phoneCode": "91", "currency": "INR", "region": "Asia"},
            {"code": "DE", "name": "Germany", "phoneCode": "49", "currency": "EUR", "region": "Europe"},
            {"code": "FR", "name": "France", "phoneCode": "33", "currency": "EUR", "region": "Europe"},
            {"code": "JP", "name": "Japan", "phoneCode": "81", "currency": "JPY", "region": "Asia"},
            {"code": "CN", "name": "China", "phoneCode": "86", "currency": "CNY", "region": "Asia"},
            {"code": "BR", "name": "Brazil", "phoneCode": "55", "currency": "BRL", "region": "Americas"},
            {"code": "AE", "name": "United Arab Emirates", "phoneCode": "971", "currency": "AED", "region": "Asia"},
            {"code": "SG", "name": "Singapore", "phoneCode": "65", "currency": "SGD", "region": "Asia"},
        ]

        print("Seeding countries...")
        count = 0
        for country_data in countries_data:
            # Check if exists
            existing = db.query(Country).filter(Country.code == country_data["code"]).first()
            if not existing:
                country = Country(**country_data)
                db.add(country)
                count += 1
        
        db.commit()
        print(f"Seeded {count} new countries.")

    except Exception as e:
        print(f"Error seeding countries: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_countries()
