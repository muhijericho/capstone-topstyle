from django.core.management.base import BaseCommand
from business.models import Product, Category

class Command(BaseCommand):
    help = 'Add sample rental products to the database'

    def handle(self, *args, **options):
        # Create categories if they don't exist
        categories = {
            'Suits': Category.objects.get_or_create(name='Suits')[0],
            'Dresses': Category.objects.get_or_create(name='Dresses')[0],
            'Barong': Category.objects.get_or_create(name='Barong')[0],
            'Coat': Category.objects.get_or_create(name='Coat')[0],
            'Pants': Category.objects.get_or_create(name='Pants')[0],
        }
        
        # Sample rental products
        rental_products = [
            {
                'name': 'Black Tuxedo',
                'category': 'Suits',
                'price': 500.00,
                'description': 'Classic black tuxedo for formal events',
                'quantity': 5
            },
            {
                'name': 'White Wedding Dress',
                'category': 'Dresses',
                'price': 800.00,
                'description': 'Elegant white wedding dress',
                'quantity': 3
            },
            {
                'name': 'Navy Blue Suit',
                'category': 'Suits',
                'price': 450.00,
                'description': 'Professional navy blue suit',
                'quantity': 4
            },
            {
                'name': 'Red Evening Gown',
                'category': 'Dresses',
                'price': 600.00,
                'description': 'Stunning red evening gown',
                'quantity': 2
            },
            {
                'name': 'Leather Dress Shoes',
                'category': 'Pants',
                'price': 200.00,
                'description': 'High-quality leather dress shoes',
                'quantity': 8
            },
            {
                'name': 'Silk Tie Set',
                'category': 'Pants',
                'price': 150.00,
                'description': 'Premium silk tie collection',
                'quantity': 10
            },
            {
                'name': 'Barong Tagalog',
                'category': 'Barong',
                'price': 400.00,
                'description': 'Traditional Filipino formal wear',
                'quantity': 6
            },
            {
                'name': 'White Barong',
                'category': 'Barong',
                'price': 350.00,
                'description': 'Elegant white barong for special occasions',
                'quantity': 4
            },
            {
                'name': 'Black Coat',
                'category': 'Coat',
                'price': 300.00,
                'description': 'Classic black overcoat',
                'quantity': 3
            },
            {
                'name': 'Formal Pants',
                'category': 'Pants',
                'price': 250.00,
                'description': 'Professional formal pants',
                'quantity': 7
            }
        ]
        
        created_count = 0
        for product_data in rental_products:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': categories[product_data['category']],
                    'product_type': 'rental',
                    'price': product_data['price'],
                    'cost': product_data['price'] * 0.6,  # 60% of price as cost
                    'quantity': product_data['quantity'],
                    'description': product_data['description'],
                    'rental_status': 'available',
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created: {product.name} - {product.category.name} - ₱{product.price}")
            else:
                self.stdout.write(f"Already exists: {product.name}")
        
        self.stdout.write(f"\nTotal rental products created: {created_count}")
        self.stdout.write(f"Total rental products in database: {Product.objects.filter(product_type='rental').count()}")

