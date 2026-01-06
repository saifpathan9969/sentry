#!/usr/bin/env python3
"""
Test login directly in container
"""
import sqlite3
import bcrypt

def test_login():
    """Test login directly"""
    print("🔐 Testing login directly in container...")
    
    # Connect to database
    conn = sqlite3.connect('pentest_brain.db')
    cursor = conn.cursor()
    
    # Get user
    email = 'saifullahpathan49@gmail.com'
    password = 'sentry@779969'
    
    cursor.execute('SELECT email, password_hash, tier FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if user:
        print(f"✅ User found: {user[0]}")
        print(f"   Tier: {user[2]}")
        
        # Test password
        stored_hash = user[1].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            print(f"✅ Password matches!")
        else:
            print(f"❌ Password does not match!")
            
        # Show hash for debugging
        print(f"   Stored hash: {user[1][:50]}...")
        
    else:
        print(f"❌ User not found: {email}")
    
    # List all users
    cursor.execute('SELECT email, tier FROM users')
    all_users = cursor.fetchall()
    print(f"\n📊 All users in database:")
    for u in all_users:
        print(f"   {u[0]} - {u[1]}")
    
    conn.close()

if __name__ == "__main__":
    test_login()