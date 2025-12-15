from django.core.management.base import BaseCommand
from business.models import Order, Product

class Command(BaseCommand):
    help = 'Diagnose rental order and product status'

    def handle(self, *args, **options):
        self.stdout.write('Diagnosing rental orders and products...')
        
        # Check all rental orders
        rental_orders = Order.objects.filter(order_type__in=['rent', 'rental'])
        self.stdout.write(f'Found {rental_orders.count()} rental orders:')
        
        for order in rental_orders:
            self.stdout.write(f'  Order {order.order_identifier}: Status={order.status}')
            
            # Check products in this order
            items = order.items.filter(product__product_type='rental')
            for item in items:
                product = item.product
                self.stdout.write(f'    Product {product.name}: rental_status={product.rental_status}, current_rental_order={product.current_rental_order}')
        
        # Check all rental products
        rental_products = Product.objects.filter(product_type='rental')
        self.stdout.write(f'\nFound {rental_products.count()} rental products:')
        
        for product in rental_products:
            self.stdout.write(f'  Product {product.name}: rental_status={product.rental_status}, current_rental_order={product.current_rental_order}')




















































