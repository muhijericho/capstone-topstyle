from django.core.management.base import BaseCommand
from business.models import Product


class Command(BaseCommand):
    help = 'Remove service products that were automatically created (customize Service and repair Service)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find service products that match the pattern of auto-created ones
        service_products = Product.objects.filter(
            product_type='service'
        ).filter(
            name__icontains='customize Service'
        ) | Product.objects.filter(
            product_type='service'
        ).filter(
            name__icontains='repair Service'
        )
        
        # Get distinct products
        products_to_delete = service_products.distinct()
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No products will be deleted'))
            self.stdout.write('')
        
        if products_to_delete.exists():
            self.stdout.write(f'Found {products_to_delete.count()} service product(s) to remove:')
            self.stdout.write('')
            
            for product in products_to_delete:
                self.stdout.write(f'  - {product.name} (ID: {product.id})')
            
            self.stdout.write('')
            
            if not dry_run:
                count = products_to_delete.count()
                products_to_delete.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted {count} service product(s)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Would delete {products_to_delete.count()} product(s)')
                )
        else:
            self.stdout.write(self.style.SUCCESS('No service products found to remove.'))


















