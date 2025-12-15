from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
import uuid
import json


class StaffProfile(models.Model):
    """Extended profile for staff members with image"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    phone = models.CharField(max_length=20, blank=True, null=True, help_text='Staff phone number')
    profile_image = models.ImageField(upload_to='staff_profiles/', blank=True, null=True, help_text='Staff profile picture')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Profile"
    
    class Meta:
        verbose_name = "Staff Profile"
        verbose_name_plural = "Staff Profiles"


class StaffWithdrawal(models.Model):
    """Track staff revenue withdrawals"""
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    withdrawal_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Amount withdrawn (staff share)')
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, help_text='Total revenue at time of withdrawal')
    owner_share = models.DecimalField(max_digits=10, decimal_places=2, help_text='Owner share at time of withdrawal')
    completed_orders_count = models.PositiveIntegerField(default=0, help_text='Number of completed orders at withdrawal')
    withdrawn_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='withdrawals_processed', help_text='User who processed the withdrawal')
    notes = models.TextField(blank=True, help_text='Additional notes about the withdrawal')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.staff.get_full_name() or self.staff.username} - ₱{self.withdrawal_amount} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Staff Withdrawal"
        verbose_name_plural = "Staff Withdrawals"
        ordering = ['-created_at']


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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=0)
    min_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    # Material specific fields
    material_type = models.ForeignKey(
        'MaterialType', 
        on_delete=models.CASCADE, 
        related_name='products',
        blank=True, 
        null=True
    )
    material_pricing = models.ForeignKey(
        'MaterialPricing', 
        on_delete=models.SET_NULL, 
        related_name='products',
        blank=True, 
        null=True
    )
    current_quantity_in_stock = models.PositiveIntegerField(
        default=0, 
        help_text='Current quantity in stock'
    )
    unit_of_measurement = models.CharField(
        blank=True, 
        help_text='Unit of measurement for this material', 
        max_length=50
    )
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
            # For rental products, availability is based on rental_status, not quantity
            # Rental products can have quantity=0 but still be available for rent (they're unique items)
            return (self.is_active and not self.is_archived 
                   and self.rental_status == 'available')
        return self.quantity > 0 and self.is_active and not self.is_archived
    
    @property
    def is_overdue(self):
        """Check if rental is overdue or almost due (1 day before or on due date)"""
        if self.product_type == 'rental' and self.rental_due_date and self.rental_status == 'rented':
            now = timezone.now()
            time_until_due = self.rental_due_date - now
            days_until_due = time_until_due.days
            
            # Overdue: past due date
            if now > self.rental_due_date:
                return True
            
            # Almost due: 1 day before or on the due date (within 3-day rental period)
            # Also check if within 24 hours
            if days_until_due == 0 or days_until_due == 1:
                return True
            # Also check if less than 24 hours remaining
            if time_until_due.total_seconds() > 0 and time_until_due.total_seconds() <= 86400:  # 24 hours
                return True
        return False
    
    @property
    def is_almost_due(self):
        """Check if rental is almost due (1 day before or on due date)"""
        if self.product_type == 'rental' and self.rental_due_date and self.rental_status == 'rented':
            now = timezone.now()
            time_until_due = self.rental_due_date - now
            days_until_due = time_until_due.days
            
            # Almost due: 1 day before or on the due date (but not past due)
            # Also check if within 24 hours
            if days_until_due == 0 or days_until_due == 1:
                return True
            # Also check if less than 24 hours remaining
            if time_until_due.total_seconds() > 0 and time_until_due.total_seconds() <= 86400:  # 24 hours
                return True
        return False

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity
    
    def save(self, *args, **kwargs):
        """Override save to set rental product pricing"""
        if self.product_type == 'rental':
            # Set base price to 500 for all rental products
            self.price = Decimal('500.00')
        super().save(*args, **kwargs)


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
        ('in_progress', 'In Progress'),
        ('rented', 'Rented'),
        ('returned', 'Returned'),
        ('almost_due', 'Almost Due'),
        ('due', 'Due'),
        ('overdue', 'Overdue'),
        ('ready_to_pick_up', 'Ready to Pick Up'),
        ('repair_done', 'Repair Done'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    ORDER_TYPES = [
        ('rent', 'Rent'),
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
    payment_method = models.CharField(max_length=50, default='cash', help_text='Payment method used for this order')
    notes = models.TextField(blank=True)
    # REMOVED: created_by field as requested
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(blank=True, null=True)
    
    # BACKEND FIX: Rental pricing fields
    rental_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Rental fee (1500)')
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Deposit amount (1000)')
    product_base_price = models.DecimalField(max_digits=10, decimal_places=2, default=500, help_text='Product base price (500)')
    
    # Customize order fields
    customize_product_reference = models.ForeignKey(
        'Product', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='customize_orders',
        help_text='Reference to customize product (uniform/PE) selected or uploaded'
    )
    customize_image = models.ImageField(
        upload_to='customize_orders/', 
        blank=True, 
        null=True,
        help_text='Uploaded customize product image (if not from existing products)'
    )
    
    # Archive field to hide completed orders from orders list but keep them in reports
    is_archived = models.BooleanField(default=False, help_text='Archive completed orders to keep them in reports but hide from orders list')
    
    # Staff assignment for repair and customize orders
    assigned_staff = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        help_text='Staff member assigned to this repair/customize order'
    )
    staff_assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when staff was assigned to this order'
    )
    staff_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when staff marked the order as done'
    )

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        """Override save to set rental pricing automatically"""
        if self.order_type in ['rent', 'rental']:
            # Set rental pricing according to business logic
            self.product_base_price = Decimal('500.00')  # Base price stays at 500
            self.rental_fee = Decimal('1500.00')  # Rent price is 1500
            self.deposit_amount = Decimal('1000.00')  # Deposit is 1000
            
            # Calculate total amount (rental_fee + deposit_amount)
            self.total_amount = self.rental_fee + self.deposit_amount
            
            # Set status to 'rented' for rental orders
            if self.status == 'pending':
                self.status = 'rented'
                
            # Set due date to 3 days from creation
            if not self.due_date:
                self.due_date = timezone.now() + timezone.timedelta(days=3)
        
        super().save(*args, **kwargs)
    
    @property
    def is_rental_order(self):
        """Check if this is a rental order"""
        return self.order_type in ['rent', 'rental']
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    @property
    def is_one_day_before_due(self):
        """Check if order is 1 day before due date"""
        days = self.days_until_due
        return days is not None and days == 1
    
    @property
    def is_due_today(self):
        """Check if order is due today"""
        days = self.days_until_due
        return days is not None and days == 0
    
    @property
    def is_overdue(self):
        """Check if a rental order is overdue"""
        if self.order_type in ['rent', 'rental'] and self.due_date:
            return timezone.now() > self.due_date and self.status in ['pending', 'rented', 'almost_due', 'due', 'overdue']
        return False
    
    @property
    def days_overdue(self):
        """Calculate how many days overdue (returns positive number if overdue, 0 if not overdue)"""
        if self.order_type in ['rent', 'rental'] and self.due_date:
            if timezone.now() > self.due_date:
                delta = timezone.now() - self.due_date
                return delta.days
        return 0

    def generate_order_identifier(self):
        """Generate unique order identifier based on order type
        Format: TS01RENT-O1, TS01REP-O1, TS01CUST-O1, etc.
        """
        if not self.order_identifier:
            # Get the prefix based on order type
            prefix_map = {
                'rent': 'TS01RENT',
                'rental': 'TS01RENT',
                'repair': 'TS01REP',
                'customize': 'TS01CUST'
            }
            prefix = prefix_map.get(self.order_type, 'TS01UNK')
            
            # Get the next sequence number for this order type
            # Filter by prefix to get the latest order of this type
            queryset = Order.objects.filter(order_identifier__startswith=prefix)
            if self.pk:  # Only exclude current order if it already exists
                queryset = queryset.exclude(id=self.pk)
            last_order = queryset.order_by('-order_identifier').first()
            
            if last_order and last_order.order_identifier:
                # Extract the number part after "-O" (e.g., TS01RENT-O1 -> 1)
                try:
                    # Split by "-O" to get the number part
                    parts = last_order.order_identifier.split('-O')
                    if len(parts) == 2:
                        last_number = int(parts[1])
                        next_number = last_number + 1
                    else:
                        # Fallback: try to extract from last part after dash
                        last_part = last_order.order_identifier.split('-')[-1]
                        # Remove 'O' if present (handle both -O01 and -01 formats)
                        last_part = last_part.replace('O', '').replace('o', '')
                        last_number = int(last_part)
                        next_number = last_number + 1
                except (IndexError, ValueError):
                    next_number = 1
            else:
                next_number = 1
            
            # Format with leading zeros (e.g., O01, O02, O03)
            self.order_identifier = f"{prefix}-O{next_number:02d}"
        
        return self.order_identifier

    def get_effective_status(self):
        """Get the effective status for display, considering rental-specific logic"""
        if self.order_type in ['rent', 'rental']:
            # For rental orders, only show completed when returned
            if self.status == 'completed':
                return 'completed'
            elif self.status == 'rented':
                return 'rented'
            else:
                return 'pending'
        else:
            # For non-rental orders, use the actual status
            return self.status
    
    def is_rental_completed(self):
        """Check if a rental order is truly completed (returned)"""
        if self.order_type in ['rent', 'rental']:
            return self.status == 'completed'
        return self.status == 'completed'
    
    def check_balance_and_update_status(self):
        """Check if balance is paid and update status accordingly"""
        # Recalculate balance
        self.balance = self.total_amount - self.paid_amount
        
        # Update status based on balance
        if self.balance <= 0:
            # Balance is fully paid
            if self.order_type in ['rent', 'rental'] and self.status == 'rented':
                # For rental orders, only mark as completed if returned
                pass  # Keep current status
            elif self.status in ['pending', 'confirmed', 'in_progress']:
                # For non-rental orders or pending rentals, mark as completed
                if self.order_type in ['rent', 'rental']:
                    self.status = 'rented'  # Rental orders become 'rented' when paid
                else:
                    self.status = 'completed'  # Regular orders become 'completed' when paid
        else:
            # Balance still exists, keep as pending
            if self.status not in ['cancelled']:
                self.status = 'pending'
        
        self.save()
        return self.balance <= 0
    
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
    # REMOVED: created_by field as requested
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
        if not self.sales_identifier or self.sales_identifier.strip() == '':
            # Get current year
            current_year = timezone.now().year
            
            # Get the last sales record for this year
            # Use a more robust query to find the highest number
            last_sales = Sales.objects.filter(
                sales_identifier__startswith=f'TSRT-{current_year}-'
            ).exclude(sales_identifier='').order_by('-sales_identifier').first()
            
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
            # But first check if this identifier already exists and increment if needed
            max_attempts = 100
            for attempt in range(max_attempts):
                candidate_identifier = f"TSRT-{current_year}-{next_number:02d}"
                if not Sales.objects.filter(sales_identifier=candidate_identifier).exists():
                    self.sales_identifier = candidate_identifier
                    break
                next_number += 1
            else:
                # If we've exhausted all attempts, use a timestamp-based fallback
                import time
                timestamp_suffix = int(time.time()) % 10000
                self.sales_identifier = f"TSRT-{current_year}-{timestamp_suffix:04d}"
        
        return self.sales_identifier

    def save(self, *args, **kwargs):
        if not self.sales_identifier or self.sales_identifier.strip() == '':
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


class MaterialType(models.Model):
    """Model for different types of materials used in the business"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    unit_of_measurement = models.CharField(
        max_length=50, 
        help_text='e.g., piece, meter, yard, bundle'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Material Types"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MaterialPricing(models.Model):
    """Model for pricing different material types"""
    PRICING_TYPES = [
        ('per_piece', 'Per Piece'),
        ('per_bundle', 'Per Bundle'),
        ('per_meter', 'Per Meter'),
        ('per_yard', 'Per Yard'),
        ('per_kg', 'Per Kilogram'),
        ('per_dozen', 'Per Dozen'),
    ]
    
    material_type = models.ForeignKey(
        MaterialType, 
        on_delete=models.CASCADE, 
        related_name='pricing_options'
    )
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES)
    bundle_size = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text='Number of pieces in a bundle (if applicable)'
    )
    buy_price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text='Price you buy this material for'
    )
    sell_price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text='Price you sell this material for'
    )
    is_default = models.BooleanField(
        default=False, 
        help_text='Default pricing option for this material type'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Material Pricing Options"
        unique_together = [('material_type', 'pricing_type', 'bundle_size')]
        ordering = ['material_type', 'pricing_type']
    
    def __str__(self):
        bundle_info = f" (Bundle of {self.bundle_size})" if self.bundle_size else ""
        return f"{self.material_type.name} - {self.get_pricing_type_display()}{bundle_info}"


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


class SystemSettings(models.Model):
    """Model for system-wide settings including background images"""
    background_image = models.ImageField(
        upload_to='system/backgrounds/',
        blank=True,
        null=True,
        help_text='Background image for the system'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Only one active setting is used'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"System Settings (Active: {self.is_active})"
    
    @classmethod
    def get_active_settings(cls):
        """Get the active system settings"""
        return cls.objects.filter(is_active=True).first()
    
    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['-is_active', '-updated_at']


class LandingPageImage(models.Model):
    """Model for managing landing page images"""
    IMAGE_TYPE_CHOICES = [
        ('hero', 'Hero Section Image'),
        ('service_repair', 'Service - Repair'),
        ('service_customize', 'Service - Customize'),
        ('service_uniform', 'Service - Uniform Making'),
        ('service_patches', 'Service - Patches'),
        ('service_rental', 'Service - Rental'),
        ('about_workshop', 'About - Workshop'),
        ('about_tailor', 'About - Tailor'),
        ('fabric_cotton', 'Fabric - Cotton'),
        ('fabric_linen', 'Fabric - Linen'),
        ('fabric_wool', 'Fabric - Wool'),
        ('fabric_leather', 'Fabric - Leather'),
        ('fabric_silk', 'Fabric - Silk'),
        ('shop_exterior', 'Shop - Exterior'),
        ('shop_exterior_2', 'Shop - Exterior 2'),
        ('shop_interior', 'Shop - Interior'),
        ('shop_interior_2', 'Shop - Interior 2'),
    ]
    
    image_type = models.CharField(
        max_length=50,
        choices=IMAGE_TYPE_CHOICES,
        unique=True,
        help_text='Type of image for the landing page'
    )
    image = models.ImageField(
        upload_to='landing_page/',
        help_text='Image file for the landing page'
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text='Alternative text for the image'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this image is currently displayed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_image_type_display()} - {'Active' if self.is_active else 'Inactive'}"
    
    class Meta:
        verbose_name = 'Landing Page Image'
        verbose_name_plural = 'Landing Page Images'
        ordering = ['image_type']


# Django Signals to automatically log activities
@receiver(post_save, sender=Order)
def log_order_activity(sender, instance, created, **kwargs):
    """Log when orders are created or updated"""
    if created:
        ActivityLog.objects.create(
            activity_type='order_created',
            description=f"New {instance.get_order_type_display()} order created for {instance.customer.name}",
            user=None,  # REMOVED: created_by field no longer exists
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
            user=None,  # REMOVED: created_by field no longer exists
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
                'price': float(instance.price) if instance.price else 0.0,
                'quantity': float(instance.quantity) if instance.quantity else 0.0,
                'category': instance.category.name if instance.category else None
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
                'price': float(instance.price) if instance.price else 0.0,
                'quantity': float(instance.quantity) if instance.quantity else 0.0,
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
            user=None,  # REMOVED: created_by field no longer exists
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
