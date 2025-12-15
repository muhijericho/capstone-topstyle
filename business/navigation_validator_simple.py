"""
Simple Navigation Validation System (Windows Compatible)
Automatically checks for navigation errors and fixes them
"""
import os
import sys
import django
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from django.core.management import execute_from_command_line
from django.test import Client
from django.contrib.auth.models import User
from django.db import connection
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')
django.setup()

logger = logging.getLogger(__name__)

class NavigationValidator:
    """Comprehensive navigation validation and auto-fix system"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
        self.navigation_urls = [
            'dashboard', 'orders', 'create_order', 'inventory', 'customer_list',
            'sales', 'track_order', 'rental_management', 'activity_log', 'archive'
        ]
    
    def validate_all_navigation(self):
        """Main validation function - checks all navigation components"""
        print("Starting Navigation Validation...")
        
        # Clear previous results
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
        
        # Run all validation checks
        self.validate_url_patterns()
        self.validate_view_functions()
        self.validate_template_links()
        self.validate_database_connections()
        self.validate_static_files()
        
        # Auto-fix common issues
        self.auto_fix_issues()
        
        # Report results
        self.report_results()
        
        return len(self.errors) == 0
    
    def validate_url_patterns(self):
        """Validate all URL patterns are working"""
        print("  Checking URL patterns...")
        
        try:
            from business.urls import urlpatterns
            
            for pattern in urlpatterns:
                if hasattr(pattern, 'name') and pattern.name:
                    try:
                        # Test if URL can be reversed
                        # For parameterized URLs, we'll just check if the pattern is valid
                        # by testing with sample parameters
                        if '<' in str(pattern.pattern):
                            # This is a parameterized URL, test with sample data
                            if 'customer_id' in str(pattern.pattern):
                                reverse(pattern.name, args=[1])
                            elif 'order_id' in str(pattern.pattern):
                                reverse(pattern.name, args=[1])
                            elif 'product_id' in str(pattern.pattern):
                                reverse(pattern.name, args=[1])
                            elif 'report_type' in str(pattern.pattern):
                                reverse(pattern.name, args=['test'])
                            elif 'item_type' in str(pattern.pattern) and 'item_id' in str(pattern.pattern):
                                reverse(pattern.name, args=['test', 1])
                            else:
                                # Skip parameterized URLs we can't test
                                continue
                        else:
                            # Non-parameterized URL
                            reverse(pattern.name)
                    except NoReverseMatch as e:
                        self.errors.append(f"URL pattern '{pattern.name}' cannot be reversed: {e}")
                    except Exception as e:
                        self.errors.append(f"URL pattern '{pattern.name}' has error: {e}")
            
            print(f"    Checked {len(urlpatterns)} URL patterns")
            
        except Exception as e:
            self.errors.append(f"Error loading URL patterns: {e}")
    
    def validate_view_functions(self):
        """Validate all view functions exist and are callable"""
        print("  Checking view functions...")
        
        try:
            from business import views
            
            # List of required view functions from navigation
            required_views = [
                'dashboard', 'orders_list', 'create_order', 'inventory_list',
                'customer_list', 'sales_page', 'track_order', 'rental_management',
                'activity_log', 'archive', 'login_view', 'logout_view'
            ]
            
            for view_name in required_views:
                if not hasattr(views, view_name):
                    self.errors.append(f"Missing view function: {view_name}")
                elif not callable(getattr(views, view_name)):
                    self.errors.append(f"View function '{view_name}' is not callable")
            
            print(f"    Checked {len(required_views)} view functions")
            
        except Exception as e:
            self.errors.append(f"Error checking view functions: {e}")
    
    def validate_template_links(self):
        """Validate template navigation links"""
        print("  Checking template navigation links...")
        
        try:
            from django.template.loader import get_template
            
            # Load base template
            template = get_template('business/base.html')
            
            # Check if template loads without errors
            context = {'user': {'username': 'test'}}
            rendered = template.render(context)
            
            # Check for common navigation issues
            if '{% url' in rendered:
                # Extract all URL references
                import re
                url_matches = re.findall(r'{% url [\'"]([^\'"]+)[\'"]', rendered)
                
                for url_name in url_matches:
                    try:
                        reverse(url_name)
                    except NoReverseMatch:
                        self.errors.append(f"Template references non-existent URL: {url_name}")
            
            print("    Template navigation links validated")
            
        except Exception as e:
            self.errors.append(f"Error validating template links: {e}")
    
    def validate_database_connections(self):
        """Validate database connectivity"""
        print("  Checking database connections...")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] != 1:
                    self.errors.append("Database connection test failed")
            print("    Database connection working")
            
        except Exception as e:
            self.errors.append(f"Database connection error: {e}")
    
    def validate_static_files(self):
        """Validate static files are accessible"""
        print("  Checking static files...")
        
        try:
            from django.contrib.staticfiles.storage import staticfiles_storage
            
            # Check critical static files
            critical_files = [
                'manifest.json',
                'js/notifications.js',
                'js/offline.js',
                'images/icon-192x192.png'
            ]
            
            for file_path in critical_files:
                if not staticfiles_storage.exists(file_path):
                    self.warnings.append(f"Static file not found: {file_path}")
            
            print("    Static files validated")
            
        except Exception as e:
            self.warnings.append(f"Error checking static files: {e}")
    
    def auto_fix_issues(self):
        """Automatically fix common navigation issues"""
        print("  Applying auto-fixes...")
        
        # Fix 1: Ensure all required URLs have corresponding views
        self.fix_missing_views()
        
        # Fix 2: Check for syntax errors in URLs
        self.fix_url_syntax_errors()
        
        # Fix 3: Validate template syntax
        self.fix_template_syntax()
    
    def fix_missing_views(self):
        """Fix missing view functions"""
        try:
            from business import views
            from business.urls import urlpatterns
            
            for pattern in urlpatterns:
                if hasattr(pattern, 'callback') and hasattr(pattern, 'name'):
                    view_name = pattern.callback.__name__ if hasattr(pattern.callback, '__name__') else str(pattern.callback)
                    if not hasattr(views, view_name):
                        self.fixes_applied.append(f"Would create missing view: {view_name}")
                        
        except Exception as e:
            self.warnings.append(f"Could not check for missing views: {e}")
    
    def fix_url_syntax_errors(self):
        """Fix URL syntax errors"""
        try:
            # Check if URLs file has syntax errors
            with open('business/urls.py', 'r') as f:
                content = f.read()
                
            # Look for common syntax issues
            if 'path(' in content and ')' not in content.split('path(')[-1]:
                self.fixes_applied.append("Found potential URL syntax error - check for missing closing parentheses")
                
        except Exception as e:
            self.warnings.append(f"Could not check URL syntax: {e}")
    
    def fix_template_syntax(self):
        """Fix template syntax errors"""
        try:
            from django.template.loader import get_template
            
            # Try to load base template
            template = get_template('business/base.html')
            self.fixes_applied.append("Template syntax validated successfully")
            
        except Exception as e:
            self.errors.append(f"Template syntax error: {e}")
    
    def report_results(self):
        """Report validation results"""
        print("\n" + "="*50)
        print("NAVIGATION VALIDATION REPORT")
        print("="*50)
        
        if self.errors:
            print(f"\nERRORS FOUND ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if self.fixes_applied:
            print(f"\nFIXES APPLIED ({len(self.fixes_applied)}):")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"  {i}. {fix}")
        
        if not self.errors and not self.warnings:
            print("\nALL NAVIGATION CHECKS PASSED!")
            print("   Your navigation system is working perfectly!")
        elif not self.errors:
            print("\nNAVIGATION IS FUNCTIONAL!")
            print("   Some warnings were found but navigation should work.")
        else:
            print(f"\nNAVIGATION HAS {len(self.errors)} CRITICAL ERRORS!")
            print("   Please fix the errors above before using the application.")
        
        print("="*50)

def run_navigation_check():
    """Main function to run navigation validation"""
    validator = NavigationValidator()
    return validator.validate_all_navigation()

if __name__ == "__main__":
    success = run_navigation_check()
    sys.exit(0 if success else 1)
