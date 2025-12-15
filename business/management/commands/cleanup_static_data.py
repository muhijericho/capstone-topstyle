"""
Management command to remove all static/dummy data from the system
"""
from django.core.management.base import BaseCommand
from business.static_data_manager import remove_static_data, get_static_products, get_static_orders


class Command(BaseCommand):
    help = 'Remove all static/dummy data from the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write('Scanning for static data...')
        
        # Get counts
        counts = remove_static_data(dry_run=True)
        
        if counts['products'] == 0 and counts['orders'] == 0:
            self.stdout.write(self.style.SUCCESS('No static data found. System is clean!'))
            return
        
        # Show what will be deleted
        self.stdout.write('\n' + '='*60)
        self.stdout.write('STATIC DATA FOUND:')
        self.stdout.write('='*60)
        self.stdout.write(f"  Products: {counts['products']}")
        self.stdout.write(f"  Orders: {counts['orders']}")
        self.stdout.write(f"  Order Items: {counts['order_items']}")
        self.stdout.write(f"  Sales Records: {counts['sales']}")
        self.stdout.write('='*60 + '\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data was deleted'))
            self.stdout.write('Run without --dry-run to actually delete the data')
            return
        
        # Confirm deletion
        if not force:
            confirm = input('Are you sure you want to delete all static data? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Deletion cancelled.'))
                return
        
        # Delete static data
        self.stdout.write('\nDeleting static data...')
        actual_counts = remove_static_data(dry_run=False)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('DELETION COMPLETE:'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f"  Deleted Products: {actual_counts['products']}"))
        self.stdout.write(self.style.SUCCESS(f"  Deleted Orders: {actual_counts['orders']}"))
        self.stdout.write(self.style.SUCCESS(f"  Deleted Order Items: {actual_counts['order_items']}"))
        self.stdout.write(self.style.SUCCESS(f"  Deleted Sales Records: {actual_counts['sales']}"))
        self.stdout.write(self.style.SUCCESS('='*60))



