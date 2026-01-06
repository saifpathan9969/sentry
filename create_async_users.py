#!/usr/bin/env python3
"""
Create users using async SQLAlchemy (same as FastAPI app)
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import User
from app.core.security import hash_password
from app.core.config import settings

async def create_users():
    """Create users using async SQLAlchemy"""
    print("🔧 Creating users with async SQLAlchemy...")
    
    # Create async engine (same as the app)
    database_url = settings.DATABASE_URL
    if database_url.startswith("sqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    # Users to create
    users_data = [
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
    
    async with AsyncSessionLocal() as session:
        try:
            for user_data in users_data:
                # Check if user exists
                from sqlalchemy import select
                result = await session.execute(
                    select(User).where(User.email == user_data['email'])
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    # Update existing user
                    existing_user.password_hash = hash_password(user_data['password'])
                    existing_user.full_name = user_data['full_name']
                    existing_user.tier = user_data['tier']
                    existing_user.is_active = True
                    existing_user.email_verified = True
                    print(f"✅ Updated user: {user_data['email']} (Tier: {user_data['tier']})")
                else:
                    # Create new user
                    user = User(
                        email=user_data['email'],
                        password_hash=hash_password(user_data['password']),
                        full_name=user_data['full_name'],
                        tier=user_data['tier'],
                        is_active=True,
                        email_verified=True
                    )
                    session.add(user)
                    print(f"✅ Created user: {user_data['email']} (Tier: {user_data['tier']})")
            
            await session.commit()
            
            # Verify users
            result = await session.execute(select(User))
            all_users = result.scalars().all()
            
            print(f"\n📊 Total users in database: {len(all_users)}")
            for user in all_users:
                print(f"   {user.email} - {user.tier} - {user.full_name}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error: {e}")
            raise
        finally:
            await session.close()
    
    await engine.dispose()
    
    print(f"\n🎯 Users created successfully with async SQLAlchemy!")
    print(f"🔑 Your credentials:")
    print(f"   Email: saifullahpathan49@gmail.com")
    print(f"   Email: saifullah.pathan24@sanjivani.edu.in")
    print(f"   Password: sentry@779969")
    print(f"   Tier: Enterprise (Full Access)")

if __name__ == "__main__":
    asyncio.run(create_users())