from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Sales
from decimal import Decimal


@receiver(post_save, sender=Order)
def create_sales_on_order_completion(sender, instance, created, **kwargs):
    """
    Automatically create a sales record when an order status changes to 'completed'
    """
    if instance.status == 'completed':
        # Check if sales record already exists
        sales_record, created = Sales.objects.get_or_create(
            order=instance,
            defaults={
                'amount': instance.total_amount,
                'payment_method': 'cash'  # Default payment method
            }
        )
        
        if created:
            # Generate sales identifier for new sales record
            sales_record.generate_sales_identifier()
            sales_record.save()
            print(f"Created sales record {sales_record.sales_identifier} for order {instance.order_identifier}")
        else:
            # Update existing sales record if needed
            if sales_record.amount != instance.total_amount:
                sales_record.amount = instance.total_amount
                sales_record.save()
                print(f"Updated sales record {sales_record.sales_identifier} for order {instance.order_identifier}")


