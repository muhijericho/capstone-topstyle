#!/usr/bin/env python3
"""
Quick Navigation Check Script
Easy way to validate navigation system
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main function"""
    print("🔍 TopStyle Navigation Validator")
    print("="*40)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found!")
        print("   Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment may not be activated")
        print("   Consider running: venv\\Scripts\\activate")
    
    try:
        print("🚀 Running navigation validation...")
        
        # Run the Django management command
        result = subprocess.run([
            sys.executable, 'manage.py', 'check_navigation', '--verbose'
        ], capture_output=True, text=True)
        
        print("\n" + "="*40)
        print("📊 VALIDATION RESULTS")
        print("="*40)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("\n✅ Navigation validation PASSED!")
            print("   Your navigation system is working correctly.")
            return True
        else:
            print("\n❌ Navigation validation FAILED!")
            print("   Please fix the errors above before using the application.")
            return False
            
    except Exception as e:
        print(f"❌ Error running validation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
