#!/usr/bin/env python3
# Setup script for Champion Reverse Weave Monitor Bot

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install requirements")
        sys.exit(1)

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('env_template.txt'):
            shutil.copy('env_template.txt', '.env')
            print("✓ Created .env file from template")
            print("⚠️  Please edit .env file with your email configuration")
        else:
            print("⚠️  No env_template.txt found, please create .env manually")
    else:
        print("✓ .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created {directory} directory")

def test_imports():
    """Test if all modules can be imported"""
    try:
        import requests
        import bs4
        import schedule
        import dotenv
        import fake_useragent
        print("✓ All required modules can be imported")
    except ImportError as e:
        print(f"Error: Failed to import module: {e}")
        sys.exit(1)

def main():
    print("🏆 Champion Reverse Weave Monitor Bot Setup")
    print("=" * 50)
    
    check_python_version()
    install_requirements()
    create_env_file()
    create_directories()
    test_imports()
    
    print("\n" + "=" * 50)
    print("✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your email configuration")
    print("2. Run: python main.py")
    print("\nFor Gmail, you'll need to:")
    print("- Enable 2-factor authentication")
    print("- Generate an app password")
    print("- Use the app password in EMAIL_PASSWORD")

if __name__ == "__main__":
    main()
