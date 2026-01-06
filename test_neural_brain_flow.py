#!/usr/bin/env python3
"""
Test the complete neural brain scan flow
"""
import asyncio
import sys
import os
sys.path.append('backend')

from backend.app.db.session import async_session_maker
from backend.app.models.user import User
from backend.app.models.scan import Scan
from backend.app.services.scan_service import ScanService
from backend.app.schemas.scan import ScanCreate
from sqlalchemy import select


async def test_neural_brain_flow():
    """Test the complete flow from scan creation to neural brain visualization"""
    
    print("🧠 Testing Neural Brain Scan Flow...")
    print("=" * 50)
    
    async with async_session_maker() as db:
        # Get test user
        query = select(User).where(User.email == 'saifullahpathan49@gmail.com')
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Test user not found. Please run backend/create_owner_user.py first")
            return
        
        print(f"✅ Found test user: {user.email} (tier: {user.tier})")
        
        # Create a test scan
        scan_data = ScanCreate(
            target_url="https://example.com",
            scan_mode="common",
            execution_mode="report_only"
        )
        
        print(f"🎯 Creating scan for: {scan_data.target_url}")
        scan = await ScanService.create_scan(db, user, scan_data)
        
        print(f"✅ Scan created with ID: {scan.id}")
        print(f"   Status: {scan.status}")
        print(f"   Target: {scan.target}")
        print(f"   Mode: {scan.scan_mode}")
        print(f"   Execution: {scan.execution_mode}")
        
        # Wait a moment for the scan to start
        await asyncio.sleep(2)
        
        # Check scan status
        updated_scan = await ScanService.get_scan(db, scan.id, user.id)
        print(f"🔄 Updated scan status: {updated_scan.status}")
        
        if updated_scan.started_at:
            print(f"   Started at: {updated_scan.started_at}")
        
        print("")
        print("🧠 Neural Brain Test Instructions:")
        print("=" * 50)
        print("1. Start your backend server:")
        print("   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("")
        print("2. Start your frontend server:")
        print("   cd frontend && npm run dev")
        print("")
        print("3. Open your browser to:")
        print("   http://localhost:3000")
        print("")
        print("4. Login with:")
        print("   Email: saifullahpathan49@gmail.com")
        print("   Password: Test1234")
        print("")
        print("5. Navigate to scan visualization:")
        print(f"   http://localhost:3000/scans/{scan.id}/visualization")
        print("")
        print("6. You should see the neural brain with:")
        print("   - 8 brain regions with different colors")
        print("   - 500+ neurons with dendrites")
        print("   - Flowing energy pulses")
        print("   - Real-time scan progress")
        print("   - Interactive 3D controls")
        print("")
        print("7. To simulate scan progress, run:")
        print(f"   cd backend && python test_scan_simulation.py {scan.id}")
        print("")
        print("🎉 Neural brain should activate and show scan progress!")
        
        return scan.id


if __name__ == "__main__":
    scan_id = asyncio.run(test_neural_brain_flow())
    print(f"\n🧠 Test scan ID: {scan_id}")
    print("Use this ID to test the neural brain visualization!")