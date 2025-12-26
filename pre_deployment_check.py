#!/usr/bin/env python3
"""
Pre-deployment validation script
Checks everything before deploying to Railway
"""

import os
import sys
import importlib.util
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def check_python_syntax():
    """Check Python syntax for all Python files"""
    print_header("Checking Python Syntax")
    
    python_files = [
        "main.py",
        "ebay_selenium_scraper.py",
        "depop_selenium_scraper.py",
        "test_local.py"
    ]
    
    errors = []
    for file in python_files:
        if not os.path.exists(file):
            print_warning(f"{file} not found (may be optional)")
            continue
            
        try:
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print_success(f"{file} - Syntax OK")
        except SyntaxError as e:
            print_error(f"{file} - Syntax error: {e}")
            errors.append((file, e))
    
    return len(errors) == 0

def check_imports():
    """Check if all required modules can be imported"""
    print_header("Checking Python Imports")
    
    required_modules = [
        "requests",
        "bs4",
        "schedule",
        "dotenv",
        "selenium",
        "webdriver_manager",
        "sqlite3",
        "smtplib",
        "email"
    ]
    
    missing = []
    for module in required_modules:
        try:
            if module == "bs4":
                __import__("bs4")
            elif module == "dotenv":
                __import__("dotenv")
            elif module == "webdriver_manager":
                __import__("webdriver_manager")
            else:
                __import__(module)
            print_success(f"{module} - Available")
        except ImportError:
            print_error(f"{module} - Missing")
            missing.append(module)
    
    if missing:
        print_warning(f"Missing modules: {', '.join(missing)}")
        print_warning("Run: pip install -r requirements.txt")
    
    return len(missing) == 0

def check_search_terms():
    """Check if search terms are configured"""
    print_header("Checking Search Terms")
    
    try:
        from main import SEARCH_TERMS
        
        print_success(f"Found {len(SEARCH_TERMS)} search terms")
        
        # Check for specific items
        all_terms = ' '.join(SEARCH_TERMS).lower()
        
        checks = {
            "North Face Puffer": any("north face" in term.lower() and "puffer" in term.lower() for term in SEARCH_TERMS),
            "Pendleton": any("pendleton" in term.lower() for term in SEARCH_TERMS),
            "Black Levis": any("black" in term.lower() and "levi" in term.lower() for term in SEARCH_TERMS),
            "Champion Reverse Weave": any("champion" in term.lower() and "reverse" in term.lower() for term in SEARCH_TERMS)
        }
        
        for item, found in checks.items():
            if found:
                print_success(f"{item} - Found in search terms")
            else:
                print_warning(f"{item} - Not found in search terms")
        
        # Show first few terms
        print(f"\nFirst 5 search terms:")
        for i, term in enumerate(SEARCH_TERMS[:5], 1):
            print(f"  {i}. {term}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to check search terms: {e}")
        return False

def check_files():
    """Check if required files exist"""
    print_header("Checking Required Files")
    
    required_files = [
        "main.py",
        "ebay_selenium_scraper.py",
        "depop_selenium_scraper.py",
        "requirements.txt",
        "Dockerfile",
        "railway.json",
        "env_template.txt"
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print_success(f"{file} - Exists")
        else:
            print_error(f"{file} - Missing")
            missing.append(file)
    
    return len(missing) == 0

def check_dockerfile():
    """Check Dockerfile for common issues"""
    print_header("Checking Dockerfile")
    
    if not os.path.exists("Dockerfile"):
        print_error("Dockerfile not found")
        return False
    
    with open("Dockerfile", 'r') as f:
        content = f.read()
    
    checks = {
        "Python base image": "FROM python" in content,
        "Chrome installation": "google-chrome" in content or "chromium" in content,
        "ChromeDriver": "chromedriver" in content.lower(),
        "Requirements install": "requirements.txt" in content,
        "Main.py copy": "COPY" in content and "main.py" in content or "COPY ." in content,
        "CMD or ENTRYPOINT": "CMD" in content or "ENTRYPOINT" in content
    }
    
    all_good = True
    for check, passed in checks.items():
        if passed:
            print_success(f"{check} - OK")
        else:
            print_error(f"{check} - Missing or incorrect")
            all_good = False
    
    return all_good

def check_railway_config():
    """Check Railway configuration"""
    print_header("Checking Railway Configuration")
    
    if not os.path.exists("railway.json"):
        print_error("railway.json not found")
        return False
    
    try:
        import json
        with open("railway.json", 'r') as f:
            config = json.load(f)
        
        print_success("railway.json - Valid JSON")
        
        if "build" in config:
            print_success("Build configuration - Present")
        else:
            print_warning("Build configuration - Missing")
        
        if "deploy" in config:
            print_success("Deploy configuration - Present")
        else:
            print_warning("Deploy configuration - Missing")
        
        return True
        
    except json.JSONDecodeError as e:
        print_error(f"railway.json - Invalid JSON: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading railway.json: {e}")
        return False

def check_env_template():
    """Check environment template"""
    print_header("Checking Environment Template")
    
    if not os.path.exists("env_template.txt"):
        print_error("env_template.txt not found")
        return False
    
    with open("env_template.txt", 'r') as f:
        content = f.read()
    
    required_vars = [
        "EMAIL_USER",
        "EMAIL_PASSWORD",
        "RECIPIENT_EMAIL",
        "SMTP_SERVER",
        "SMTP_PORT"
    ]
    
    missing = []
    for var in required_vars:
        if var in content:
            print_success(f"{var} - Documented")
        else:
            print_warning(f"{var} - Not documented")
            missing.append(var)
    
    return len(missing) == 0

def check_requirements():
    """Check requirements.txt"""
    print_header("Checking Requirements")
    
    if not os.path.exists("requirements.txt"):
        print_error("requirements.txt not found")
        return False
    
    with open("requirements.txt", 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print_success(f"Found {len(lines)} dependencies")
    
    critical = ["selenium", "requests", "beautifulsoup4", "schedule", "python-dotenv"]
    found = []
    for dep in critical:
        if any(dep.lower() in line.lower() for line in lines):
            print_success(f"{dep} - Listed")
            found.append(dep)
        else:
            print_warning(f"{dep} - Not found")
    
    return len(found) == len(critical)

def check_gitignore():
    """Check if .gitignore exists and has important entries"""
    print_header("Checking .gitignore")
    
    if not os.path.exists(".gitignore"):
        print_warning(".gitignore not found (recommended to add)")
        return True  # Not critical
    
    with open(".gitignore", 'r') as f:
        content = f.read()
    
    important = [".env", "__pycache__", "*.db", "*.log", "venv/", ".venv/"]
    found = []
    for item in important:
        if item in content or item.replace("/", "") in content:
            print_success(f"{item} - Ignored")
            found.append(item)
        else:
            print_warning(f"{item} - Not in .gitignore")
    
    return True  # Not critical, just informational

def main():
    """Run all checks"""
    print("\n" + "=" * 70)
    print("  PRE-DEPLOYMENT VALIDATION CHECK")
    print("  Checking everything before Railway deployment")
    print("=" * 70)
    
    results = {
        "Python Syntax": check_python_syntax(),
        "Python Imports": check_imports(),
        "Search Terms": check_search_terms(),
        "Required Files": check_files(),
        "Dockerfile": check_dockerfile(),
        "Railway Config": check_railway_config(),
        "Env Template": check_env_template(),
        "Requirements": check_requirements(),
        "Gitignore": check_gitignore()
    }
    
    print_header("Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check}")
    
    print(f"\n  Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("  🎉 ALL CHECKS PASSED!")
        print("  Your code is ready for Railway deployment!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Make sure .env variables are set in Railway dashboard")
        print("  2. Push code to GitHub")
        print("  3. Connect Railway to your GitHub repo")
        print("  4. Railway will auto-deploy!")
        return 0
    else:
        print("\n" + "=" * 70)
        print("  ⚠️  SOME CHECKS FAILED")
        print("  Please fix the issues above before deploying")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())

