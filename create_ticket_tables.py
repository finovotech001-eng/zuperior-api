"""
Script to create Ticket and TicketReply tables in the database
Run this script to add the missing ticket tables
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import engine, Base

def create_ticket_tables():
    """Create Ticket and TicketReply tables"""
    print("Creating Ticket and TicketReply tables...")
    try:
        # Import all models to ensure they're registered with Base
        from app.models import models
        
        # Create only the Ticket and TicketReply tables
        models.Ticket.__table__.create(bind=engine, checkfirst=True)
        models.TicketReply.__table__.create(bind=engine, checkfirst=True)
        
        print("✓ Ticket and TicketReply tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Creating Ticket Tables")
    print("=" * 50)
    
    create_ticket_tables()
    
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)

