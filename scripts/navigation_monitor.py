#!/usr/bin/env python3
"""
Navigation Monitoring Script
Continuously monitors navigation health and auto-fixes issues
"""
import os
import sys
import time
import requests
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')
import django
django.setup()

class NavigationMonitor:
    """Continuous navigation monitoring and auto-fix system"""
    
    def __init__(self, server_url="http://127.0.0.1:8000", check_interval=30):
        self.server_url = server_url
        self.check_interval = check_interval
        self.last_check = None
        self.error_count = 0
        self.max_errors = 5
        
    def check_navigation_health(self):
        """Check navigation health via API"""
        try:
            response = requests.get(f"{self.server_url}/api/quick-nav-check/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'ok'
            return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def run_full_validation(self):
        """Run full navigation validation"""
        try:
            from business.navigation_validator import NavigationValidator
            validator = NavigationValidator()
            return validator.validate_all_navigation()
        except Exception as e:
            print(f"❌ Full validation failed: {e}")
            return False
    
    def auto_fix_navigation(self):
        """Attempt to auto-fix navigation issues"""
        print("🔧 Attempting to auto-fix navigation issues...")
        
        try:
            # Run Django check command
            import subprocess
            result = subprocess.run([
                sys.executable, 'manage.py', 'check_navigation', '--fix'
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Auto-fix completed successfully!")
                return True
            else:
                print(f"❌ Auto-fix failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Auto-fix error: {e}")
            return False
    
    def log_status(self, status, message=""):
        """Log status with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_icon = "✅" if status else "❌"
        print(f"[{timestamp}] {status_icon} {message}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("🚀 Starting Navigation Monitor...")
        print(f"   Server: {self.server_url}")
        print(f"   Check Interval: {self.check_interval} seconds")
        print("   Press Ctrl+C to stop")
        print("="*60)
        
        try:
            while True:
                # Quick health check
                is_healthy = self.check_navigation_health()
                
                if is_healthy:
                    self.log_status(True, "Navigation is healthy")
                    self.error_count = 0
                else:
                    self.error_count += 1
                    self.log_status(False, f"Navigation issue detected (Error #{self.error_count})")
                    
                    # If too many errors, run full validation and auto-fix
                    if self.error_count >= self.max_errors:
                        print("🔍 Running full navigation validation...")
                        if not self.run_full_validation():
                            print("🔧 Running auto-fix...")
                            if self.auto_fix_navigation():
                                self.error_count = 0
                                print("✅ Navigation issues resolved!")
                            else:
                                print("❌ Auto-fix failed. Manual intervention required.")
                
                self.last_check = datetime.now()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Navigation monitor stopped by user")
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Navigation Monitor')
    parser.add_argument('--server', default='http://127.0.0.1:8000', 
                       help='Server URL to monitor')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in seconds')
    parser.add_argument('--once', action='store_true',
                       help='Run check once and exit')
    
    args = parser.parse_args()
    
    monitor = NavigationMonitor(args.server, args.interval)
    
    if args.once:
        # Run single check
        print("🔍 Running single navigation check...")
        is_healthy = monitor.check_navigation_health()
        if is_healthy:
            print("✅ Navigation is healthy!")
            sys.exit(0)
        else:
            print("❌ Navigation has issues!")
            if monitor.run_full_validation():
                print("✅ Full validation passed!")
            else:
                print("❌ Full validation failed!")
                monitor.auto_fix_navigation()
            sys.exit(1)
    else:
        # Run continuous monitoring
        monitor.monitor_loop()

if __name__ == "__main__":
    main()
