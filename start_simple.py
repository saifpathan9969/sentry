#!/usr/bin/env python3
"""
Super simple startup - handles the exact Render structure
"""
import os
import sys

print("🚀 Simple Render Startup")
print(f"📁 Working in: {os.getcwd()}")

# List what we have
print("📂 Available files/folders:")
for item in os.listdir('.'):
    print(f"  {item}")

# The most likely scenario based on the logs:
# We're in /opt/render/project/src and need to find backend/app
if os.path.exists('backend/app/main.py'):
    print("✅ Found backend/app/main.py - using backend structure")
    os.chdir('backend')
    sys.path.insert(0, os.getcwd())
    module = 'app.main:app'
elif os.path.exists('app/main.py'):
    print("✅ Found app/main.py - using direct structure")
    sys.path.insert(0, os.getcwd())
    module = 'app.main:app'
elif os.path.exists('main.py'):
    print("✅ Found main.py - using root structure")
    sys.path.insert(0, os.getcwd())
    module = 'main:app'
else:
    print("❌ Cannot find main.py anywhere")
    sys.exit(1)

port = os.environ.get('PORT', '8000')
print(f"🌐 Starting on port {port}")
print(f"📁 Working directory: {os.getcwd()}")
print(f"🎯 Module: {module}")

# Start uvicorn directly
import uvicorn
uvicorn.run(module, host="0.0.0.0", port=int(port))