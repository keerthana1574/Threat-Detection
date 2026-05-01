#!/usr/bin/env python3
"""
AI Cybersecurity Threat Detection System - Simple Startup Script
"""

import os
import sys
import platform
from datetime import datetime

def main():
    """Simple startup without Unicode characters"""
    print("AI Cybersecurity Threat Detection System")
    print("=" * 50)
    print(f"OS: {platform.system()}")
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Check if we can import the main app
    try:
        print("\n[INFO] Checking application...")

        # Add current directory to Python path
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

        # Try to import the main components
        print("[CHECK] Importing Flask...")
        import flask
        print("[PASS] Flask available")

        print("[CHECK] Loading main application...")
        from app import app, socketio
        print("[PASS] Application loaded successfully")

        print("\n[INFO] Starting AI Cybersecurity System...")
        print("[INFO] Server will be available at: http://localhost:5000")
        print("[INFO] Dashboard: http://localhost:5000/dashboard")
        print("\n[INFO] Press Ctrl+C to stop the system")
        print("-" * 50)

        # Run the application
        socketio.run(
            app,
            debug=False,
            host='0.0.0.0',
            port=5000,
            use_reloader=False
        )

    except KeyboardInterrupt:
        print("\n\n[INFO] System shutdown requested by user")
        print("[INFO] Thank you for using the AI Cybersecurity System!")
        sys.exit(0)

    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("[INFO] Make sure all dependencies are installed:")
        print("       pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"[ERROR] Failed to start application: {e}")
        print("\n[INFO] Troubleshooting tips:")
        print("1. Check if port 5000 is available")
        print("2. Verify all dependencies are installed")
        print("3. Run: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()