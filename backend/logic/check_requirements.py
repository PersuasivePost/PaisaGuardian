#!/usr/bin/env python3
"""
Dependency checker and installer for Fraud Detection API
Verifies all requirements are installed and installs missing ones
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.9 or higher"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Error: Python 3.9 or higher is required")
        return False
    
    print("✓ Python version is compatible")
    return True

def check_venv():
    """Check if running in a virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("✓ Running in virtual environment")
        return True
    else:
        print("⚠️  Warning: Not running in a virtual environment")
        print("   Recommended: Create and activate a virtual environment")
        print("   Run: python3 -m venv venv && source venv/bin/activate")
        return False

def read_requirements():
    """Read requirements from requirements.txt"""
    req_file = Path(__file__).parent / "requirements.txt"
    
    if not req_file.exists():
        print("❌ Error: requirements.txt not found")
        return []
    
    with open(req_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"✓ Found {len(requirements)} requirements in requirements.txt")
    return requirements

def check_package_installed(package_name):
    """Check if a package is installed"""
    # Extract package name without version specifier
    pkg = package_name.split('==')[0].split('>=')[0].split('[')[0].strip()
    
    try:
        __import__(pkg.replace('-', '_'))
        return True
    except ImportError:
        return False

def install_requirements():
    """Install all requirements from requirements.txt"""
    print("\n📦 Installing requirements...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt", 
            "--quiet"
        ])
        print("✓ All requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if env_file.exists():
        print("✓ .env file exists")
        return True
    elif env_example.exists():
        print("⚠️  .env file not found, but .env.example exists")
        print("   Creating .env from .env.example...")
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print("✓ .env file created from template")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("⚠️  No .env or .env.example file found")
        print("   The application will use default configuration")
        return False

def check_all_installed():
    """Check if all required packages are installed"""
    requirements = read_requirements()
    
    if not requirements:
        return False
    
    print("\n🔍 Checking installed packages...")
    
    missing = []
    for req in requirements:
        pkg_name = req.split('==')[0].split('>=')[0].split('[')[0].strip()
        if check_package_installed(pkg_name):
            print(f"  ✓ {pkg_name}")
        else:
            print(f"  ✗ {pkg_name} (missing)")
            missing.append(req)
    
    if missing:
        print(f"\n❌ Missing {len(missing)} package(s)")
        return False
    else:
        print("\n✓ All packages are installed")
        return True

def verify_imports():
    """Verify critical imports work"""
    print("\n🧪 Verifying critical imports...")
    
    critical_imports = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
        ('httpx', 'HTTPX'),
    ]
    
    all_ok = True
    for module, name in critical_imports:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
            all_ok = False
    
    if all_ok:
        print("\n✓ All critical imports verified")
    else:
        print("\n❌ Some imports failed")
    
    return all_ok

def main():
    """Main function"""
    print("=" * 60)
    print("Fraud Detection API - Dependency Checker")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print()
    
    # Check virtual environment
    check_venv()
    
    print()
    
    # Check if all packages are installed
    all_installed = check_all_installed()
    
    if not all_installed:
        print("\n❓ Would you like to install missing packages? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            if install_requirements():
                print("\n✓ Installation complete!")
                # Verify again
                if not check_all_installed():
                    print("\n❌ Some packages still missing after installation")
                    sys.exit(1)
            else:
                sys.exit(1)
        else:
            print("\n⚠️  Please install missing packages manually:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
    
    print()
    
    # Verify imports
    if not verify_imports():
        print("\n❌ Import verification failed")
        print("   Try reinstalling: pip install -r requirements.txt --force-reinstall")
        sys.exit(1)
    
    print()
    
    # Check .env file
    check_env_file()
    
    print()
    print("=" * 60)
    print("✅ All checks passed! The API is ready to run.")
    print("=" * 60)
    print()
    print("To start the server, run:")
    print("  python main.py")
    print("or")
    print("  uvicorn main:app --reload")
    print()

if __name__ == "__main__":
    main()
