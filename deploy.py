#!/usr/bin/env python3
"""
Deployment script for Cybersecurity Dashboard
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'backend/models/cyberbullying',
        'backend/models/fake_news',
        'backend/models/network_security',
        'backend/models/web_security',
        'datasets/cyberbullying',
        'datasets/fake_news',
        'datasets/network_security',
        'datasets/web_security',
        'frontend/static/css',
        'frontend/static/js',
        'frontend/templates',
        'config'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def setup_virtual_environment():
    """Setup Python virtual environment"""
    if not os.path.exists('venv'):
        run_command('python -m venv venv', 'Creating virtual environment')
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = 'venv\\Scripts\\activate.bat && '
    else:  # Unix/Linux/Mac
        activate_script = 'source venv/bin/activate && '
    
    # Install requirements
    install_cmd = f'{activate_script}pip install --upgrade pip && pip install -r requirements.txt'
    run_command(install_cmd, 'Installing Python dependencies')

def download_nltk_data():
    """Download required NLTK data"""
    nltk_downloads = [
        'punkt',
        'stopwords',
        'wordnet',
        'omw-1.4',
        'averaged_perceptron_tagger',
        'vader_lexicon'
    ]
    
    # Determine activation script
    if os.name == 'nt':
        activate_script = 'venv\\Scripts\\activate.bat && '
    else:
        activate_script = 'source venv/bin/activate && '
    
    for data in nltk_downloads:
        cmd = f'{activate_script}python -c "import nltk; nltk.download(\'{data}\')"'
        run_command(cmd, f'Downloading NLTK data: {data}')

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        env_content = """# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=cybersecurity-dashboard-secret-key-2024

# Database
DATABASE_URL=sqlite:///cybersecurity.db

# Twitter API Keys (replace with your actual keys)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Logging
LOG_LEVEL=INFO
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("ℹ️  .env file already exists")

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        if memory.total < 4 * 1024**3:  # 4GB
            print("⚠️  Warning: Less than 4GB RAM detected. Performance may be impacted.")
        else:
            print(f"✅ Available RAM: {memory.total // (1024**3)}GB")
    except ImportError:
        print("ℹ️  Could not check memory requirements (psutil not installed)")
    
    return True

def train_models():
    """Train all ML models"""
    print("🤖 Training machine learning models...")
    
    # Determine activation script
    if os.name == 'nt':
        activate_script = 'venv\\Scripts\\activate.bat && '
    else:
        activate_script = 'source venv/bin/activate && '
    
    training_scripts = [
        ('backend/modules/cyberbullying/train.py', 'Cyberbullying Detection Models'),
        ('backend/modules/fake_news/train.py', 'Fake News Detection Models'),
        ('backend/modules/network_security/train.py', 'Network Security Models'),
        ('backend/modules/web_security/train_sql_injection.py', 'SQL Injection Detection Models'),
        ('backend/modules/web_security/train_xss.py', 'XSS Detection Models')
    ]
    
    for script, description in training_scripts:
        if os.path.exists(script):
            cmd = f'{activate_script}python {script}'
            result = run_command(cmd, f'Training {description}')
            if result is None:
                print(f"⚠️  Warning: {description} training may have failed")
        else:
            print(f"⚠️  Warning: Training script not found: {script}")

def create_systemd_service():
    """Create systemd service for Linux deployment"""
    if os.name != 'nt' and shutil.which('systemctl'):
        service_content = f"""[Unit]
Description=Cybersecurity Dashboard
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getcwd()}/venv/bin
ExecStart={os.getcwd()}/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = '/etc/systemd/system/cybersecurity-dashboard.service'
        print(f"📄 Systemd service file content (save to {service_file}):")
        print(service_content)
        print("Run the following commands as root to enable the service:")
        print("sudo systemctl daemon-reload")
        print("sudo systemctl enable cybersecurity-dashboard.service")
        print("sudo systemctl start cybersecurity-dashboard.service")

def main():
    """Main deployment function"""
    print("🚀 Starting Cybersecurity Dashboard Deployment")
    print("=" * 50)
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System requirements not met. Exiting.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create environment file
    create_env_file()
    
    # Setup virtual environment and install dependencies
    setup_virtual_environment()
    
    # Download NLTK data
    download_nltk_data()
    
    # Provide instructions for datasets
    print("\n📊 Dataset Setup Instructions:")
    print("=" * 30)
    print("1. For Cyberbullying Detection:")
    print("   - Download datasets from Kaggle and place in datasets/cyberbullying/")
    print("   - kaggle datasets download -d andrewmvd/cyberbullying-classification")
    print("   - kaggle datasets download -d datatattle/cyberbullying-detection")
    
    print("\n2. For Fake News Detection:")
    print("   - Download LIAR dataset: wget https://www.cs.ucsb.edu/~william/data/liar_dataset.zip")
    print("   - Download from Kaggle: kaggle datasets download -d clmentbisaillon/fake-and-real-news-dataset")
    
    print("\n3. For Network Security:")
    print("   - Download KDD Cup 1999: wget http://kdd.ics.uci.edu/databases/kddcup99/kddcup.data_10_percent.gz")
    
    print("\n4. For Web Security:")
    print("   - Download from Kaggle: kaggle datasets download -d sajid576/sql-injection-dataset")
    print("   - Download from Kaggle: kaggle datasets download -d syedsaqlainhussain/cross-site-scripting-xss-dataset")
    
    # Ask user if they want to train models now
    train_now = input("\n🤖 Do you want to train the ML models now? (y/n): ").lower()
    if train_now == 'y':
        train_models()
    else:
        print("ℹ️  You can train models later by running the individual training scripts")
    
    # Create systemd service (Linux only)
    create_systemd_service()
    
    print("\n🎉 Deployment completed successfully!")
    print("=" * 30)
    print("Next steps:")
    print("1. Update .env file with your actual API keys")
    print("2. Download and extract datasets as instructed above")
    print("3. Train ML models if you haven't already")
    print("4. Run the application:")
    print("   - Development: python app.py")
    print("   - Production: gunicorn --bind 0.0.0.0:5000 app:app")
    print("\n🌐 Access the dashboard at: http://localhost:5000")

if __name__ == "__main__":
    main()