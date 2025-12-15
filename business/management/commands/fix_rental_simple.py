from django.core.management.base import BaseCommand
from business.models import Product, Order

class Command(BaseCommand):
    help = 'SIMPLE DIRECT: Fix rental status for all products'

    def handle(self, *args, **options):
        self.stdout.write('SIMPLE DIRECT: Starting rental status fix...')
        
        # Get all rental products
        rental_products = Product.objects.filter(product_type='rental')
        self.stdout.write(f'Found {rental_products.count()} rental products')
        
        # Get all active rental orders
        active_orders = Order.objects.filter(
            order_type__in=['rent', 'rental'],
            status__in=['rented', 'pending']
        )
        
        self.stdout.write(f'Found {active_orders.count()} active rental orders')
        
        # Track which products should be rented
        products_that_should_be_rented = set()
        
        for order in active_orders:
            self.stdout.write(f'Processing order {order.order_identifier}')
            for item in order.items.filter(product__product_type='rental'):
                products_that_should_be_rented.add(item.product.id)
                self.stdout.write(f'  - Product {item.product.name} should be rented')
        
        # Update product statuses
        fixed_count = 0
        
        for product in rental_products:
            should_be_rented = product.id in products_that_should_be_rented
            is_currently_rented = product.rental_status == 'rented'
            
            if should_be_rented and not is_currently_rented:
                # Product should be rented but isn't
                product.rental_status = 'rented'
                product.save()
                self.stdout.write(f'FIXED: {product.name} marked as rented')
                fixed_count += 1
            elif not should_be_rented and is_currently_rented:
                # Product is marked as rented but shouldn't be
                product.rental_status = 'available'
                product.current_rental_order = None
                product.rental_start_date = None
                product.rental_due_date = None
                product.save()
                self.stdout.write(f'FIXED: {product.name} marked as available')
                fixed_count += 1
            else:
                self.stdout.write(f'OK: {product.name} status is correct ({product.rental_status})')
        
        self.stdout.write(f'SIMPLE DIRECT: Fixed {fixed_count} products')




















































