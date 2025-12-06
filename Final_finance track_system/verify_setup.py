"""
Setup Verification Script
Checks if all required modules are available for the Personal Finance Tracker
"""

import sys

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def check_standard_library_modules():
    """Check if all required standard library modules are available"""
    modules = {
        'tkinter': 'GUI framework',
        'json': 'Data persistence',
        'datetime': 'Date handling',
        'os': 'File operations',
        'typing': 'Type hints'
    }
    
    all_ok = True
    for module_name, description in modules.items():
        try:
            __import__(module_name)
            print(f"✅ {module_name:12} - {description} - Available")
        except ImportError as e:
            print(f"❌ {module_name:12} - {description} - NOT AVAILABLE: {e}")
            all_ok = False
    
    return all_ok

def check_optional_modules():
    """Check if optional modules are available"""
    optional_modules = {
        'matplotlib': 'Visualization (optional)'
    }
    
    for module_name, description in optional_modules.items():
        try:
            __import__(module_name)
            print(f"✅ {module_name:12} - {description} - Available")
        except ImportError:
            print(f"⚠️  {module_name:12} - {description} - Not installed (optional)")

def check_project_files():
    """Check if required project files exist"""
    import os
    files = {
        'Project2.py': 'Main application file',
        'requirements.txt': 'Requirements file',
        'README.md': 'Documentation'
    }
    
    all_ok = True
    for filename, description in files.items():
        if os.path.exists(filename):
            print(f"✅ {filename:20} - {description} - Found")
        else:
            print(f"❌ {filename:20} - {description} - NOT FOUND")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("Personal Finance Tracker - Setup Verification")
    print("=" * 60)
    print()
    
    print("1. Checking Python Version...")
    python_ok = check_python_version()
    print()
    
    print("2. Checking Required Standard Library Modules...")
    modules_ok = check_standard_library_modules()
    print()
    
    print("3. Checking Optional Modules...")
    check_optional_modules()
    print()
    
    print("4. Checking Project Files...")
    files_ok = check_project_files()
    print()
    
    print("=" * 60)
    if python_ok and modules_ok and files_ok:
        print("✅ All checks passed! You're ready to run the application.")
        print("\nTo start the application, run:")
        print("   python Project2.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 60)

if __name__ == "__main__":
    main()


