#!/usr/bin/env python3
"""Simple test to check if backend is working"""
import requests
import time

def test_backend():
    """Test if backend is responding"""
    try:
        print("Testing backend at http://localhost:8000...")
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is working!")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - is it running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend request timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints"""
    base_url = "http://localhost:8000/api/v1"
    
    # Test health endpoint (if it exists)
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"API root: {response.status_code}")
    except:
        print("API root endpoint not available")
    
    # Test auth endpoints
    try:
        response = requests.post(f"{base_url}/auth/register", 
                               json={"email": "test@example.com", "password": "Test1234"},
                               timeout=5)
        print(f"Register endpoint: {response.status_code}")
        if response.status_code == 422:
            print("  (422 is expected - validation error)")
    except Exception as e:
        print(f"Register endpoint error: {e}")

if __name__ == "__main__":
    print("🔍 Testing local backend...")
    
    # Wait a moment for backend to start
    print("Waiting 3 seconds for backend to start...")
    time.sleep(3)
    
    if test_backend():
        print("\n🧪 Testing API endpoints...")
        test_api_endpoints()
    
    print("\n📋 Summary:")
    print("- Backend: http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")
    print("- Frontend: http://localhost:3001")
    print("\nIf backend is not working, try:")
    print("1. cd backend")
    print("2. .venv\\Scripts\\activate")
    print("3. python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")