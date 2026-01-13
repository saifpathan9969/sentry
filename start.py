#!/usr/bin/env python3
"""
Startup script for Render deployment
This ensures the correct working directory and Python path
"""
import os
import sys
import subprocess

# Get the project root directory
project_root = os.path.dirname(__file__)
backend_dir = os.path.join(project_root, 'backend')

print(f"🚀 Starting Sentry Security API")
print(f"📁 Project root: {project_root}")
print(f"📁 Backend directory: {backend_dir}")

# Verify backend directory exists
if not os.path.exists(backend_dir):
    print(f"❌ Backend directory not found: {backend_dir}")
    sys.exit(1)

# Verify app directory exists
app_dir = os.path.join(backend_dir, 'app')
if not os.path.exists(app_dir):
    print(f"❌ App directory not found: {app_dir}")
    sys.exit(1)

# Verify main.py exists
main_py = os.path.join(app_dir, 'main.py')
if not os.path.exists(main_py):
    print(f"❌ main.py not found: {main_py}")
    sys.exit(1)

print(f"✅ All required files found")

# Change to backend directory
os.chdir(backend_dir)
print(f"📁 Changed working directory to: {os.getcwd()}")

# Add backend to Python path
sys.path.insert(0, backend_dir)
print(f"🐍 Added to Python path: {backend_dir}")

# Get port from environment
port = os.environ.get('PORT', '8000')
print(f"🌐 Using port: {port}")

# Test import before starting server
try:
    print("🧪 Testing imports...")
    import app.main
    print("✅ Import test successful")
except ImportError as e:
    print(f"❌ Import test failed: {e}")
    print(f"🐍 Current Python path: {sys.path}")
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"📂 Directory contents: {os.listdir('.')}")
    if os.path.exists('app'):
        print(f"📂 App directory contents: {os.listdir('app')}")
    sys.exit(1)

# Start uvicorn
cmd = [
    sys.executable, '-m', 'uvicorn', 
    'app.main:app', 
    '--host', '0.0.0.0', 
    '--port', port
]

print(f"⚡ Starting server with command: {' '.join(cmd)}")
print("🚀 Server starting...")

# Execute uvicorn
try:
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"❌ Server failed to start: {e}")
    sys.exit(1)