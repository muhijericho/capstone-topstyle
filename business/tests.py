from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Customer, Product, Order, Category
from decimal import Decimal


class BusinessModelTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        self.customer = Customer.objects.create(
            name='Test Customer',
            phone='1234567890',
            email='test@example.com',
            address='Test Address'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product description',
            category=self.category,
            product_type='material',
            price=Decimal('100.00'),
            cost=Decimal('50.00'),
            quantity=10,
            min_quantity=2
        )

    def test_customer_creation(self):
        """Test customer model creation"""
        self.assertEqual(self.customer.name, 'Test Customer')
        self.assertEqual(self.customer.phone, '1234567890')
        self.assertEqual(str(self.customer), 'Test Customer')

    def test_product_creation(self):
        """Test product model creation"""
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, Decimal('100.00'))
        self.assertTrue(self.product.is_available)
        self.assertFalse(self.product.is_low_stock)

    def test_order_creation(self):
        """Test order model creation"""
        order = Order.objects.create(
            customer=self.customer,
            order_type='repair',
            status='pending',
            total_amount=Decimal('100.00'),
            created_by=self.user
        )
        
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.order_type, 'repair')
        self.assertEqual(order.status, 'pending')
        self.assertIsNotNone(order.order_identifier)

    def test_product_low_stock(self):
        """Test product low stock detection"""
        # Set quantity below minimum
        self.product.quantity = 1
        self.product.save()
        
        self.assertTrue(self.product.is_low_stock)

    def test_product_out_of_stock(self):
        """Test product out of stock detection"""
        # Set quantity to 0
        self.product.quantity = 0
        self.product.save()
        
        self.assertFalse(self.product.is_available)


class BusinessViewTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        self.customer = Customer.objects.create(
            name='Test Customer',
            phone='1234567890',
            email='test@example.com'
        )

    def test_login_view(self):
        """Test login view"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_dashboard_authenticated(self):
        """Test dashboard with authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_customer_list_view(self):
        """Test customer list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('customer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Customer')

    def test_add_customer_view(self):
        """Test add customer view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('add_customer'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add New Customer')

    def test_orders_list_view(self):
        """Test orders list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('orders'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Orders Management')

    def test_inventory_list_view(self):
        """Test inventory list view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('inventory'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inventory Management')


class BusinessAPITests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.customer = Customer.objects.create(
            name='Test Customer',
            phone='1234567890',
            email='test@example.com'
        )

    def test_customers_api_requires_login(self):
        """Test customers API requires authentication"""
        response = self.client.get('/api/customers/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_customers_api_authenticated(self):
        """Test customers API with authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/customers/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['customers']), 1)
        self.assertEqual(data['customers'][0]['name'], 'Test Customer')

    def test_customer_detail_api(self):
        """Test customer detail API"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/api/customers/{self.customer.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['customer']['name'], 'Test Customer')

    def test_inventory_status_api(self):
        """Test inventory status API"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/inventory-status/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('total_products', data)
        self.assertIn('low_stock', data)
        self.assertIn('out_of_stock', data)







