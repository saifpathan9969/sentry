#!/usr/bin/env python3
"""
Fixed startup script for Render deployment
Works with actual Render directory structure
"""
import os
import sys
import traceback

def main():
    """Main startup function"""
    print("🚀 SENTRY SECURITY API STARTUP")
    print("=" * 50)
    
    # Print current environment
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    print(f"🐍 Python executable: {sys.executable}")
    
    # List current directory contents
    print("\n📂 Current directory contents:")
    try:
        for item in sorted(os.listdir('.')):
            item_path = os.path.join('.', item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
                # If it's backend directory, show its contents too
                if item == 'backend':
                    try:
                        backend_contents = os.listdir(item_path)
                        for sub_item in sorted(backend_contents):
                            sub_path = os.path.join(item_path, sub_item)
                            if os.path.isdir(sub_path):
                                print(f"    📁 {sub_item}/")
                            else:
                                print(f"    📄 {sub_item}")
                    except:
                        pass
            else:
                print(f"  📄 {item}")
    except Exception as e:
        print(f"  ❌ Error listing directory: {e}")
    
    # Strategy: Find where the backend/app structure is
    possible_locations = [
        # Case 1: We're in root, backend is subdirectory
        ('backend', 'backend/app'),
        # Case 2: We're already in backend
        ('.', 'app'),
        # Case 3: App is directly in current directory
        ('.', '.'),
    ]
    
    working_dir = None
    app_location = None
    
    for work_dir, app_dir in possible_locations:
        full_work_path = os.path.abspath(work_dir)
        full_app_path = os.path.join(full_work_path, app_dir.replace('backend/', '').replace('backend', ''))
        main_py_path = os.path.join(full_app_path, 'main.py')
        
        print(f"\n🔍 Checking location:")
        print(f"  Work dir: {full_work_path}")
        print(f"  App dir: {full_app_path}")
        print(f"  Main.py: {main_py_path}")
        
        if os.path.exists(main_py_path):
            working_dir = full_work_path
            app_location = app_dir.replace('backend/', '').replace('backend', '') if app_dir != '.' else 'app'
            print(f"  ✅ Found main.py!")
            break
        else:
            print(f"  ❌ main.py not found")
    
    if not working_dir:
        print("\n❌ Could not find backend/app/main.py anywhere!")
        print("📂 Please check your repository structure")
        return False
    
    # Change to working directory
    if working_dir != current_dir:
        os.chdir(working_dir)
        print(f"\n📁 Changed to working directory: {os.getcwd()}")
    
    # Add working directory to Python path
    if working_dir not in sys.path:
        sys.path.insert(0, working_dir)
        print(f"🐍 Added to Python path: {working_dir}")
    
    # Get port from environment
    port = os.environ.get('PORT', '8000')
    print(f"🌐 Using port: {port}")
    
    # Test import
    print(f"\n🧪 Testing import of {app_location}.main...")
    try:
        if app_location == 'app':
            import app.main
            module_name = 'app.main:app'
        else:
            # Direct import
            import main
            module_name = 'main:app'
        print("✅ Import successful!")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("📍 Traceback:")
        traceback.print_exc()
        return False
    
    # Start uvicorn
    print(f"\n⚡ Starting uvicorn server...")
    print(f"  Module: {module_name}")
    print(f"  Host: 0.0.0.0")
    print(f"  Port: {port}")
    print(f"  Working dir: {os.getcwd()}")
    
    try:
        import uvicorn
        uvicorn.run(
            module_name,
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