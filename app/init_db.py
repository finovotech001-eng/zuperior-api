"""
Database initialization script
Creates tables and optionally creates an initial admin user
"""
from core.database import engine, Base, SessionLocal
from core.security import get_password_hash
from models.models import User
from sqlalchemy.exc import IntegrityError
import sys


def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def create_admin_user(email: str, password: str, name: str = "Admin"):
    """Create an initial admin user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"✗ User with email {email} already exists")
            return False
        
        # Create admin user
        admin_user = User(
            email=email,
            password=get_password_hash(password),
            name=name,
            role="admin",
            status="active",
            emailVerified=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✓ Admin user created successfully!")
        print(f"  Email: {email}")
        print(f"  ID: {admin_user.id}")
        print(f"  Client ID: {admin_user.clientId}")
        return True
        
    except IntegrityError as e:
        db.rollback()
        print(f"✗ Error creating admin user: {e}")
        return False
    except Exception as e:
        db.rollback()
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        db.close()


def create_test_user(email: str, password: str, name: str = "Test User"):
    """Create a test user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"✗ User with email {email} already exists")
            return False
        
        # Create test user
        test_user = User(
            email=email,
            password=get_password_hash(password),
            name=name,
            role="user",
            status="active",
            emailVerified=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✓ Test user created successfully!")
        print(f"  Email: {email}")
        print(f"  ID: {test_user.id}")
        print(f"  Client ID: {test_user.clientId}")
        return True
        
    except IntegrityError as e:
        db.rollback()
        print(f"✗ Error creating test user: {e}")
        return False
    except Exception as e:
        db.rollback()
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Database Initialization Script")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    # Create admin user
    print("\n" + "=" * 50)
    print("Creating Admin User")
    print("=" * 50)
    admin_email = input("Admin email (default: admin@example.com): ").strip() or "admin@example.com"
    admin_password = input("Admin password (default: admin123): ").strip() or "admin123"
    admin_name = input("Admin name (default: Admin): ").strip() or "Admin"
    
    create_admin_user(admin_email, admin_password, admin_name)
    
    # Ask if want to create test user
    print("\n" + "=" * 50)
    create_test = input("Create test user? (y/n, default: y): ").strip().lower()
    if create_test in ['y', 'yes', '']:
        test_email = input("Test user email (default: test@example.com): ").strip() or "test@example.com"
        test_password = input("Test user password (default: test123): ").strip() or "test123"
        test_name = input("Test user name (default: Test User): ").strip() or "Test User"
        
        create_test_user(test_email, test_password, test_name)
    
    print("\n" + "=" * 50)
    print("Initialization complete!")
    print("=" * 50)
    print("\nYou can now start the API server:")
    print("  python main.py")
    print("\nOr:")
    print("  uvicorn main:app --reload")



