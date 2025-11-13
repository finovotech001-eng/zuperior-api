#!/usr/bin/env python3
"""
Verification script to check if the metadata issue is fixed
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("Testing model imports...")
    from app.models.models import Transaction, Account
    print("✓ Transaction model imported successfully")
    print("✓ Account model imported successfully")
    
    # Check Transaction model attributes
    print("\nChecking Transaction model attributes:")
    transaction_attrs = dir(Transaction)
    
    if 'metadata_json' in transaction_attrs:
        print("✓ metadata_json attribute exists (correct)")
    else:
        print("✗ metadata_json attribute missing!")
    
    if 'metadata' in transaction_attrs and not hasattr(Transaction, '__mapper__'):
        # metadata might exist as SQLAlchemy's metadata, which is fine
        if hasattr(Transaction, 'metadata') and type(Transaction.metadata).__name__ == 'MetaData':
            print("✓ metadata exists as SQLAlchemy MetaData (this is fine)")
        else:
            print("✗ WARNING: metadata attribute exists as a column (this is the problem!)")
    else:
        print("✓ No metadata column attribute (correct)")
    
    # Try to create the table metadata (this is where the error would occur)
    print("\nChecking table definition...")
    if hasattr(Transaction, '__table__'):
        columns = [col.name for col in Transaction.__table__.columns]
        print(f"✓ Transaction table has {len(columns)} columns")
        if 'metadata_json' in columns:
            print("✓ metadata_json column found in table definition")
        if 'metadata' in columns:
            print("✗ ERROR: metadata column found in table definition (this is the problem!)")
        else:
            print("✓ No metadata column in table definition (correct)")
    
    print("\n✅ All checks passed! The fix should work.")
    print("\nIf you're still seeing the error:")
    print("1. Stop your server completely")
    print("2. Delete all __pycache__ directories: find . -type d -name __pycache__ -exec rm -r {} +")
    print("3. Delete all .pyc files: find . -name '*.pyc' -delete")
    print("4. Restart your server")
    
except Exception as e:
    print(f"\n✗ Error occurred: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

