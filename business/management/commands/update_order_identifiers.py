"""
Management command to update all existing order identifiers to the new format:
- Rent/Rental: TS01RENT-O1, TS01RENT-O2, etc.
- Repair: TS01REP-O1, TS01REP-O2, etc.
- Customize: TS01CUST-O1, TS01CUST-O2, etc.
"""
from django.core.management.base import BaseCommand
from business.models import Order
from collections import defaultdict


class Command(BaseCommand):
    help = 'Update all existing order identifiers to the new format based on order type'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if order already has new format identifier',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            self.stdout.write('')
        
        # Get prefix map
        prefix_map = {
            'rent': 'TS01RENT',
            'rental': 'TS01RENT',
            'repair': 'TS01REP',
            'customize': 'TS01CUST'
        }
        
        # Group orders by type and sort by creation date (oldest first)
        orders_by_type = defaultdict(list)
        all_orders = Order.objects.all().order_by('created_at')
        
        for order in all_orders:
            order_type = order.order_type
            if order_type in prefix_map:
                # Check if already has new format
                if not force and order.order_identifier:
                    prefix = prefix_map[order_type]
                    if order.order_identifier.startswith(prefix) and '-O' in order.order_identifier:
                        # Already has new format, skip unless force
                        continue
                orders_by_type[order_type].append(order)
        
        total_updated = 0
        total_skipped = 0
        
        # Process each order type
        for order_type, orders in orders_by_type.items():
            prefix = prefix_map[order_type]
            self.stdout.write(f'\nProcessing {order_type.upper()} orders (prefix: {prefix})...')
            self.stdout.write(f'Found {len(orders)} orders to update')
            
            # Sort by creation date to maintain chronological order
            orders_sorted = sorted(orders, key=lambda o: o.created_at)
            
            # Generate new identifiers sequentially starting from O01
            sequence_number = 1
            used_identifiers = set()  # Track identifiers we've assigned in this batch
            
            for order in orders_sorted:
                # Find the next available identifier
                while True:
                    new_identifier = f"{prefix}-O{sequence_number:02d}"
                    # Check if this identifier is already taken by another order (not in current batch)
                    existing_order = Order.objects.filter(order_identifier=new_identifier).exclude(id=order.id).first()
                    # Also check if we've already assigned it in this batch
                    if not existing_order and new_identifier not in used_identifiers:
                        break
                    # If taken, try next number
                    sequence_number += 1
                
                # Mark this identifier as used
                used_identifiers.add(new_identifier)
                
                old_identifier = order.order_identifier or '(empty)'
                
                if dry_run:
                    self.stdout.write(f'  Would update: {old_identifier} -> {new_identifier} (Order ID: {order.id}, Created: {order.created_at})')
                else:
                    order.order_identifier = new_identifier
                    order.save(update_fields=['order_identifier'])
                    self.stdout.write(f'  Updated: {old_identifier} -> {new_identifier} (Order ID: {order.id})')
                
                # Increment for next order
                sequence_number += 1
                total_updated += 1
        
        # Count skipped orders
        total_skipped = all_orders.count() - total_updated
        
        self.stdout.write('')
        self.stdout.write('=' * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE'))
            self.stdout.write(f'Would update: {total_updated} orders')
            self.stdout.write(f'Would skip: {total_skipped} orders')
            self.stdout.write('')
            self.stdout.write('Run without --dry-run to apply changes')
        else:
            self.stdout.write(self.style.SUCCESS('UPDATE COMPLETE'))
            self.stdout.write(f'Updated: {total_updated} orders')
            self.stdout.write(f'Skipped: {total_skipped} orders')
        
        self.stdout.write('=' * 60)

