from django.core.management.base import BaseCommand
from business.views import fix_existing_rental_orders

class Command(BaseCommand):
    help = 'Fix existing rental orders that don\'t have their products marked as rented'

    def handle(self, *args, **options):
        self.stdout.write('Starting rental status fix...')
        
        fixed_count = fix_existing_rental_orders()
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully fixed {fixed_count} products')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No products needed fixing')
            )




















































