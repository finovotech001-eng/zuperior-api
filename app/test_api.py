"""
Simple API test script to verify the API is working
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


class APITester:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_email = "test@example.com"
        self.user_password = "testpassword123"
    
    def print_response(self, response: requests.Response, title: str):
        """Print formatted response"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")
    
    def test_health(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        self.print_response(response, "Health Check")
        return response.status_code == 200
    
    def test_register(self):
        """Test user registration"""
        data = {
            "email": self.user_email,
            "password": self.user_password,
            "name": "Test User",
            "phone": "+1234567890",
            "country": "USA"
        }
        response = requests.post(f"{API_URL}/auth/register", json=data)
        self.print_response(response, "User Registration")
        return response.status_code in [200, 201, 400]  # 400 if user already exists
    
    def test_login(self):
        """Test user login"""
        data = {
            "email": self.user_email,
            "password": self.user_password
        }
        response = requests.post(f"{API_URL}/auth/login/json", json=data)
        self.print_response(response, "User Login")
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get("access_token")
            self.refresh_token = tokens.get("refresh_token")
            print(f"\n✓ Access token obtained: {self.access_token[:50]}...")
            print(f"✓ Refresh token obtained: {self.refresh_token[:50]}...")
            return True
        return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def test_get_profile(self):
        """Test getting user profile"""
        response = requests.get(f"{API_URL}/users/me", headers=self.get_headers())
        self.print_response(response, "Get User Profile")
        return response.status_code == 200
    
    def test_update_profile(self):
        """Test updating user profile"""
        data = {
            "name": "Updated Test User",
            "phone": "+9876543210"
        }
        response = requests.put(f"{API_URL}/users/me", json=data, headers=self.get_headers())
        self.print_response(response, "Update User Profile")
        return response.status_code == 200
    
    def test_create_mt5_account(self):
        """Test creating MT5 account"""
        data = {
            "accountId": "MT5-12345678"
        }
        response = requests.post(f"{API_URL}/mt5-accounts/", json=data, headers=self.get_headers())
        self.print_response(response, "Create MT5 Account")
        
        if response.status_code in [200, 201]:
            return response.json().get("id")
        return None
    
    def test_list_mt5_accounts(self):
        """Test listing MT5 accounts"""
        response = requests.get(
            f"{API_URL}/mt5-accounts/?page=1&per_page=10",
            headers=self.get_headers()
        )
        self.print_response(response, "List MT5 Accounts")
        return response.status_code == 200
    
    def test_create_deposit(self, mt5_account_id: str):
        """Test creating deposit"""
        data = {
            "mt5AccountId": mt5_account_id,
            "amount": 1000.00,
            "currency": "USD",
            "method": "bank_transfer",
            "bankDetails": "Account: 1234567890"
        }
        response = requests.post(f"{API_URL}/deposits/", json=data, headers=self.get_headers())
        self.print_response(response, "Create Deposit")
        return response.status_code in [200, 201]
    
    def test_list_deposits(self):
        """Test listing deposits"""
        response = requests.get(
            f"{API_URL}/deposits/?page=1&per_page=10&status=pending",
            headers=self.get_headers()
        )
        self.print_response(response, "List Deposits")
        return response.status_code == 200
    
    def test_refresh_token(self):
        """Test token refresh"""
        data = {
            "refresh_token": self.refresh_token
        }
        response = requests.post(f"{API_URL}/auth/refresh", json=data)
        self.print_response(response, "Refresh Access Token")
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get("access_token")
            self.refresh_token = tokens.get("refresh_token")
            print(f"\n✓ New access token obtained")
            return True
        return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "="*60)
        print("Starting API Tests")
        print("="*60)
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Health check
        tests_total += 1
        if self.test_health():
            tests_passed += 1
            print("✓ Health check passed")
        else:
            print("✗ Health check failed")
            return
        
        # Test 2: Register
        tests_total += 1
        if self.test_register():
            tests_passed += 1
            print("✓ Registration test passed")
        else:
            print("✗ Registration test failed")
        
        # Test 3: Login
        tests_total += 1
        if self.test_login():
            tests_passed += 1
            print("✓ Login test passed")
        else:
            print("✗ Login test failed")
            return
        
        # Test 4: Get profile
        tests_total += 1
        if self.test_get_profile():
            tests_passed += 1
            print("✓ Get profile test passed")
        else:
            print("✗ Get profile test failed")
        
        # Test 5: Update profile
        tests_total += 1
        if self.test_update_profile():
            tests_passed += 1
            print("✓ Update profile test passed")
        else:
            print("✗ Update profile test failed")
        
        # Test 6: Create MT5 account
        tests_total += 1
        mt5_account_id = self.test_create_mt5_account()
        if mt5_account_id:
            tests_passed += 1
            print("✓ Create MT5 account test passed")
        else:
            print("✗ Create MT5 account test failed")
        
        # Test 7: List MT5 accounts
        tests_total += 1
        if self.test_list_mt5_accounts():
            tests_passed += 1
            print("✓ List MT5 accounts test passed")
        else:
            print("✗ List MT5 accounts test failed")
        
        # Test 8: Create deposit (if MT5 account was created)
        if mt5_account_id:
            tests_total += 1
            if self.test_create_deposit(mt5_account_id):
                tests_passed += 1
                print("✓ Create deposit test passed")
            else:
                print("✗ Create deposit test failed")
        
        # Test 9: List deposits
        tests_total += 1
        if self.test_list_deposits():
            tests_passed += 1
            print("✓ List deposits test passed")
        else:
            print("✗ List deposits test failed")
        
        # Test 10: Refresh token
        tests_total += 1
        if self.test_refresh_token():
            tests_passed += 1
            print("✓ Refresh token test passed")
        else:
            print("✗ Refresh token test failed")
        
        # Summary
        print("\n" + "="*60)
        print(f"Test Results: {tests_passed}/{tests_total} passed")
        print("="*60)
        
        if tests_passed == tests_total:
            print("✓ All tests passed!")
        else:
            print(f"✗ {tests_total - tests_passed} test(s) failed")


if __name__ == "__main__":
    print("API Testing Script")
    print("Make sure the API server is running on http://localhost:8000")
    input("Press Enter to start tests...")
    
    tester = APITester()
    tester.run_all_tests()



