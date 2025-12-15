#!/usr/bin/env python3
"""
Pre-commit hook for navigation validation
Automatically runs navigation checks before commits
"""
import os
import sys
import subprocess
import django
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')
django.setup()

def run_navigation_check():
    """Run navigation validation"""
    print("🔍 Running pre-commit navigation validation...")
    
    try:
        # Run the navigation check command
        result = subprocess.run([
            sys.executable, 'manage.py', 'check_navigation', '--verbose'
        ], cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Navigation validation passed!")
            return True
        else:
            print("❌ Navigation validation failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running navigation check: {e}")
        return False

def main():
    """Main pre-commit hook function"""
    print("="*60)
    print("🚀 PRE-COMMIT NAVIGATION VALIDATION")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Are you in the project root?")
        sys.exit(1)
    
    # Run navigation check
    if run_navigation_check():
        print("\n✅ All navigation checks passed! Proceeding with commit...")
        sys.exit(0)
    else:
        print("\n❌ Navigation validation failed! Please fix errors before committing.")
        print("\nTo fix navigation issues:")
        print("1. Run: python manage.py check_navigation")
        print("2. Fix any reported errors")
        print("3. Try committing again")
        sys.exit(1)

if __name__ == "__main__":
    main()
