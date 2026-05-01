import os

def setup_nsl_kdd():
    """Quick setup for NSL-KDD system"""
    print("Setting up NSL-KDD Network Security System")
    print("="*50)
    
    # Create directories - using your NSL-KDD folder name
    directories = [
        'datasets/network_security/NSL-KDD',  # Changed to match your folder structure
        'backend/models/network_security',
        'backend/modules/network_security',
        'logs/network_security'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created: {directory}")
    
    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Place your NSL-KDD files in datasets/NSL-KDD/:")
    print("   - KDDTrain+.txt (or .csv)")
    print("   - KDDTest+.txt (or .csv)")
    print("2. Run: python backend/modules/network_security/nsl_train.py")
    print("3. Test: python backend/modules/network_security/nsl_test.py")

if __name__ == "__main__":
    setup_nsl_kdd()