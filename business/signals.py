from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, Sales, Product
from decimal import Decimal


@receiver(pre_save, sender=Order)
def auto_fix_rental_order_status(sender, instance, **kwargs):
    """
    ROBUST AUTO-FIX: Automatically ensure rental orders have 'rented' status and proper pricing
    This prevents the pending status issue from happening in the future
    """
    if instance.order_type in ['rent', 'rental']:
        # Set rental pricing according to business logic
        instance.product_base_price = Decimal('500.00')  # Base price stays at 500
        instance.rental_fee = Decimal('1500.00')  # Rent price is 1500
        instance.deposit_amount = Decimal('1000.00')  # Deposit is 1000
        
        # Calculate total amount (rental_fee + deposit_amount)
        instance.total_amount = instance.rental_fee + instance.deposit_amount
        
        # Set status to 'rented' for rental orders
        if instance.status == 'pending':
            instance.status = 'rented'
            print(f"[AUTO-FIX] Order {instance.order_identifier or 'NEW'} automatically set to 'rented' status")
            
        # Set due date to 3 days from creation
        if not instance.due_date:
            instance.due_date = timezone.now() + timezone.timedelta(days=3)


@receiver(post_save, sender=Order)
def create_sales_on_order_completion(sender, instance, created, **kwargs):
    """
    Automatically create a sales record when an order status changes to 'completed'
    """
    if instance.status == 'completed':
        # Use get_or_create but handle the case where Sales might already exist
        # Check if sales record already exists first
        if Sales.objects.filter(order=instance).exists():
            # Sales record already exists, just update if needed
            sales_record = Sales.objects.get(order=instance)
            if sales_record.amount != instance.total_amount:
                sales_record.amount = instance.total_amount
                sales_record.save()
                print(f"Updated sales record {sales_record.sales_identifier} for order {instance.order_identifier}")
        else:
            # Sales record doesn't exist, create new one
            # Create without identifier first, let the save() method generate it
            # This avoids race conditions with identifier generation
            try:
                # Use order's payment_method if available, otherwise default to 'cash'
                payment_method = getattr(instance, 'payment_method', 'cash') or 'cash'
                sales_record = Sales.objects.create(
                    order=instance,
                    amount=instance.total_amount,
                    payment_method=payment_method,
                    sales_identifier=''  # Empty string, will be generated in save()
                )
                print(f"Created sales record {sales_record.sales_identifier} for order {instance.order_identifier}")
            except Exception as e:
                # If creation fails (e.g., due to unique constraint on order), try to get existing
                if 'UNIQUE constraint' in str(e) or 'unique constraint' in str(e).lower():
                    try:
                        sales_record = Sales.objects.get(order=instance)
                        print(f"Sales record already exists for order {instance.order_identifier}")
                    except Sales.DoesNotExist:
                        # If it still doesn't exist, there might be a different issue
                        print(f"Error creating sales record for order {instance.order_identifier}: {e}")
                        raise
                else:
                    raise


@receiver(post_save, sender=Order)
def auto_update_rental_products(sender, instance, created, **kwargs):
    """
    ROBUST AUTO-FIX: Automatically update rental products when rental order is created
    This ensures products are marked as rented immediately
    """
    if instance.order_type in ['rent', 'rental'] and instance.status == 'rented':
        print(f"[AUTO-FIX] Updating rental products for order {instance.order_identifier}")
        
        for item in instance.items.all():
            if item.product.product_type == 'rental':
                item.product.rental_status = 'rented'
                item.product.current_rental_order = instance
                item.product.rental_start_date = instance.created_at
                item.product.rental_due_date = instance.created_at + timezone.timedelta(days=3)
                item.product.save()
                print(f"[AUTO-FIX] Product '{item.product.name}' marked as rented")

















