#!/usr/bin/env python3
"""
Fixed startup script for Render deployment
"""
import os
import sys
import traceback

def main():
    """Main startup function"""
    print("🚀 SENTRY SECURITY API STARTUP")
    print("=" * 50)
    
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    # List current directory contents to debug
    print("\n📂 Current directory contents:")
    try:
        items = sorted(os.listdir('.'))
        for item in items:
            item_path = os.path.join('.', item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
            else:
                print(f"  📄 {item}")
    except Exception as e:
        print(f"  ❌ Error listing directory: {e}")
    
    # Based on logs, we know the structure should be:
    # current_dir/backend/app/main.py
    backend_dir = os.path.join(current_dir, 'backend')
    app_dir = os.path.join(backend_dir, 'app')
    main_py = os.path.join(app_dir, 'main.py')
    
    print(f"\n🔍 Expected paths:")
    print(f"  Backend: {backend_dir}")
    print(f"  App: {app_dir}")
    print(f"  Main.py: {main_py}")
    
    print(f"\n✅ Path checks:")
    print(f"  Backend exists: {os.path.exists(backend_dir)}")
    print(f"  App exists: {os.path.exists(app_dir)}")
    print(f"  Main.py exists: {os.path.exists(main_py)}")
    
    # If backend directory exists, show its contents
    if os.path.exists(backend_dir):
        print(f"\n📂 Backend directory contents:")
        try:
            for item in sorted(os.listdir(backend_dir)):
                item_path = os.path.join(backend_dir, item)
                if os.path.isdir(item_path):
                    print(f"  📁 {item}/")
                else:
                    print(f"  📄 {item}")
        except Exception as e:
            print(f"  ❌ Error listing backend: {e}")
    
    # If app directory exists, show its contents
    if os.path.exists(app_dir):
        print(f"\n📂 App directory contents:")
        try:
            for item in sorted(os.listdir(app_dir)):
                print(f"  📄 {item}")
        except Exception as e:
            print(f"  ❌ Error listing app: {e}")
    
    # Check if main.py exists
    if not os.path.exists(main_py):
        print(f"\n❌ main.py not found at: {main_py}")
        print("🔍 This might be a file system sync issue on Render")
        return False
    
    print(f"\n✅ Found main.py at: {main_py}")
    
    # Change to backend directory
    os.chdir(backend_dir)
    print(f"📁 Changed working directory to: {os.getcwd()}")
    
    # Add to Python path
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
        print(f"🐍 Added to Python path: {backend_dir}")
    
    # Test import
    print(f"\n🧪 Testing import of app.main...")
    try:
        import app.main
        print("✅ Import successful!")
        
        # Check if FastAPI app exists
        if hasattr(app.main, 'app'):
            print("✅ FastAPI app instance found")
        else:
            print("⚠️ FastAPI app instance not found, but import worked")
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("📍 Traceback:")
        traceback.print_exc()
        
        # Show Python path for debugging
        print(f"\n🐍 Current Python path:")
        for i, path in enumerate(sys.path):
            print(f"  {i}: {path}")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected import error: {e}")
        traceback.print_exc()
        return False
    
    # Get port
    port = os.environ.get('PORT', '8000')
    print(f"\n🌐 Starting server on port: {port}")
    
    # Start uvicorn
    print("🚀 Starting uvicorn server...")
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=int(port),
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ STARTUP FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)