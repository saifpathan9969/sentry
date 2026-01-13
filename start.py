#!/usr/bin/env python3
"""
Startup script for AI Pentest Brain Web Service
"""
import os
import sys

print("🧠 AI PENTEST BRAIN WEB SERVICE STARTUP")
print("=" * 50)

current_dir = os.getcwd()
print(f"📁 Working directory: {current_dir}")

# List files to confirm we have the pentest brain
print("\n📂 Available files:")
for item in sorted(os.listdir('.')):
    if item.endswith('.py'):
        print(f"  📄 {item}")

# Check for required files
required_files = [
    'ai_pentest_brain_complete.py',
    'pentest_brain_web.py'
]

missing_files = []
for file in required_files:
    if os.path.exists(file):
        print(f"✅ Found: {file}")
    else:
        print(f"❌ Missing: {file}")
        missing_files.append(file)

if missing_files:
    print(f"\n❌ Missing required files: {missing_files}")
    sys.exit(1)

# Add current directory to Python path
sys.path.insert(0, current_dir)
print(f"🐍 Added to Python path: {current_dir}")

# Get port
port = os.environ.get('PORT', '8000')
print(f"🌐 Starting on port: {port}")

# Test import
print("\n🧪 Testing imports...")
try:
    import pentest_brain_web
    print("✅ pentest_brain_web imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Start the web service
print("\n🚀 Starting AI Pentest Brain Web Service...")
import uvicorn
uvicorn.run("pentest_brain_web:app", host="0.0.0.0", port=int(port), log_level="info")