#!/usr/bin/env python3
"""
Direct startup script - goes straight to the known structure
"""
import os
import sys

print("🚀 DIRECT STARTUP FOR RENDER")
print(f"📁 Starting from: {os.getcwd()}")

# Based on the logs, we know the structure:
# /opt/render/project/src/backend/app/main.py exists
# So let's go directly there

backend_path = os.path.join(os.getcwd(), 'backend')
app_path = os.path.join(backend_path, 'app')
main_py_path = os.path.join(app_path, 'main.py')

print(f"📁 Backend path: {backend_path}")
print(f"📁 App path: {app_path}")
print(f"📄 Main.py path: {main_py_path}")

# Check if files exist
print(f"✅ Backend exists: {os.path.exists(backend_path)}")
print(f"✅ App exists: {os.path.exists(app_path)}")
print(f"✅ Main.py exists: {os.path.exists(main_py_path)}")

if not os.path.exists(main_py_path):
    print("❌ main.py not found - listing actual contents:")
    if os.path.exists(backend_path):
        print("Backend contents:")
        for item in os.listdir(backend_path):
            print(f"  {item}")
        if os.path.exists(app_path):
            print("App contents:")
            for item in os.listdir(app_path):
                print(f"  {item}")
    sys.exit(1)

# Change to backend directory
os.chdir(backend_path)
print(f"📁 Changed to: {os.getcwd()}")

# Add to Python path
sys.path.insert(0, os.getcwd())
print(f"🐍 Added to Python path: {os.getcwd()}")

# Test import
print("🧪 Testing import...")
try:
    import app.main
    print("✅ Import successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Get port
port = os.environ.get('PORT', '8000')
print(f"🌐 Starting on port: {port}")

# Start server
print("🚀 Starting uvicorn...")
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=int(port), log_level="info")