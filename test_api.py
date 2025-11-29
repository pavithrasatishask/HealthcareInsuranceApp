"""
Comprehensive API test script for Healthcare Insurance API.
Tests all endpoints with the requested scenario.
"""
import requests
import json
import time
import sys
from typing import Dict, List, Optional

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure the base URL - update this if your app runs on a different address
BASE_URL = "http://192.168.68.118:5000"
API_BASE = f"{BASE_URL}/api"

# Alternative: Use localhost if running locally
# BASE_URL = "http://localhost:5000"
# API_BASE = f"{BASE_URL}/api"

# Store tokens and IDs for testing
tokens: Dict[str, str] = {}
user_ids: Dict[str, int] = {}
policy_ids: Dict[str, List[int]] = {}
claim_ids: Dict[str, List[int]] = {}


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_test(test_name: str):
    """Print test name."""
    print(f"\n[TEST] {test_name}")


def print_success(message: str):
    """Print success message."""
    try:
        print(f"✅ {message}")
    except UnicodeEncodeError:
        print(f"[SUCCESS] {message}")


def print_error(message: str):
    """Print error message."""
    try:
        print(f"❌ {message}")
    except UnicodeEncodeError:
        print(f"[ERROR] {message}")


def print_info(message: str):
    """Print info message."""
    try:
        print(f"ℹ️  {message}")
    except UnicodeEncodeError:
        print(f"[INFO] {message}")


def make_request(method: str, endpoint: str, token: Optional[str] = None, data: Optional[dict] = None) -> Optional[dict]:
    """Make HTTP request and return response."""
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        else:
            print_error(f"Unsupported method: {method}")
            return None
        
        try:
            result = response.json()
        except:
            result = {"raw_response": response.text}
        
        result["_status_code"] = response.status_code
        return result
    
    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed. Is the Flask app running on {BASE_URL}?")
        return None
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None


def test_health_check():
    """Test health check endpoint."""
    print_test("Health Check")
    # Health check is at root, not under /api
    try:
        response = requests.get(BASE_URL + "/")
        result = response.json()
        result["_status_code"] = response.status_code
        
        if result and result.get("_status_code") == 200:
            print_success("Health check passed")
            print_info(f"Response: {result.get('message')}")
            return True
        else:
            print_error("Health check failed")
            return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False


def register_user(email: str, password: str, full_name: str, role: str, phone: str = None, address: str = None) -> Optional[int]:
    """Register a new user."""
    data = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role
    }
    
    if phone:
        data["phone"] = phone
    if address:
        data["address"] = address
    
    result = make_request("POST", "/auth/register", data=data)
    
    if result and result.get("_status_code") == 201:
        user_id = result.get("user", {}).get("id")
        print_success(f"Registered {role}: {email} (ID: {user_id})")
        return user_id
    else:
        error = result.get("error", "Unknown error") if result else "No response"
        status = result.get("_status_code", "N/A") if result else "N/A"
        print_error(f"Failed to register {email}: {error} (Status: {status})")
        if result:
            print_info(f"Full response: {json.dumps(result, indent=2)}")
        return None


def login_user(email: str, password: str) -> Optional[str]:
    """Login user and return token."""
    data = {
        "email": email,
        "password": password
    }
    
    result = make_request("POST", "/auth/login", data=data)
    
    if result and result.get("_status_code") == 200:
        token = result.get("token")
        user = result.get("user", {})
        print_success(f"Logged in: {user.get('email')} ({user.get('role')})")
        return token
    else:
        error = result.get("error", "Unknown error") if result else "No response"
        print_error(f"Failed to login {email}: {error}")
        return None


def create_policy(token: str, user_id: int, policy_type: str = "Individual Health") -> Optional[int]:
    """Create a policy for a user."""
    data = {
        "user_id": user_id,
        "policy_type": policy_type,
        "coverage_amount": 50000.00,
        "premium_amount": 500.00,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "status": "active"
    }
    
    result = make_request("POST", "/policies", token=token, data=data)
    
    if result and result.get("_status_code") == 201:
        policy = result.get("policy", {})
        policy_id = policy.get("id")
        policy_number = policy.get("policy_number")
        print_success(f"Created policy {policy_number} (ID: {policy_id}) for user {user_id}")
        return policy_id
    else:
        error = result.get("error", "Unknown error") if result else "No response"
        print_error(f"Failed to create policy: {error}")
        return None


def submit_claim(token: str, policy_id: int, claim_amount: float = 5000.00) -> Optional[int]:
    """Submit a claim for a policy."""
    data = {
        "policy_id": policy_id,
        "claim_amount": claim_amount,
        "diagnosis": "Medical treatment",
        "treatment_details": "Standard medical procedure",
        "provider_name": "City Hospital",
        "service_date": "2024-01-15"
    }
    
    result = make_request("POST", "/claims", token=token, data=data)
    
    if result and result.get("_status_code") == 201:
        claim = result.get("claim", {})
        claim_id = claim.get("id")
        claim_number = claim.get("claim_number")
        print_success(f"Submitted claim {claim_number} (ID: {claim_id}) for policy {policy_id}")
        return claim_id
    else:
        error = result.get("error", "Unknown error") if result else "No response"
        print_error(f"Failed to submit claim: {error}")
        return None


def test_get_current_user(token: str):
    """Test get current user endpoint."""
    result = make_request("GET", "/auth/me", token=token)
    
    if result and result.get("_status_code") == 200:
        user = result.get("user", {})
        print_success(f"Get current user: {user.get('email')}")
        return True
    else:
        print_error("Failed to get current user")
        return False


def test_get_all_users(token: str):
    """Test get all users endpoint."""
    result = make_request("GET", "/users", token=token)
    
    if result and result.get("_status_code") == 200:
        users = result.get("users", [])
        print_success(f"Get all users: {len(users)} users found")
        return True
    else:
        print_error("Failed to get all users")
        return False


def test_get_policies(token: str):
    """Test get policies endpoint."""
    result = make_request("GET", "/policies", token=token)
    
    if result and result.get("_status_code") == 200:
        policies = result.get("policies", [])
        print_success(f"Get policies: {len(policies)} policies found")
        return True
    else:
        print_error("Failed to get policies")
        return False


def test_get_claims(token: str):
    """Test get claims endpoint."""
    result = make_request("GET", "/claims", token=token)
    
    if result and result.get("_status_code") == 200:
        claims = result.get("claims", [])
        print_success(f"Get claims: {len(claims)} claims found")
        return True
    else:
        print_error("Failed to get claims")
        return False


def review_claim(token: str, claim_id: int, status: str = "approved", approved_amount: float = 4500.00):
    """Review a claim."""
    data = {
        "status": status,
        "approved_amount": approved_amount,
        "review_notes": f"Claim reviewed and {status}"
    }
    
    result = make_request("POST", f"/claims/{claim_id}/review", token=token, data=data)
    
    if result and result.get("_status_code") == 200:
        claim = result.get("claim", {})
        print_success(f"Reviewed claim {claim_id}: {status}")
        return True
    else:
        error = result.get("error", "Unknown error") if result else "No response"
        print_error(f"Failed to review claim: {error}")
        return False


def main():
    """Main test function."""
    print_section("Healthcare Insurance API - Comprehensive Test Suite")
    
    # Test health check
    if not test_health_check():
        print_error("\nHealth check failed. Please ensure the Flask app is running.")
        print_info("Start the app with: python app.py")
        return
    
    print_section("Step 1: Register 6 Users (2 Patients, 2 Providers, 2 Administrators)")
    
    # Register 2 patients
    user_ids["patient1"] = register_user(
        "patient1@test.com", "password123", "Patient One", "patient", 
        "1111111111", "123 Patient St"
    )
    user_ids["patient2"] = register_user(
        "patient2@test.com", "password123", "Patient Two", "patient",
        "2222222222", "456 Patient Ave"
    )
    
    # Register 2 providers
    user_ids["provider1"] = register_user(
        "provider1@test.com", "password123", "Dr. Provider One", "provider",
        "3333333333", "789 Provider Blvd"
    )
    user_ids["provider2"] = register_user(
        "provider2@test.com", "password123", "Dr. Provider Two", "provider",
        "4444444444", "321 Provider Way"
    )
    
    # Register 2 administrators
    user_ids["admin1"] = register_user(
        "admin1@test.com", "password123", "Admin One", "administrator",
        "5555555555", "654 Admin St"
    )
    user_ids["admin2"] = register_user(
        "admin2@test.com", "password123", "Admin Two", "administrator",
        "6666666666", "987 Admin Ave"
    )
    
    # Check if all registrations succeeded
    if None in user_ids.values():
        print_error("\nSome user registrations failed. Please check the errors above.")
        return
    
    print_section("Step 2: Login All Users and Get Tokens")
    
    # Login all users
    tokens["patient1"] = login_user("patient1@test.com", "password123")
    tokens["patient2"] = login_user("patient2@test.com", "password123")
    tokens["provider1"] = login_user("provider1@test.com", "password123")
    tokens["provider2"] = login_user("provider2@test.com", "password123")
    tokens["admin1"] = login_user("admin1@test.com", "password123")
    tokens["admin2"] = login_user("admin2@test.com", "password123")
    
    # Check if all logins succeeded
    if None in tokens.values():
        print_error("\nSome logins failed. Please check the errors above.")
        return
    
    # Test get current user endpoint
    print_test("Test GET /api/auth/me")
    test_get_current_user(tokens["patient1"])
    
    print_section("Step 3: Create 2 Policies for Each User (Using Provider/Admin Accounts)")
    
    # Initialize policy lists
    policy_ids["patient1"] = []
    policy_ids["patient2"] = []
    policy_ids["provider1"] = []
    policy_ids["provider2"] = []
    policy_ids["admin1"] = []
    policy_ids["admin2"] = []
    
    # Create 2 policies for patient1 (using provider1)
    print_info(f"\nCreating policies for Patient 1 (user_id: {user_ids['patient1']})")
    policy_ids["patient1"].append(create_policy(tokens["provider1"], user_ids["patient1"], "Individual Health"))
    policy_ids["patient1"].append(create_policy(tokens["provider1"], user_ids["patient1"], "Family Plan"))
    
    # Create 2 policies for patient2 (using provider2)
    print_info(f"\nCreating policies for Patient 2 (user_id: {user_ids['patient2']})")
    policy_ids["patient2"].append(create_policy(tokens["provider2"], user_ids["patient2"], "Individual Health"))
    policy_ids["patient2"].append(create_policy(tokens["provider2"], user_ids["patient2"], "Family Plan"))
    
    # Create 2 policies for provider1 (using admin1)
    print_info(f"\nCreating policies for Provider 1 (user_id: {user_ids['provider1']})")
    policy_ids["provider1"].append(create_policy(tokens["admin1"], user_ids["provider1"], "Individual Health"))
    policy_ids["provider1"].append(create_policy(tokens["admin1"], user_ids["provider1"], "Family Plan"))
    
    # Create 2 policies for provider2 (using admin2)
    print_info(f"\nCreating policies for Provider 2 (user_id: {user_ids['provider2']})")
    policy_ids["provider2"].append(create_policy(tokens["admin2"], user_ids["provider2"], "Individual Health"))
    policy_ids["provider2"].append(create_policy(tokens["admin2"], user_ids["provider2"], "Family Plan"))
    
    # Create 2 policies for admin1 (using admin2)
    print_info(f"\nCreating policies for Admin 1 (user_id: {user_ids['admin1']})")
    policy_ids["admin1"].append(create_policy(tokens["admin2"], user_ids["admin1"], "Individual Health"))
    policy_ids["admin1"].append(create_policy(tokens["admin2"], user_ids["admin1"], "Family Plan"))
    
    # Create 2 policies for admin2 (using admin1)
    print_info(f"\nCreating policies for Admin 2 (user_id: {user_ids['admin2']})")
    policy_ids["admin2"].append(create_policy(tokens["admin1"], user_ids["admin2"], "Individual Health"))
    policy_ids["admin2"].append(create_policy(tokens["admin1"], user_ids["admin2"], "Family Plan"))
    
    # Filter out None values
    for key in policy_ids:
        policy_ids[key] = [p for p in policy_ids[key] if p is not None]
    
    # Test get policies endpoint
    print_test("Test GET /api/policies")
    test_get_policies(tokens["patient1"])
    test_get_policies(tokens["provider1"])
    
    print_section("Step 4: Submit 2 Claims for Each User Who Has 2 Active Policies")
    
    # Initialize claim lists
    claim_ids["patient1"] = []
    claim_ids["patient2"] = []
    claim_ids["provider1"] = []
    claim_ids["provider2"] = []
    claim_ids["admin1"] = []
    claim_ids["admin2"] = []
    
    # Submit 2 claims for patient1 (who has 2 policies)
    if len(policy_ids["patient1"]) >= 2:
        print_info(f"\nSubmitting claims for Patient 1 (has {len(policy_ids['patient1'])} policies)")
        claim_ids["patient1"].append(submit_claim(tokens["patient1"], policy_ids["patient1"][0], 5000.00))
        claim_ids["patient1"].append(submit_claim(tokens["patient1"], policy_ids["patient1"][1], 7500.00))
    
    # Submit 2 claims for patient2 (who has 2 policies)
    if len(policy_ids["patient2"]) >= 2:
        print_info(f"\nSubmitting claims for Patient 2 (has {len(policy_ids['patient2'])} policies)")
        claim_ids["patient2"].append(submit_claim(tokens["patient2"], policy_ids["patient2"][0], 3000.00))
        claim_ids["patient2"].append(submit_claim(tokens["patient2"], policy_ids["patient2"][1], 6000.00))
    
    # Submit 2 claims for provider1 (who has 2 policies)
    if len(policy_ids["provider1"]) >= 2:
        print_info(f"\nSubmitting claims for Provider 1 (has {len(policy_ids['provider1'])} policies)")
        claim_ids["provider1"].append(submit_claim(tokens["provider1"], policy_ids["provider1"][0], 4000.00))
        claim_ids["provider1"].append(submit_claim(tokens["provider1"], policy_ids["provider1"][1], 5500.00))
    
    # Submit 2 claims for provider2 (who has 2 policies)
    if len(policy_ids["provider2"]) >= 2:
        print_info(f"\nSubmitting claims for Provider 2 (has {len(policy_ids['provider2'])} policies)")
        claim_ids["provider2"].append(submit_claim(tokens["provider2"], policy_ids["provider2"][0], 4500.00))
        claim_ids["provider2"].append(submit_claim(tokens["provider2"], policy_ids["provider2"][1], 6500.00))
    
    # Submit 2 claims for admin1 (who has 2 policies)
    if len(policy_ids["admin1"]) >= 2:
        print_info(f"\nSubmitting claims for Admin 1 (has {len(policy_ids['admin1'])} policies)")
        claim_ids["admin1"].append(submit_claim(tokens["admin1"], policy_ids["admin1"][0], 3500.00))
        claim_ids["admin1"].append(submit_claim(tokens["admin1"], policy_ids["admin1"][1], 5000.00))
    
    # Submit 2 claims for admin2 (who has 2 policies)
    if len(policy_ids["admin2"]) >= 2:
        print_info(f"\nSubmitting claims for Admin 2 (has {len(policy_ids['admin2'])} policies)")
        claim_ids["admin2"].append(submit_claim(tokens["admin2"], policy_ids["admin2"][0], 4200.00))
        claim_ids["admin2"].append(submit_claim(tokens["admin2"], policy_ids["admin2"][1], 5800.00))
    
    # Filter out None values
    for key in claim_ids:
        claim_ids[key] = [c for c in claim_ids[key] if c is not None]
    
    # Test get claims endpoint
    print_test("Test GET /api/claims")
    test_get_claims(tokens["patient1"])
    test_get_claims(tokens["provider1"])
    
    print_section("Step 5: Test Additional Endpoints")
    
    # Test get all users (admin/provider only)
    print_test("Test GET /api/users (Admin/Provider only)")
    test_get_all_users(tokens["admin1"])
    
    # Test get user by ID
    print_test("Test GET /api/users/<id>")
    result = make_request("GET", f"/users/{user_ids['patient1']}", token=tokens["patient1"])
    if result and result.get("_status_code") == 200:
        print_success("Get user by ID successful")
    
    # Test review claims (admin/provider)
    print_test("Test POST /api/claims/<id>/review")
    if claim_ids["patient1"]:
        review_claim(tokens["provider1"], claim_ids["patient1"][0], "approved", 4500.00)
        if len(claim_ids["patient1"]) > 1:
            review_claim(tokens["admin1"], claim_ids["patient1"][1], "approved", 7000.00)
    
    # Test update claim status (admin only)
    print_test("Test PATCH /api/claims/<id>/status (Admin only)")
    if claim_ids["patient1"]:
        data = {"status": "paid"}
        result = make_request("PATCH", f"/claims/{claim_ids['patient1'][0]}/status", token=tokens["admin1"], data=data)
        if result and result.get("_status_code") == 200:
            print_success("Updated claim status to 'paid'")
    
    # Test update policy status (admin only)
    print_test("Test PATCH /api/policies/<id>/status (Admin only)")
    if policy_ids["patient1"]:
        data = {"status": "active"}
        result = make_request("PATCH", f"/policies/{policy_ids['patient1'][0]}/status", token=tokens["admin1"], data=data)
        if result and result.get("_status_code") == 200:
            print_success("Updated policy status")
    
    print_section("Test Summary")
    
    print_info(f"Users registered: {len([u for u in user_ids.values() if u is not None])}")
    print_info(f"Tokens obtained: {len([t for t in tokens.values() if t is not None])}")
    
    total_policies = sum(len(p) for p in policy_ids.values())
    print_info(f"Policies created: {total_policies}")
    
    total_claims = sum(len(c) for c in claim_ids.values())
    print_info(f"Claims submitted: {total_claims}")
    
    print_section("Test Complete!")
    print_success("All tests executed. Check the output above for any errors.")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            print("\n\n⚠️  Test interrupted by user")
        except:
            print("\n\n[WARNING] Test interrupted by user")
    except Exception as e:
        try:
            print(f"\n\n❌ Unexpected error: {str(e)}")
        except:
            print(f"\n\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

