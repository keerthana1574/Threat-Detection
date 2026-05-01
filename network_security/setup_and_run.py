# backend/modules/network_security/setup_and_run.py
import os
import subprocess
import sys

def setup_network_security():
    """Complete setup script for network security module"""
    
    print("Network Security Module Setup")
    print("="*50)
    
    # Check if running with admin privileges (required for packet capture)
    if os.name == 'nt':  # Windows
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Warning: Administrator privileges may be required for packet capture")
            print("Consider running as administrator for full functionality")
    
    # Install additional dependencies if needed
    try:
        import scapy
        print("✓ Scapy available for packet capture")
    except ImportError:
        print("Installing scapy for packet capture...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'scapy'])
    
    # Create directory structure
    directories = [
        'datasets/network_security',
        'backend/models/network_security',
        'logs/network_security'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Download dataset
    from backend.modules.network_security.nsl_data_preprocessor import NetworkDataPreprocessor
    preprocessor = NetworkDataPreprocessor()
    
    print("\nDownloading KDD Cup dataset...")
    success = preprocessor.download_kdd_dataset()
    
    if success:
        print("✓ Dataset ready for training")
    else:
        print("✗ Dataset download failed - please download manually")
    
    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Run: python backend/modules/network_security/train.py")
    print("2. Run: python backend/modules/network_security/test.py")
    print("3. For real-time monitoring: python backend/modules/network_security/monitor.py")

if __name__ == "__main__":
    setup_network_security()
