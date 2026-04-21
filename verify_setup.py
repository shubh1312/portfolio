#!/usr/bin/env python3
"""
Quick verification script for Option 3 hybrid setup
Tests if all dependencies are installed and ready
"""

import sys
import subprocess
from pathlib import Path

def check_python_packages():
    """Check if all Python packages are installed"""
    print("\n🐍 Checking Python packages...")
    
    required = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'pandas': 'Pandas (should already be installed)',
        'requests': 'Requests (should already be installed)',
    }
    
    missing = []
    for pkg, name in required.items():
        try:
            __import__(pkg)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - MISSING")
            missing.append(pkg)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("\n✅ All Python packages installed!")
    return True

def check_node_packages():
    """Check if Node.js and npm are installed"""
    print("\n📦 Checking Node.js and npm...")
    
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"  ✅ Node.js {result.stdout.strip()}")
    except FileNotFoundError:
        print("  ❌ Node.js not found")
        print("     Install from: https://nodejs.org/")
        return False
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        print(f"  ✅ npm {result.stdout.strip()}")
    except FileNotFoundError:
        print("  ❌ npm not found")
        return False
    
    return True

def check_backend_structure():
    """Check if backend files exist"""
    print("\n🔧 Checking backend structure...")
    
    files = [
        'backend/main.py',
        'backend/requirements.txt',
    ]
    
    all_exist = True
    for file in files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_exist = False
    
    if not all_exist:
        print("\n❌ Backend files missing!")
        return False
    
    print("\n✅ Backend structure OK!")
    return True

def check_frontend_structure():
    """Check if frontend files exist"""
    print("\n⚛️  Checking frontend structure...")
    
    files = [
        'frontend/Orbit Portfolio.html',
        'frontend/shell.jsx',
        'frontend/shell.css',
        'frontend/api.js',
        'frontend/package.json',
        'frontend/vite.config.js',
    ]
    
    all_exist = True
    for file in files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_exist = False
    
    if not all_exist:
        print("\n❌ Frontend files missing!")
        return False
    
    print("\n✅ Frontend structure OK!")
    return True

def check_services():
    """Check if Python services are available"""
    print("\n📚 Checking Python services...")
    
    services = [
        'services/performance_service.py',
        'services/portfolio_service.py',
        'services/market_data.py',
    ]
    
    all_exist = True
    for service in services:
        if Path(service).exists():
            print(f"  ✅ {service}")
        else:
            print(f"  ❌ {service} - MISSING")
            all_exist = False
    
    if not all_exist:
        print("\n❌ Service files missing!")
        return False
    
    print("\n✅ All services available!")
    return True

def main():
    print("=" * 60)
    print("🚀 Orbit Portfolio - Option 3 Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python", check_python_packages),
        ("Node.js", check_node_packages),
        ("Backend", check_backend_structure),
        ("Frontend", check_frontend_structure),
        ("Services", check_services),
    ]
    
    results = {}
    for name, check in checks:
        try:
            results[name] = check()
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results[name] = False
    
    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    if all(results.values()):
        print("\n" + "=" * 60)
        print("✨ All checks passed! Ready to start development")
        print("=" * 60)
        print("\n🚀 Quick Start:")
        print("   Terminal 1: python -m uvicorn backend.main:app --reload")
        print("   Terminal 2: cd frontend && npm install && npm run dev")
        print("   Browser:   http://localhost:5173")
        print("\n📚 API Docs:  http://localhost:8000/docs")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Some checks failed. Please fix the issues above.")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
