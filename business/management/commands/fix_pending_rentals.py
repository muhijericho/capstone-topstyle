from django.core.management.base import BaseCommand
from business.models import Order, Product, OrderItem
from django.utils import timezone
from decimal import Decimal

class Command(BaseCommand):
    help = 'Fix pending rental orders by creating missing OrderItems'

    def handle(self, *args, **options):
        self.stdout.write('Fixing pending rental orders...')
        
        # Get pending rental orders
        pending_orders = Order.objects.filter(
            order_type__in=['rent', 'rental'],
            status='pending'
        )
        
        self.stdout.write(f'Found {pending_orders.count()} pending rental orders')
        
        fixed_count = 0
        
        for order in pending_orders:
            self.stdout.write(f'Processing order {order.order_identifier}')
            
            # Check if order has any items
            if order.items.count() == 0:
                self.stdout.write(f'  Order {order.order_identifier} has no items, skipping')
                continue
            
            # Process each item in the order
            for item in order.items.all():
                product = item.product
                
                if product.product_type == 'rental':
                    # Update product status to rented
                    if product.rental_status != 'rented':
                        product.rental_status = 'rented'
                        product.current_rental_order = order
                        product.rental_start_date = order.created_at
                        product.rental_due_date = order.created_at + timezone.timedelta(days=3)
                        product.save()
                        
                        self.stdout.write(f'  Fixed product {product.name}: marked as rented')
                        fixed_count += 1
                    else:
                        self.stdout.write(f'  Product {product.name} already marked as rented')
        
        self.stdout.write(f'Fixed {fixed_count} products')




















































