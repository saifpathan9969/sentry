#!/usr/bin/env python3
"""
Startup script for Render deployment
This ensures the correct working directory and Python path
"""
import os
import sys
import subprocess

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

# Add backend to Python path
sys.path.insert(0, backend_dir)

# Get port from environment
port = os.environ.get('PORT', '8000')

# Start uvicorn
cmd = [
    sys.executable, '-m', 'uvicorn', 
    'app.main:app', 
    '--host', '0.0.0.0', 
    '--port', port
]

print(f"🚀 Starting Sentry Security API on port {port}")
print(f"📁 Working directory: {os.getcwd()}")
print(f"🐍 Python path: {sys.path[0]}")
print(f"⚡ Command: {' '.join(cmd)}")

# Execute uvicorn
subprocess.run(cmd)