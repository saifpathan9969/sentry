#!/usr/bin/env python3
"""
Test production deployment
"""
import requests
import json
import time

# Production URLs
BACKEND_URL = "https://sentry-backend-qugp.onrender.com"
FRONTEND_URL = "https://sentry-ift7qnmep-saifs-projects-7eef2715.vercel.app"

def test_backend_health():
    """Test backend health check"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend healthy: {data['status']} (v{data['version']})")
            return True
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_authentication():
    """Test authentication endpoints"""
    print("🔐 Testing authentication...")
    
    # Test credentials
    test_users = [
        {"email": "test@example.com", "password": "Test1234", "tier": "free"},
        {"email": "saifullahpathan49@gmail.com", "password": "Test1234", "tier": "enterprise"}
    ]
    
    for user in test_users:
        try:
            # Test login
            login_response = requests.post(
                f"{BACKEND_URL}/api/v1/auth/login",
                json={"email": user["email"], "password": user["password"]},
                timeout=10
            )
            
            if login_response.status_code == 200:
                data = login_response.json()
                print(f"✅ Login successful: {user['email']} ({data.get('user', {}).get('tier', 'unknown')} tier)")
                
                # Test token validation
                token = data.get('access_token')
                if token:
                    user_response = requests.get(
                        f"{BACKEND_URL}/api/v1/users/me",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=10
                    )
                    if user_response.status_code == 200:
                        print(f"✅ Token validation successful for {user['email']}")
                    else:
                        print(f"❌ Token validation failed for {user['email']}")
                
            else:
                print(f"❌ Login failed for {user['email']}: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                
        except Exception as e:
            print(f"❌ Authentication test failed for {user['email']}: {e}")

def test_scan_creation():
    """Test scan creation"""
    print("🔬 Testing scan creation...")
    
    try:
        # Login first
        login_response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json={"email": "test@example.com", "password": "Test1234"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print("❌ Cannot login for scan test")
            return
        
        token = login_response.json().get('access_token')
        
        # Create scan
        scan_data = {
            "target_url": "https://example.com",
            "scan_mode": "common",
            "execution_mode": "report_only"
        }
        
        scan_response = requests.post(
            f"{BACKEND_URL}/api/v1/scans/",
            json=scan_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        
        if scan_response.status_code == 200:
            scan = scan_response.json()
            print(f"✅ Scan created successfully: {scan.get('id', 'unknown')}")
            print(f"   Target: {scan.get('target', 'unknown')}")
            print(f"   Mode: {scan.get('scan_mode', 'unknown')}")
            print(f"   Execution: {scan.get('execution_mode', 'unknown')}")
        else:
            print(f"❌ Scan creation failed: {scan_response.status_code}")
            print(f"   Response: {scan_response.text}")
            
    except Exception as e:
        print(f"❌ Scan creation test failed: {e}")

def test_frontend_accessibility():
    """Test frontend accessibility"""
    print("🌐 Testing frontend accessibility...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessible")
            if "Sentry" in response.text:
                print("✅ Frontend content loaded correctly")
            else:
                print("⚠️  Frontend content may not be loading correctly")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend accessibility test failed: {e}")

def test_cors():
    """Test CORS configuration"""
    print("🔗 Testing CORS configuration...")
    
    try:
        # Simulate frontend request
        headers = {
            "Origin": FRONTEND_URL,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
        
        response = requests.options(
            f"{BACKEND_URL}/api/v1/auth/login",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            cors_headers = response.headers
            if "Access-Control-Allow-Origin" in cors_headers:
                print("✅ CORS configured correctly")
            else:
                print("⚠️  CORS headers missing")
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

def main():
    """Run all production tests"""
    print("🚀 Starting Production Deployment Tests")
    print("=" * 50)
    
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print()
    
    # Run tests
    backend_healthy = test_backend_health()
    print()
    
    if backend_healthy:
        test_authentication()
        print()
        
        test_scan_creation()
        print()
        
        test_cors()
        print()
    
    test_frontend_accessibility()
    print()
    
    print("=" * 50)
    print("🏁 Production tests completed!")
    print()
    print("📋 Next Steps:")
    print("1. Visit the frontend URL to test the UI")
    print("2. Login with test credentials")
    print("3. Create a scan and test the neural visualization")
    print("4. Test the 'Remember Me' functionality")

if __name__ == "__main__":
    main()