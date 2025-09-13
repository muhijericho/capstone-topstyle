from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from business.models import Category, Product, Customer


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {'name': 'Suits', 'description': 'Formal suits for men and women'},
            {'name': 'Dresses', 'description': 'Formal and casual dresses'},
            {'name': 'Accessories', 'description': 'Belts, ties, shoes, and other accessories'},
            {'name': 'Materials', 'description': 'Fabric and sewing materials'},
            {'name': 'Services', 'description': 'Tailoring and repair services'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products
        products_data = [
            # Rental Items
            {'name': 'Black Tuxedo', 'category': 'Suits', 'type': 'rental', 'price': 50.00, 'cost': 200.00, 'quantity': 5, 'min_quantity': 1},
            {'name': 'White Wedding Dress', 'category': 'Dresses', 'type': 'rental', 'price': 80.00, 'cost': 300.00, 'quantity': 3, 'min_quantity': 1},
            {'name': 'Navy Blue Suit', 'category': 'Suits', 'type': 'rental', 'price': 45.00, 'cost': 180.00, 'quantity': 4, 'min_quantity': 1},
            {'name': 'Red Evening Gown', 'category': 'Dresses', 'type': 'rental', 'price': 60.00, 'cost': 250.00, 'quantity': 2, 'min_quantity': 1},
            {'name': 'Leather Dress Shoes', 'category': 'Accessories', 'type': 'rental', 'price': 15.00, 'cost': 80.00, 'quantity': 8, 'min_quantity': 2},
            {'name': 'Silk Tie Set', 'category': 'Accessories', 'type': 'rental', 'price': 10.00, 'cost': 30.00, 'quantity': 12, 'min_quantity': 3},
            
            # Materials
            {'name': 'Cotton Fabric (1 yard)', 'category': 'Materials', 'type': 'material', 'price': 8.00, 'cost': 5.00, 'quantity': 50, 'min_quantity': 10},
            {'name': 'Silk Fabric (1 yard)', 'category': 'Materials', 'type': 'material', 'price': 15.00, 'cost': 10.00, 'quantity': 30, 'min_quantity': 5},
            {'name': 'Thread (spool)', 'category': 'Materials', 'type': 'material', 'price': 2.00, 'cost': 1.00, 'quantity': 100, 'min_quantity': 20},
            {'name': 'Buttons (pack of 10)', 'category': 'Materials', 'type': 'material', 'price': 3.00, 'cost': 1.50, 'quantity': 80, 'min_quantity': 15},
            {'name': 'Zipper (12 inch)', 'category': 'Materials', 'type': 'material', 'price': 4.00, 'cost': 2.00, 'quantity': 60, 'min_quantity': 10},
            
            # Services
            {'name': 'Suit Alteration', 'category': 'Services', 'type': 'service', 'price': 25.00, 'cost': 0.00, 'quantity': 999, 'min_quantity': 0},
            {'name': 'Dress Hemming', 'category': 'Services', 'type': 'service', 'price': 15.00, 'cost': 0.00, 'quantity': 999, 'min_quantity': 0},
            {'name': 'Custom Tailoring', 'category': 'Services', 'type': 'service', 'price': 100.00, 'cost': 0.00, 'quantity': 999, 'min_quantity': 0},
            {'name': 'Emergency Repair', 'category': 'Services', 'type': 'service', 'price': 20.00, 'cost': 0.00, 'quantity': 999, 'min_quantity': 0},
        ]
        
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'category': categories[prod_data['category']],
                    'product_type': prod_data['type'],
                    'price': prod_data['price'],
                    'cost': prod_data['cost'],
                    'quantity': prod_data['quantity'],
                    'min_quantity': prod_data['min_quantity'],
                    'description': f'Sample {prod_data["type"]} product for TopStyle Business'
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create sample customers
        customers_data = [
            {'name': 'John Smith', 'email': 'john.smith@email.com', 'phone': '+1-555-0101', 'address': '123 Main St, City, State 12345'},
            {'name': 'Sarah Johnson', 'email': 'sarah.j@email.com', 'phone': '+1-555-0102', 'address': '456 Oak Ave, City, State 12345'},
            {'name': 'Michael Brown', 'email': 'mike.brown@email.com', 'phone': '+1-555-0103', 'address': '789 Pine Rd, City, State 12345'},
            {'name': 'Emily Davis', 'email': 'emily.davis@email.com', 'phone': '+1-555-0104', 'address': '321 Elm St, City, State 12345'},
            {'name': 'David Wilson', 'email': 'david.wilson@email.com', 'phone': '+1-555-0105', 'address': '654 Maple Dr, City, State 12345'},
        ]
        
        for cust_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                email=cust_data['email'],
                defaults={
                    'name': cust_data['name'],
                    'phone': cust_data['phone'],
                    'address': cust_data['address']
                }
            )
            if created:
                self.stdout.write(f'Created customer: {customer.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )

