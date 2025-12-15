"""
Django management command for navigation validation
Usage: python manage.py check_navigation
"""
from django.core.management.base import BaseCommand, CommandError
from business.navigation_validator_simple import NavigationValidator

class Command(BaseCommand):
    help = 'Check and validate navigation system for errors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix common navigation issues',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Navigation Validation...')
        )
        
        validator = NavigationValidator()
        success = validator.validate_all_navigation()
        
        if options['verbose']:
            self.stdout.write(
                self.style.SUCCESS(f'Errors: {len(validator.errors)}')
            )
            self.stdout.write(
                self.style.WARNING(f'Warnings: {len(validator.warnings)}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Fixes Applied: {len(validator.fixes_applied)}')
            )
        
        if success:
            self.stdout.write(
                self.style.SUCCESS('Navigation validation completed successfully!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Navigation validation found errors!')
            )
            raise CommandError('Navigation validation failed')
