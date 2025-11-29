from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
import uuid

client = TestClient(app)

def generate_random_string():
    return uuid.uuid4().hex[:8]

def get_admin_token():
    # Assuming there's a way to get admin token or we can mock it
    # For now, let's try to login as a user and see if we can create countries/groups
    # If not, we might need to create an admin user directly in DB or mock the dependency
    # But for simplicity, let's try with a new user and see permissions
    
    # Register a new user
    email = f"admin_{generate_random_string()}@example.com"
    password = "password123"
    response = client.post(f"{settings.API_V1_STR}/auth/register", json={
        "email": email,
        "password": password,
        "name": "Admin User",
        "phone": "+1234567890",
        "country": "USA"
    })
    
    # Login
    response = client.post(f"{settings.API_V1_STR}/auth/login/json", json={
        "email": email,
        "password": password
    })
    
    # Promote to Admin (Direct DB access)
    from app.core.database import get_db
    from app.models.models import User
    from sqlalchemy import text
    
    try:
        db = next(get_db())
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = "admin"
            db.commit()
            print(f"[PASS] Promoted {email} to admin")
    except Exception as e:
        print(f"Error promoting user: {e}")
        
    return response.json()["access_token"]

def verify_apis():
    print("Starting verification...")
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Test Countries API
    print("\nTesting Countries API...")
    country_code = generate_random_string()[:2].upper()
    country_data = {
        "code": country_code,
        "name": f"Test Country {country_code}",
        "phoneCode": "123",
        "currency": "USD",
        "region": "Test Region"
    }
    
    # Create Country
    response = client.post(f"{settings.API_V1_STR}/countries/", json=country_data, headers=headers)
    if response.status_code == 201:
        print("[PASS] Create Country passed")
        country_id = response.json()["id"]
    elif response.status_code == 403:
        print("! Create Country skipped (User is not admin)")
        # We might need to mock admin dependency or manually update user role
        # For now, let's assume we can proceed or skip admin-only tests
        country_id = None
    else:
        print(f"[FAIL] Create Country failed: {response.status_code} {response.text}")
        country_id = None

    # List Countries
    print("\nListing Countries...")
    response = client.get(f"{settings.API_V1_STR}/countries/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        print(f"[PASS] List Countries passed. Found {len(items)} items.")
        if len(items) == 0:
            print("! Warning: No countries returned.")
        else:
            print(f"Sample item: {items[0]}")
    else:
        print(f"[FAIL] List Countries failed: {response.status_code} {response.text}")

    # 2. Test Group Management API
    print("\nTesting Group Management API...")
    group_name = f"Group_{generate_random_string()}"
    group_data = {
        "group": group_name,
        "dedicated_name": "Test Dedicated",
        "account_type": "Live",
        "server": 1,
        "is_active": True
    }
    
    # Create Group
    response = client.post(f"{settings.API_V1_STR}/group-management/", json=group_data, headers=headers)
    if response.status_code == 201:
        print("[PASS] Create Group passed")
        group_id = response.json()["id"]
    elif response.status_code == 403:
        print("! Create Group skipped (User is not admin)")
        group_id = None
    else:
        print(f"[FAIL] Create Group failed: {response.status_code} {response.text}")
        group_id = None

    # List Groups (no filters)
    print("\nListing Groups (no filters)...")
    response = client.get(f"{settings.API_V1_STR}/group-management/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        print(f"[PASS] List Groups (no filters): Found {len(items)} items.")
    else:
        print(f"[FAIL] List Groups failed: {response.status_code} {response.text}")

    # List Groups (is_active=True)
    print("\nListing Groups (is_active=True)...")
    response = client.get(f"{settings.API_V1_STR}/group-management/?is_active=true", headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        print(f"[PASS] List Groups (active): Found {len(items)} items.")
    else:
        print(f"[FAIL] List Groups (active) failed: {response.status_code} {response.text}")

    # List Groups (is_active=False)
    print("\nListing Groups (is_active=False)...")
    response = client.get(f"{settings.API_V1_STR}/group-management/?is_active=false", headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        print(f"[PASS] List Groups (inactive): Found {len(items)} items.")
    else:
        print(f"[FAIL] List Groups (inactive) failed: {response.status_code} {response.text}")
    # Try to create account with valid group (if group creation succeeded)
    if group_id:
        valid_group_account = {
            "accountId": f"MT5-{generate_random_string()}",
            "package": group_name
        }
        response = client.post(f"{settings.API_V1_STR}/mt5-accounts/", json=valid_group_account, headers=headers)
        if response.status_code == 201:
            print("[PASS] Create Mt5Account with valid group passed")
        else:
            print(f"[FAIL] Create Mt5Account with valid group failed: {response.status_code} {response.text}")
    else:
        print("! Skipping valid group test (Group creation failed/skipped)")

    # 4. Test Admin MT5Account Access
    print("\nTesting Admin MT5Account Access...")
    # List all accounts (Admin should see all)
    response = client.get(f"{settings.API_V1_STR}/mt5-accounts/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        print(f"[PASS] Admin List MT5 Accounts: Found {len(items)} items.")
        
        # Check for new fields in the first item
        if len(items) > 0:
            account = items[0]
            fields_to_check = ["balance", "equity", "credit", "margin", "marginFree"]
            missing_fields = [f for f in fields_to_check if f not in account]
            if not missing_fields:
                print(f"[PASS] New fields present: {fields_to_check}")
            else:
                print(f"[FAIL] Missing fields: {missing_fields}")
                print(f"Account data: {account}")
    else:
        print(f"[FAIL] Admin List MT5 Accounts failed: {response.status_code} {response.text}")

    # Test Group Filter
    print("\nTesting MT5Account Group Filter...")
    # Use a group name that likely exists or was just created
    filter_group = group_name if group_id else "managers\\administrators"
    response = client.get(f"{settings.API_V1_STR}/mt5-accounts/?group={filter_group}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        print(f"[PASS] Filter by Group '{filter_group}': Found {len(items)} items.")
    else:
        print(f"[FAIL] Filter by Group failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    verify_apis()
