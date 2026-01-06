#!/usr/bin/env python3
"""
Create users directly in Docker container database
"""
import sqlite3
import hashlib
import uuid
from datetime import datetime

def hash_password(password: str) -> str:
    """Hash password using bcrypt-like method"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_users():
    """Create users directly in SQLite database"""
    print("🔧 Creating users in Docker container database...")
    
    # Connect to SQLite database
    conn = sqlite3.connect('pentest_brain.db')
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            tier TEXT DEFAULT 'free',
            api_key_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            email_verified BOOLEAN DEFAULT 0
        )
    ''')
    
    # Users to create
    users = [
        {
            'email': 'saifullahpathan49@gmail.com',
            'password': 'sentry@779969',
            'full_name': 'Saifullah Pathan',
            'tier': 'enterprise'
        },
        {
            'email': 'saifullah.pathan24@sanjivani.edu.in',
            'password': 'sentry@779969',
            'full_name': 'Saifullah Pathan',
            'tier': 'enterprise'
        },
        {
            'email': 'test@example.com',
            'password': 'Test1234',
            'full_name': 'Test User',
            'tier': 'free'
        }
    ]
    
    for user in users:
        user_id = str(uuid.uuid4())
        password_hash = hash_password(user['password'])
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (id, email, password_hash, full_name, tier, is_active, email_verified, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, 1, ?, ?)
            ''', (
                user_id,
                user['email'],
                password_hash,
                user['full_name'],
                user['tier'],
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            print(f"✅ Created user: {user['email']} (Tier: {user['tier']})")
            
        except Exception as e:
            print(f"❌ Error creating user {user['email']}: {e}")
    
    conn.commit()
    
    # Verify users were created
    cursor.execute('SELECT email, tier, full_name FROM users')
    all_users = cursor.fetchall()
    
    print(f"\n📊 Total users in database: {len(all_users)}")
    for user in all_users:
        print(f"   {user[0]} - {user[1]} - {user[2]}")
    
    conn.close()
    
    print(f"\n🎯 Users created successfully!")
    print(f"🔑 Your credentials:")
    print(f"   Email: saifullahpathan49@gmail.com")
    print(f"   Email: saifullah.pathan24@sanjivani.edu.in")
    print(f"   Password: sentry@779969")
    print(f"   Tier: Enterprise (Full Access)")

if __name__ == "__main__":
    create_users()