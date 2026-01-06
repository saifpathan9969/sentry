#!/usr/bin/env python3
"""
Test API login from inside container
"""
import requests
import json

def test_api_login():
    """Test API login"""
    print("🔐 Testing API login from inside container...")
    
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "email": "saifullahpathan49@gmail.com",
        "password": "sentry@779969"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login successful!")
            print(f"   Access Token: {result['access_token'][:50]}...")
            
            # Test protected endpoint
            headers = {"Authorization": f"Bearer {result['access_token']}"}
            me_response = requests.get("http://localhost:8000/api/v1/users/me", headers=headers)
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"   User: {user_data['email']}")
                print(f"   Tier: {user_data['tier']}")
                print(f"   Full Name: {user_data['full_name']}")
            else:
                print(f"⚠️ Protected endpoint failed: {me_response.status_code}")
                print(f"   Error: {me_response.text}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_login()