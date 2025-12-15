"""
Quick script to test email configuration
Run: python test_email_config.py
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
import random
import string

def test_email_config():
    print("\n" + "="*60)
    print("TopStyle Business - Email Configuration Test")
    print("="*60 + "\n")
    
    # Check configuration
    print("Email Configuration:")
    print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or 'NOT SET ⚠'}")
    print(f"  EMAIL_HOST_PASSWORD: {'SET ✓' if settings.EMAIL_HOST_PASSWORD else 'NOT SET ⚠'}")
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL or 'NOT SET ⚠'}")
    print()
    
    # Validate
    if not settings.EMAIL_HOST_USER:
        print("❌ ERROR: EMAIL_HOST_USER is not set!")
        print("   Please add EMAIL_HOST_USER=your-email@gmail.com to your .env file")
        return False
    
    if not settings.EMAIL_HOST_PASSWORD:
        print("❌ ERROR: EMAIL_HOST_PASSWORD is not set!")
        print("   Please add EMAIL_HOST_PASSWORD=your-app-password to your .env file")
        print("   See GMAIL_SETUP.md for instructions on generating an App Password")
        return False
    
    # Get recipient email
    recipient = input("Enter recipient email address to test: ").strip()
    if not recipient:
        print("❌ No email address provided")
        return False
    
    # Generate test code
    test_code = ''.join(random.choices(string.digits, k=6))
    
    print(f"\nSending test email to {recipient}...")
    print(f"Test verification code: {test_code}\n")
    
    try:
        subject = 'TopStyle Business - Test Email'
        message = f"""This is a test email from TopStyle Business Management System.

Your test verification code is: {test_code}

If you received this email, your email configuration is working correctly!

Best regards,
TopStyle Business Team"""
        
        from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
        
        result = send_mail(
            subject,
            message,
            from_email,
            [recipient],
            fail_silently=False,
        )
        
        if result:
            print("✅ SUCCESS! Test email sent successfully!")
            print(f"   Please check {recipient} (including spam folder)")
            print(f"   Test code: {test_code}")
            return True
        else:
            print("⚠️  WARNING: Email send returned False")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR: Failed to send email")
        print(f"   Error: {error_msg}\n")
        
        if 'authentication failed' in error_msg.lower() or 'invalid credentials' in error_msg.lower():
            print("Troubleshooting:")
            print("  1. Make sure you have enabled 2-Factor Authentication on your Google account")
            print("  2. Generate a Gmail App Password (not your regular password)")
            print("  3. Use the 16-character app password in your .env file")
            print("  4. See GMAIL_SETUP.md for detailed instructions")
        elif 'connection' in error_msg.lower():
            print("Troubleshooting:")
            print("  1. Check your internet connection")
            print("  2. Verify Gmail SMTP settings are correct")
            print("  3. Check if your firewall is blocking the connection")
        
        return False

if __name__ == '__main__':
    try:
        success = test_email_config()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

























