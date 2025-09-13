from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from business.models import Order, Customer, Product, Category, OrderItem
from decimal import Decimal
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create sample orders for testing'

    def handle(self, *args, **options):
        # Get or create a user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        
        # Get or create categories
        category, created = Category.objects.get_or_create(
            name='Coat',
            defaults={'description': 'Coat category'}
        )
        
        # Get or create products
        product, created = Product.objects.get_or_create(
            name='Coat',
            defaults={
                'category': category,
                'description': 'Sample coat product',
                'price': Decimal('100.00'),
                'quantity': 10
            }
        )
        
        # Get or create customers
        customer1, created = Customer.objects.get_or_create(
            name='John Doe',
            defaults={'phone': '1234567890', 'email': 'john@example.com'}
        )
        
        customer2, created = Customer.objects.get_or_create(
            name='Jane Smith',
            defaults={'phone': '0987654321', 'email': 'jane@example.com'}
        )
        
        customer3, created = Customer.objects.get_or_create(
            name='Bob Johnson',
            defaults={'phone': '5555555555', 'email': 'bob@example.com'}
        )
        
        # Create sample orders
        orders_data = [
            {
                'customer': customer1,
                'order_type': 'repair',
                'status': 'pending',
                'total_amount': Decimal('200.00'),
                'paid_amount': Decimal('0.00'),
                'quantity': 2
            },
            {
                'customer': customer2,
                'order_type': 'rental',
                'status': 'confirmed',
                'total_amount': Decimal('300.00'),
                'paid_amount': Decimal('300.00'),
                'quantity': 2
            },
            {
                'customer': customer3,
                'order_type': 'customize',
                'status': 'completed',
                'total_amount': Decimal('400.00'),
                'paid_amount': Decimal('400.00'),
                'quantity': 2
            }
        ]
        
        for order_data in orders_data:
            # Create order
            order = Order.objects.create(
                customer=order_data['customer'],
                order_type=order_data['order_type'],
                status=order_data['status'],
                total_amount=order_data['total_amount'],
                paid_amount=order_data['paid_amount'],
                balance=order_data['total_amount'] - order_data['paid_amount'],
                created_by=user
            )
            
            # Generate unique identifier
            order.generate_order_identifier()
            order.save()
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=order_data['quantity'],
                unit_price=Decimal('100.00'),
                total_price=order_data['total_amount']
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created order {order.order_identifier} for {order.customer.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample orders!')
        )


