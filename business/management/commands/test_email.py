"""
Management command to test email configuration and send a test email
Usage: python manage.py test_email recipient@example.com
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
import random
import string


class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient',
            type=str,
            help='Email address to send test email to',
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        
        # Check email configuration
        self.stdout.write('\n=== Email Configuration Check ===')
        self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or "NOT SET"}')
        self.stdout.write(f'EMAIL_HOST_PASSWORD: {"SET" if settings.EMAIL_HOST_PASSWORD else "NOT SET"}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL or "NOT SET"}')
        self.stdout.write('')
        
        # Validate configuration
        if not settings.EMAIL_HOST_USER:
            raise CommandError('ERROR: EMAIL_HOST_USER is not set. Please add it to your .env file.')
        
        if not settings.EMAIL_HOST_PASSWORD:
            raise CommandError('ERROR: EMAIL_HOST_PASSWORD is not set. Please add it to your .env file.')
        
        # Generate test code
        test_code = ''.join(random.choices(string.digits, k=6))
        
        # Send test email
        self.stdout.write(f'Attempting to send test email to {recipient}...')
        
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
                self.stdout.write(self.style.SUCCESS(f'\n✓ SUCCESS! Test email sent to {recipient}'))
                self.stdout.write(self.style.SUCCESS(f'Test code: {test_code}'))
                self.stdout.write('\nPlease check your email (including spam folder) to verify receipt.')
            else:
                self.stdout.write(self.style.WARNING('\n⚠ WARNING: Email send returned False'))
                
        except Exception as e:
            error_msg = str(e)
            self.stdout.write(self.style.ERROR(f'\n✗ ERROR: Failed to send email'))
            self.stdout.write(self.style.ERROR(f'Error: {error_msg}'))
            
            if 'authentication failed' in error_msg.lower() or 'invalid credentials' in error_msg.lower():
                self.stdout.write('\nTroubleshooting:')
                self.stdout.write('1. Make sure you have enabled 2-Factor Authentication on your Google account')
                self.stdout.write('2. Generate a Gmail App Password (not your regular password)')
                self.stdout.write('3. Use the 16-character app password in your .env file')
                self.stdout.write('4. See GMAIL_SETUP.md for detailed instructions')
            elif 'connection' in error_msg.lower():
                self.stdout.write('\nTroubleshooting:')
                self.stdout.write('1. Check your internet connection')
                self.stdout.write('2. Verify Gmail SMTP settings are correct')
                self.stdout.write('3. Check if your firewall is blocking the connection')
            
            raise CommandError(f'Email sending failed: {error_msg}')

























