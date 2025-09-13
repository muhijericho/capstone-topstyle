from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
import uuid
import json


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    PRODUCT_TYPES = [
        ('rental', 'Rental Item'),
        ('material', 'Material'),
        ('service', 'Service'),
    ]
    
    RENTAL_STATUS = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    min_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    # Rental specific fields
    rental_status = models.CharField(max_length=20, choices=RENTAL_STATUS, default='available')
    current_rental_order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='rented_products')
    rental_start_date = models.DateTimeField(null=True, blank=True)
    rental_due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        if self.product_type == 'rental':
            return (self.quantity > 0 and self.is_active and not self.is_archived 
                   and self.rental_status == 'available')
        return self.quantity > 0 and self.is_active and not self.is_archived
    
    @property
    def is_overdue(self):
        if self.product_type == 'rental' and self.rental_due_date:
            return timezone.now() > self.rental_due_date and self.rental_status == 'rented'
        return False

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity


class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    ORDER_TYPES = [
        ('rental', 'Rental'),
        ('repair', 'Repair'),
        ('customize', 'Customize'),
    ]

    order_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_identifier = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.name}"

    def generate_order_identifier(self):
        """Generate unique order identifier based on order type"""
        if not self.order_identifier:
            # Get the prefix based on order type
            prefix_map = {
                'rental': 'TS01',
                'repair': 'TS02', 
                'customize': 'TS03'
            }
            prefix = prefix_map.get(self.order_type, 'TS00')
            
            # Get the next sequence number for this order type
            last_order = Order.objects.filter(
                order_type=self.order_type,
                order_identifier__startswith=prefix
            ).order_by('-order_identifier').first()
            
            if last_order and last_order.order_identifier:
                # Extract the number part and increment
                try:
                    last_number = int(last_order.order_identifier.split('-')[1])
                    next_number = last_number + 1
                except (IndexError, ValueError):
                    next_number = 1
            else:
                next_number = 1
            
            # Format with leading zeros (e.g., 01, 02, 03)
            self.order_identifier = f"{prefix}-{next_number:02d}"
        
        return self.order_identifier

    def save(self, *args, **kwargs):
        self.balance = self.total_amount - self.paid_amount
        if not self.order_identifier:
            self.generate_order_identifier()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Ensure quantity is an integer and unit_price is a Decimal
        quantity = int(self.quantity) if self.quantity else 0
        unit_price = Decimal(str(self.unit_price)) if self.unit_price else Decimal('0')
        self.total_price = quantity * unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('rental_out', 'Rental Out'),
        ('rental_in', 'Rental Return'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()  # Can be negative for stock out
    reference_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.transaction_type} - {self.quantity}"


class Sales(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    sales_identifier = models.CharField(max_length=20, unique=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='cash')
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_sales_identifier(self):
        """Generate unique sales identifier in format TSRT-YYYY-XX"""
        if not self.sales_identifier:
            # Get current year
            current_year = timezone.now().year
            
            # Get the last sales record for this year
            last_sales = Sales.objects.filter(
                sales_identifier__startswith=f'TSRT-{current_year}'
            ).order_by('-sales_identifier').first()
            
            if last_sales and last_sales.sales_identifier:
                # Extract the number part and increment
                try:
                    parts = last_sales.sales_identifier.split('-')
                    if len(parts) == 3 and parts[1] == str(current_year):
                        last_number = int(parts[2])
                        next_number = last_number + 1
                    else:
                        next_number = 1
                except (IndexError, ValueError):
                    next_number = 1
            else:
                next_number = 1
            
            # Format with leading zeros (e.g., 01, 02, 03)
            self.sales_identifier = f"TSRT-{current_year}-{next_number:02d}"
        
        return self.sales_identifier

    def save(self, *args, **kwargs):
        if not self.sales_identifier:
            self.generate_sales_identifier()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale {self.sales_identifier} - {self.order}"


class QRCode(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    qr_code_image = models.ImageField(upload_to='qr_codes/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR Code - {self.order}"


class SMSNotification(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SMS - {self.order} - {self.phone_number}"


class ActivityLog(models.Model):
    """Model to track all activities in the system"""
    ACTIVITY_TYPES = [
        ('order_created', 'Order Created'),
        ('order_updated', 'Order Updated'),
        ('order_completed', 'Order Completed'),
        ('order_cancelled', 'Order Cancelled'),
        ('product_added', 'Product Added'),
        ('product_updated', 'Product Updated'),
        ('product_archived', 'Product Archived'),
        ('inventory_transaction', 'Inventory Transaction'),
        ('sales_created', 'Sales Created'),
        ('payment_received', 'Payment Received'),
        ('customer_created', 'Customer Created'),
        ('customer_updated', 'Customer Updated'),
    ]
    
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # Store additional data
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.created_at}"


# Django Signals to automatically log activities
@receiver(post_save, sender=Order)
def log_order_activity(sender, instance, created, **kwargs):
    """Log when orders are created or updated"""
    if created:
        ActivityLog.objects.create(
            activity_type='order_created',
            description=f"New {instance.get_order_type_display()} order created for {instance.customer.name}",
            user=instance.created_by,
            order=instance,
            customer=instance.customer,
            metadata={
                'order_identifier': instance.order_identifier,
                'order_type': instance.order_type,
                'total_amount': float(instance.total_amount),
                'status': instance.status
            }
        )
    else:
        ActivityLog.objects.create(
            activity_type='order_updated',
            description=f"Order {instance.order_identifier} updated - Status: {instance.get_status_display()}",
            user=instance.created_by,
            order=instance,
            customer=instance.customer,
            metadata={
                'order_identifier': instance.order_identifier,
                'status': instance.status,
                'total_amount': float(instance.total_amount),
                'paid_amount': float(instance.paid_amount)
            }
        )

@receiver(post_save, sender=Product)
def log_product_activity(sender, instance, created, **kwargs):
    """Log when products are created or updated"""
    if created:
        ActivityLog.objects.create(
            activity_type='product_added',
            description=f"New product '{instance.name}' added to inventory",
            product=instance,
            metadata={
                'product_name': instance.name,
                'product_type': instance.product_type,
                'price': float(instance.price),
                'quantity': instance.quantity,
                'category': instance.category.name
            }
        )
    else:
        ActivityLog.objects.create(
            activity_type='product_updated',
            description=f"Product '{instance.name}' updated",
            product=instance,
            metadata={
                'product_name': instance.name,
                'product_type': instance.product_type,
                'price': float(instance.price),
                'quantity': instance.quantity,
                'is_archived': instance.is_archived
            }
        )

@receiver(post_save, sender=InventoryTransaction)
def log_inventory_transaction(sender, instance, created, **kwargs):
    """Log inventory transactions"""
    if created:
        ActivityLog.objects.create(
            activity_type='inventory_transaction',
            description=f"Inventory transaction: {instance.get_transaction_type_display()} - {instance.product.name} (Qty: {instance.quantity})",
            product=instance.product,
            order=instance.reference_order,
            user=instance.created_by,
            metadata={
                'transaction_type': instance.transaction_type,
                'product_name': instance.product.name,
                'quantity': instance.quantity,
                'order_identifier': instance.reference_order.order_identifier if instance.reference_order else None
            }
        )

@receiver(post_save, sender=Sales)
def log_sales_activity(sender, instance, created, **kwargs):
    """Log when sales are created"""
    if created:
        ActivityLog.objects.create(
            activity_type='sales_created',
            description=f"Sale {instance.sales_identifier} created for order {instance.order.order_identifier}",
            order=instance.order,
            customer=instance.order.customer,
            metadata={
                'sales_identifier': instance.sales_identifier,
                'order_identifier': instance.order.order_identifier,
                'amount': float(instance.amount),
                'payment_method': instance.payment_method
            }
        )

@receiver(post_save, sender=Customer)
def log_customer_activity(sender, instance, created, **kwargs):
    """Log when customers are created or updated"""
    if created:
        ActivityLog.objects.create(
            activity_type='customer_created',
            description=f"New customer '{instance.name}' added",
            customer=instance,
            metadata={
                'customer_name': instance.name,
                'phone': instance.phone,
                'email': instance.email
            }
        )
    else:
        ActivityLog.objects.create(
            activity_type='customer_updated',
            description=f"Customer '{instance.name}' updated",
            customer=instance,
            metadata={
                'customer_name': instance.name,
                'phone': instance.phone,
                'email': instance.email
            }
        )
