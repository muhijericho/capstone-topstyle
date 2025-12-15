from django.core.management.base import BaseCommand
from business.rental_manager import RentalStatusManager

class Command(BaseCommand):
    help = 'Sync all rental statuses to ensure consistency across the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if no inconsistencies are detected',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting comprehensive rental status sync...')
        
        synced_count = RentalStatusManager.sync_all_rental_status()
        
        if synced_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully synced {synced_count} products')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No products needed syncing - all statuses are consistent')
            )
        
        # Also get current status overview
        status_data = RentalStatusManager.get_rental_status_for_all_products()
        
        rented_count = sum(1 for data in status_data.values() if data['is_rented'])
        available_count = len(status_data) - rented_count
        
        self.stdout.write(f'Current status overview:')
        self.stdout.write(f'  - Total rental products: {len(status_data)}')
        self.stdout.write(f'  - Currently rented: {rented_count}')
        self.stdout.write(f'  - Currently available: {available_count}')




















































