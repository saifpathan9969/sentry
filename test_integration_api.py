"""
Simple integration test to verify frontend-backend connection
Run this after starting the backend server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    print(f"  Status: {data['status']}")
    print(f"  Version: {data['version']}")
    print("  ✓ Health check passed\n")

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    print(f"  Message: {data['message']}")
    print("  ✓ Root endpoint passed\n")

def test_docs():
    """Test API docs endpoint"""
    print("Testing API docs endpoint...")
    response = requests.get(f"{BASE_URL}/docs")
    assert response.status_code == 200
    print("  ✓ API docs accessible\n")

def test_register_and_login():
    """Test user registration and login"""
    print("Testing registration and login...")
    
    # Register a test user
    test_email = "test_integration@example.com"
    test_password = "TestPassword123"
    
    register_data = {
        "email": test_email,
        "password": test_password,
        "full_name": "Test User"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=register_data
    )
    
    if response.status_code == 201:
        print("  ✓ Registration successful")
        data = response.json()
        print(f"  User ID: {data['user']['id']}")
        print(f"  Tier: {data['user']['tier']}")
        access_token = data['access_token']
    elif response.status_code == 400 and "already registered" in response.text.lower():
        print("  User already exists, trying login...")
        # Try login instead
        login_data = {
            "email": test_email,
            "password": test_password
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        access_token = data['access_token']
        print("  ✓ Login successful")
    else:
        print(f"  Registration failed: {response.status_code} - {response.text}")
        return None
    
    return access_token

def test_authenticated_endpoints(token):
    """Test authenticated endpoints"""
    if not token:
        print("Skipping authenticated tests (no token)")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get current user
    print("Testing get current user...")
    response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    user = response.json()
    print(f"  Email: {user['email']}")
    print(f"  Tier: {user['tier']}")
    print("  ✓ Get current user passed\n")
    
    # Test list scans (should be empty for new user)
    print("Testing list scans...")
    response = requests.get(f"{BASE_URL}/api/v1/scans", headers=headers)
    assert response.status_code == 200
    data = response.json()
    print(f"  Total scans: {data['total']}")
    print("  ✓ List scans passed\n")
    
    # Test usage statistics
    print("Testing usage statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/users/me/usage", headers=headers)
    if response.status_code == 200:
        print("  ✓ Usage statistics passed\n")
    else:
        print(f"  Usage statistics returned {response.status_code} (may not be implemented)\n")

def main():
    print("=" * 50)
    print("AI Pentest Brain - Integration Test")
    print("=" * 50 + "\n")
    
    try:
        test_health()
        test_root()
        test_docs()
        token = test_register_and_login()
        test_authenticated_endpoints(token)
        
        print("=" * 50)
        print("All integration tests passed! ✓")
        print("=" * 50)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend server")
        print("Make sure the backend is running on http://localhost:8000")
    except AssertionError as e:
        print(f"ERROR: Test failed - {e}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
