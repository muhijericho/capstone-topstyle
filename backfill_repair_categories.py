#!/usr/bin/env python
"""Script to backfill repair order categories"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')
django.setup()

from decimal import Decimal
from business.models import Order, OrderItem, Product, Category, InventoryTransaction

def backfill_repair_orders():
    """Backfill OrderItems for existing repair orders"""
    print("[BACKFILL] Starting repair order category backfill...")
    
    # Find all repair orders without OrderItems
    repair_orders = Order.objects.filter(
        order_type='repair'
    ).prefetch_related('items')
    
    orders_to_fix = [order for order in repair_orders if order.items.count() == 0]
    
    print(f"[BACKFILL] Found {len(orders_to_fix)} repair orders without OrderItems")
    
    # Get or create repair category
    repair_category, _ = Category.objects.get_or_create(
        name='Repair',
        defaults={'description': 'Repair service category'}
    )
    
    fixed_count = 0
    failed_count = 0
    
    for order in orders_to_fix:
        try:
            repair_type = None
            
            # Method 1: Try to extract repair type from inventory transaction notes
            transactions = InventoryTransaction.objects.filter(
                reference_order=order
            ).order_by('created_at')
            
            for transaction in transactions:
                if transaction.notes:
                    notes_lower = transaction.notes.lower()
                    # Look for patterns like "used for zipper repair" or "for zipper repair"
                    if 'repair' in notes_lower:
                        # Try to extract repair type from notes
                        # Pattern: "used for {repair_type} repair"
                        if 'used for' in notes_lower:
                            parts = notes_lower.split('used for')
                            if len(parts) > 1:
                                repair_part = parts[1].split('repair')[0].strip()
                                if repair_part:
                                    repair_type = repair_part.title()
                                    break
                        # Pattern: "for {repair_type} repair"
                        elif 'for' in notes_lower and 'repair' in notes_lower:
                            parts = notes_lower.split('for')
                            if len(parts) > 1:
                                repair_part = parts[1].split('repair')[0].strip()
                                if repair_part:
                                    repair_type = repair_part.title()
                                    break
            
            # Method 2: Try to extract from order notes
            if not repair_type and order.notes:
                notes_lower = order.notes.lower()
                # Look for common repair types
                repair_types = ['zipper', 'button', 'bewang', 'lock', 'patch', 'thread']
                for rt in repair_types:
                    if rt in notes_lower:
                        repair_type = rt.title()
                        break
            
            # Method 3: Default to "Repair Service" if nothing found
            if not repair_type:
                repair_type = 'Repair Service'
            
            # Get or create product for this repair type
            product_name = f"Repair - {repair_type}" if repair_type != 'Repair Service' else "Repair Service"
            product, created = Product.objects.get_or_create(
                name=product_name,
                product_type='service',
                defaults={
                    'category': repair_category,
                    'description': f"Repair service: {repair_type}",
                    'price': Decimal('0'),
                    'quantity': 0,
                    'is_active': True,
                    'is_archived': False,
                }
            )
            
            # Update category if product already existed but didn't have one
            if not created and not product.category:
                product.category = repair_category
                product.description = f"Repair service: {repair_type}"
                product.save()
            
            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                unit_price=Decimal('0'),
                total_price=Decimal('0')
            )
            
            fixed_count += 1
            print(f"[BACKFILL] OK Fixed order {order.order_identifier}: {repair_type}")
            
        except Exception as e:
            failed_count += 1
            print(f"[BACKFILL] ERROR Failed to fix order {order.order_identifier}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n[BACKFILL] Completed: {fixed_count} fixed, {failed_count} failed")
    return fixed_count, failed_count

if __name__ == '__main__':
    fixed, failed = backfill_repair_orders()
    print(f"\nSUCCESS: Successfully backfilled {fixed} repair orders")
    if failed > 0:
        print(f"WARNING: {failed} orders failed to backfill")

