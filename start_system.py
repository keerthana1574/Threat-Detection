#!/usr/bin/env python3
"""
AI Cybersecurity Threat Detection System - Startup Script
Comprehensive system initialization and health checks
"""

import os
import sys
import time
import subprocess
import platform
from datetime import datetime
import requests
import json

class SystemStarter:
    def __init__(self):
        self.system_os = platform.system()
        self.python_version = sys.version_info
        self.startup_time = datetime.now()
        self.checks_passed = 0
        self.total_checks = 0

    def run_startup_sequence(self):
        """Run complete system startup and verification"""
        print(">> AI Cybersecurity Threat Detection System")
        print("=" * 60)
        print(f"OS: {self.system_os}")
        print(f"Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print(f"Startup Time: {self.startup_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Run all checks
        checks = [
            ("Environment Setup", self.check_environment),
            ("Dependencies", self.check_dependencies),
            ("Model Files", self.check_model_files),
            ("Configuration", self.check_configuration),
            ("Database Connectivity", self.check_database),
            ("API Keys", self.check_api_keys),
            ("System Permissions", self.check_permissions),
        ]

        for check_name, check_func in checks:
            self.total_checks += 1
            print(f"\n🔍 Checking {check_name}...")
            try:
                if check_func():
                    print(f"✅ {check_name}: PASSED")
                    self.checks_passed += 1
                else:
                    print(f"❌ {check_name}: FAILED")
            except Exception as e:
                print(f"💥 {check_name}: ERROR - {e}")

        # Start the application if checks pass
        if self.checks_passed >= self.total_checks * 0.8:  # 80% pass rate
            print(f"\n🎉 System Health: {self.checks_passed}/{self.total_checks} checks passed")
            print("🚀 Starting application...")
            self.start_application()
        else:
            print(f"\n🚨 System Health: {self.checks_passed}/{self.total_checks} checks passed")
            print("❌ Too many checks failed. Please fix issues before starting.")
            sys.exit(1)

    def check_environment(self):
        """Check Python environment and virtual environment"""
        try:
            # Check if we're in a virtual environment
            in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            if in_venv:
                print("   📦 Virtual environment: ACTIVE")
            else:
                print("   ⚠️  Virtual environment: NOT DETECTED (recommended)")

            # Check Python version
            if self.python_version >= (3, 8):
                print(f"   🐍 Python version: {sys.version} (COMPATIBLE)")
                return True
            else:
                print(f"   ❌ Python version: {sys.version} (INCOMPATIBLE - need 3.8+)")
                return False

        except Exception as e:
            print(f"   💥 Environment check failed: {e}")
            return False

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        required_packages = [
            'flask', 'flask_cors', 'flask_socketio', 'numpy', 'pandas',
            'scikit-learn', 'tensorflow', 'torch', 'transformers',
            'tweepy', 'requests', 'beautifulsoup4', 'scapy', 'psutil'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package} (MISSING)")
                missing_packages.append(package)

        if missing_packages:
            print(f"   💡 Install missing packages: pip install {' '.join(missing_packages)}")
            return False

        return True

    def check_model_files(self):
        """Check if all required model files exist"""
        model_paths = [
            'backend/models/cyberbullying/tfidf_vectorizer.pkl',
            'backend/models/cyberbullying/naive_bayes_model.pkl',
            'backend/models/fake_news/tfidf_vectorizer.pkl',
            'backend/models/fake_news/random_forest_model.pkl',
        ]

        missing_models = []
        for model_path in model_paths:
            if os.path.exists(model_path):
                print(f"   ✅ {model_path}")
            else:
                print(f"   ❌ {model_path} (MISSING)")
                missing_models.append(model_path)

        if missing_models:
            print("   💡 Some models are missing. The system will use fallback detection.")
            return True  # Allow startup with missing models

        return True

    def check_configuration(self):
        """Check configuration files and environment variables"""
        try:
            # Check .env file
            if os.path.exists('.env'):
                print("   ✅ .env file found")
            else:
                print("   ⚠️  .env file not found (using defaults)")

            # Check critical directories
            directories = ['backend', 'frontend', 'logs']
            for directory in directories:
                if os.path.exists(directory):
                    print(f"   ✅ {directory}/ directory")
                else:
                    print(f"   ❌ {directory}/ directory (MISSING)")
                    os.makedirs(directory, exist_ok=True)
                    print(f"   🔧 Created {directory}/ directory")

            return True

        except Exception as e:
            print(f"   💥 Configuration check failed: {e}")
            return False

    def check_database(self):
        """Check database connectivity (if configured)"""
        try:
            # For now, we'll skip database checks as they're optional
            print("   ⚠️  Database connectivity: SKIPPED (optional)")
            return True

        except Exception as e:
            print(f"   💥 Database check failed: {e}")
            return False

    def check_api_keys(self):
        """Check if API keys are configured"""
        try:
            from dotenv import load_dotenv
            load_dotenv()

            # Check X (Twitter) API keys
            twitter_keys = [
                'TWITTER_API_KEY',
                'TWITTER_API_SECRET',
                'TWITTER_ACCESS_TOKEN',
                'TWITTER_ACCESS_SECRET',
                'TWITTER_BEARER_TOKEN'
            ]

            twitter_configured = all(os.getenv(key) for key in twitter_keys)

            if twitter_configured:
                print("   ✅ X (Twitter) API keys: CONFIGURED")
            else:
                print("   ⚠️  X (Twitter) API keys: NOT CONFIGURED (social media monitoring disabled)")

            # System will work without API keys, just with limited functionality
            return True

        except Exception as e:
            print(f"   💥 API key check failed: {e}")
            return True  # Don't fail startup for missing API keys

    def check_permissions(self):
        """Check system permissions for network monitoring"""
        try:
            # Check if we can write to logs directory
            logs_dir = 'logs'
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)

            test_file = os.path.join(logs_dir, 'test_permissions.txt')
            with open(test_file, 'w') as f:
                f.write('Permission test')
            os.remove(test_file)

            print("   ✅ File system permissions: OK")

            # Check network permissions (platform-specific)
            if self.system_os == "Windows":
                print("   ⚠️  Network monitoring: May require administrator privileges")
            elif self.system_os in ["Linux", "Darwin"]:
                print("   ⚠️  Network monitoring: May require sudo for raw sockets")

            return True

        except Exception as e:
            print(f"   💥 Permission check failed: {e}")
            return False

    def start_application(self):
        """Start the main application"""
        try:
            print("\n🚀 Starting AI Cybersecurity Threat Detection System...")
            print("📡 Server will be available at: http://localhost:5000")
            print("📊 Dashboard will be available at: http://localhost:5000/dashboard")
            print("\n⚡ Press Ctrl+C to stop the system")
            print("-" * 60)

            # Import and run the main application
            os.environ['FLASK_APP'] = 'app.py'

            # Add current directory to Python path
            if os.getcwd() not in sys.path:
                sys.path.insert(0, os.getcwd())

            # Import the Flask app
            from app import app, socketio

            # Run with SocketIO support
            socketio.run(
                app,
                debug=False,
                host='0.0.0.0',
                port=5000,
                use_reloader=False
            )

        except KeyboardInterrupt:
            print("\n\n🛑 System shutdown requested by user")
            print("👋 Thank you for using AI Cybersecurity Threat Detection System!")
            sys.exit(0)

        except Exception as e:
            print(f"\n💥 Failed to start application: {e}")
            print("\n🔧 Troubleshooting tips:")
            print("1. Check if port 5000 is available")
            print("2. Verify all dependencies are installed")
            print("3. Run: pip install -r requirements.txt")
            print("4. Check the error logs for more details")
            sys.exit(1)

    def create_desktop_shortcut(self):
        """Create a desktop shortcut for easy access"""
        try:
            if self.system_os == "Windows":
                import winshell
                from win32com.client import Dispatch

                desktop = winshell.desktop()
                path = os.path.join(desktop, "AI Cybersecurity System.lnk")
                target = sys.executable
                wDir = os.getcwd()
                icon = sys.executable

                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = target
                shortcut.Arguments = f'"{os.path.join(wDir, "start_system.py")}"'
                shortcut.WorkingDirectory = wDir
                shortcut.IconLocation = icon
                shortcut.save()

                print(f"🔗 Desktop shortcut created: {path}")

        except Exception as e:
            print(f"⚠️  Could not create desktop shortcut: {e}")

def print_welcome_banner():
    """Print welcome banner with system information"""
    banner = """
    =================================================================
    |                                                               |
    |     AI CYBERSECURITY THREAT DETECTION SYSTEM                 |
    |                                                               |
    |  Features:                                                    |
    |  - Cyberbullying Detection (Enhanced ML)                     |
    |  - Fake News Detection (Multi-model Ensemble)                |
    |  - Phishing URL Detection (Advanced Patterns)                |
    |  - SQL Injection Detection (Rule-based + ML)                 |
    |  - XSS Detection (Pattern Recognition)                       |
    |  - DDoS & Network Anomaly Detection                          |
    |  - Real-time Social Media Monitoring                         |
    |  - Interactive Web Dashboard                                  |
    |                                                               |
    |  Access: http://localhost:5000                                |
    |  Dashboard: http://localhost:5000/dashboard                   |
    |                                                               |
    =================================================================
    """
    print(banner)

def main():
    """Main startup function"""
    print_welcome_banner()

    # Check if running as script
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'test':
            print("🧪 Running comprehensive tests...")
            os.system(f"{sys.executable} test_comprehensive.py")
            return

        elif command == 'help':
            print("""
🆘 AI Cybersecurity System - Help

Usage:
  python start_system.py          # Start the system
  python start_system.py test     # Run comprehensive tests
  python start_system.py help     # Show this help message

System Files:
  app.py                          # Main application
  test_comprehensive.py           # Test suite
  requirements.txt                # Dependencies
  .env                           # Configuration
  DEPLOYMENT.md                   # Deployment guide

Directories:
  backend/                        # Detection modules
  frontend/                       # Web interface
  logs/                          # System logs

For more information, see DEPLOYMENT.md
            """)
            return

    # Start the system
    starter = SystemStarter()
    starter.run_startup_sequence()

if __name__ == "__main__":
    main()