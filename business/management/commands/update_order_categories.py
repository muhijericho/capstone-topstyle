from django.core.management.base import BaseCommand
from business.models import Order, OrderItem, Product, Category, InventoryTransaction
from django.utils import timezone
from decimal import Decimal


class Command(BaseCommand):
    help = 'Update existing orders to extract and display correct repair/customize categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def format_repair_type(self, repair_type_str):
        """Format repair type from snake_case to Title Case"""
        if not repair_type_str:
            return None
        # Remove "Repair - " prefix if present
        if "Repair - " in repair_type_str:
            repair_type_str = repair_type_str[10:].strip()
        # Remove "repair - " prefix if present (lowercase)
        if "repair - " in repair_type_str.lower():
            repair_type_str = repair_type_str[repair_type_str.lower().find("repair - ") + 9:].strip()
        # Remove class suffix like "(Class standard)"
        if " (Class " in repair_type_str:
            repair_type_str = repair_type_str.split(" (Class ")[0].strip()
        # Remove timestamp if present
        if " - " in repair_type_str and len(repair_type_str.split(" - ")[-1]) > 10:
            repair_type_str = repair_type_str.split(" - ")[0].strip()
        # Handle common repair types
        repair_type_lower = repair_type_str.lower().strip()
        repair_type_map = {
            'zipper': 'Zipper',
            'zipper_repair': 'Zipper',
            'zipper_replacement': 'Zipper',
            'buttons': 'Buttons',
            'button': 'Buttons',
            'buttons_repair': 'Buttons',
            'patch': 'Patch',
            'patches': 'Patch',
            'patch_repair': 'Patch',
            'lock': 'Lock',
            'locks': 'Lock',
            'lock_repair': 'Lock',
            'garter': 'Garter',
            'garter_repair': 'Garter',
            'elastic': 'Elastic',
            'elastic_repair': 'Elastic',
            'bewang': 'Bewang',
            'bewang_repair': 'Bewang',
            'putol': 'Putol',
            'baston': 'Baston',
            'suklot': 'Suklot',
            'baston_suklot': 'Baston Suklot',
            'baston_putol': 'Baston Putol',
            'ambel': 'Ambel',
            'pasada': 'Pasada',
            'general_repair': 'General Repair',
            'general_tshirt_repair': 'General T-Shirt Repair',
        }
        if repair_type_lower in repair_type_map:
            return repair_type_map[repair_type_lower]
        # Check if it contains any of the repair types
        for key, value in repair_type_map.items():
            if key in repair_type_lower:
                return value
        # Replace underscores with spaces and title case
        formatted = repair_type_str.replace('_', ' ').title()
        return formatted

    def format_customize_type(self, customize_type_str):
        """Format customize type name"""
        if not customize_type_str:
            return None
        # Remove "Customize - " prefix if present
        if "Customize - " in customize_type_str:
            customize_type_str = customize_type_str[11:].strip()
        # Remove "customize - " prefix if present (lowercase)
        if "customize - " in customize_type_str.lower():
            customize_type_str = customize_type_str[customize_type_str.lower().find("customize - ") + 12:].strip()
        # Remove class suffix like "(Class standard)"
        if " (Class " in customize_type_str:
            customize_type_str = customize_type_str.split(" (Class ")[0].strip()
        # Remove timestamp suffix if present
        if " - " in customize_type_str and len(customize_type_str.split(" - ")[-1]) > 10:
            customize_type_str = customize_type_str.split(" - ")[0].strip()
        # Handle common customize types
        customize_type_lower = customize_type_str.lower().strip()
        customize_type_map = {
            'polo': 'Polo',
            'polo_shirt': 'Polo Shirt',
            'blouse': 'Blouse',
            'pants': 'Pants',
            'shorts': 'Shorts',
            'skirt_palda': 'Skirt/Palda',
            'skirt': 'Skirt/Palda',
            'palda': 'Skirt/Palda',
            'uniform': 'Uniform',
            'pe': 'PE',
        }
        if customize_type_lower in customize_type_map:
            return customize_type_map[customize_type_lower]
        # Check if it contains any of the customize types
        for key, value in customize_type_map.items():
            if key in customize_type_lower:
                return value
        # Replace underscores with spaces and title case
        formatted = customize_type_str.replace('_', ' ').title()
        return formatted

    def extract_repair_type(self, order):
        """Extract repair type from order using multiple methods"""
        repair_type = None
        
        # METHOD 1: Check inventory transaction notes
        try:
            transactions = InventoryTransaction.objects.filter(reference_order=order).order_by('-created_at')[:5]
            for transaction in transactions:
                if transaction.notes:
                    notes_lower = transaction.notes.lower()
                    repair_types = ['zipper', 'buttons', 'button', 'patch', 'patches', 'lock', 'locks', 'garter', 
                                   'elastic', 'bewang', 'zipper_replacement', 'button_repair', 'lock_repair', 
                                   'putol', 'baston', 'suklot', 'ambel', 'pasada', 'general_repair', 'general_tshirt_repair']
                    for rt in repair_types:
                        if rt in notes_lower:
                            repair_type = rt
                            break
                    if repair_type:
                        break
        except Exception:
            pass
        
        # METHOD 2: Check order notes
        if not repair_type and order.notes:
            notes_lower = order.notes.lower()
            repair_types = ['zipper', 'buttons', 'button', 'patch', 'patches', 'lock', 'locks', 'garter', 
                           'elastic', 'bewang', 'zipper_replacement', 'button_repair', 'lock_repair', 
                           'putol', 'baston', 'suklot', 'ambel', 'pasada', 'general_repair', 'general_tshirt_repair']
            for rt in repair_types:
                if rt in notes_lower:
                    repair_type = rt
                    break
        
        # METHOD 3: Check order items' product names
        if not repair_type:
            for item in order.items.all():
                if item.product and item.product.name:
                    product_name = item.product.name.lower()
                    repair_types = ['zipper', 'buttons', 'button', 'patch', 'patches', 'lock', 'locks', 'garter', 
                                   'elastic', 'bewang', 'zipper_replacement', 'button_repair', 'lock_repair', 
                                   'putol', 'baston', 'suklot', 'ambel', 'pasada', 'general_repair', 'general_tshirt_repair']
                    for rt in repair_types:
                        if rt in product_name:
                            repair_type = rt
                            break
                    if repair_type:
                        break
        
        return repair_type

    def extract_customize_type(self, order):
        """Extract customize type from order using multiple methods"""
        customize_type = None
        
        # METHOD 1: Check order notes
        if order.notes:
            notes_lower = order.notes.lower()
            customize_types = ['polo', 'polo_shirt', 'blouse', 'pants', 'shorts', 'skirt', 'palda', 
                              'skirt_palda', 'uniform', 'pe']
            for ct in customize_types:
                if ct in notes_lower:
                    customize_type = ct
                    break
        
        # METHOD 2: Check order items' product names
        if not customize_type:
            for item in order.items.all():
                if item.product and item.product.name:
                    product_name = item.product.name.lower()
                    customize_types = ['polo', 'polo_shirt', 'blouse', 'pants', 'shorts', 'skirt', 'palda', 
                                      'skirt_palda', 'uniform', 'pe']
                    for ct in customize_types:
                        if ct in product_name:
                            customize_type = ct
                            break
                    if customize_type:
                        break
                
                # Check product description
                if not customize_type and item.product and item.product.description:
                    desc = item.product.description.lower()
                    if 'type: uniform' in desc or 'type:uniform' in desc:
                        customize_type = 'uniform'
                        break
                    elif 'type: pe' in desc or 'type:pe' in desc:
                        customize_type = 'pe'
                        break
        
        return customize_type

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write(self.style.SUCCESS('Starting order category update...'))
        
        # Get all repair and customize orders
        repair_orders = Order.objects.filter(order_type='repair', is_archived=False).prefetch_related('items__product')
        customize_orders = Order.objects.filter(order_type='customize', is_archived=False).prefetch_related('items__product')
        
        self.stdout.write(f'Found {repair_orders.count()} repair orders')
        self.stdout.write(f'Found {customize_orders.count()} customize orders')
        
        repair_updated = 0
        customize_updated = 0
        repair_skipped = 0
        customize_skipped = 0
        
        # Get or create categories
        repair_category, _ = Category.objects.get_or_create(
            name='Repair Service',
            defaults={'description': 'General repair service category'}
        )
        customize_category, _ = Category.objects.get_or_create(
            name='Customize Service',
            defaults={'description': 'General customize service category'}
        )
        
        # Process repair orders
        self.stdout.write('\n=== Processing Repair Orders ===')
        for order in repair_orders:
            try:
                # Extract repair type
                repair_type = self.extract_repair_type(order)
                
                if repair_type:
                    formatted_type = self.format_repair_type(repair_type)
                    self.stdout.write(f'Order {order.order_identifier}: Extracted type = {formatted_type}')
                    
                    # Check if order items have generic "Repair Service" product
                    needs_update = False
                    for item in order.items.all():
                        if item.product and item.product.name:
                            product_name_lower = item.product.name.lower()
                            if 'repair service' in product_name_lower and formatted_type != 'Repair Service':
                                needs_update = True
                                break
                    
                    if needs_update and not dry_run:
                        # Try to find or create a more specific product
                        specific_product_name = f"Repair - {formatted_type}"
                        specific_product = Product.objects.filter(
                            name__iexact=specific_product_name,
                            product_type='service',
                            is_archived=False,
                            is_active=True
                        ).first()
                        
                        if not specific_product:
                            # Try to find similar product
                            specific_product = Product.objects.filter(
                                name__icontains=formatted_type.lower(),
                                product_type='service',
                                is_archived=False,
                                is_active=True
                            ).first()
                        
                        if specific_product:
                            # Update order items to use the specific product
                            for item in order.items.all():
                                if item.product and 'repair service' in item.product.name.lower():
                                    item.product = specific_product
                                    item.save()
                                    self.stdout.write(f'  Updated item to use product: {specific_product.name}')
                            repair_updated += 1
                        else:
                            self.stdout.write(f'  Could not find specific product for: {formatted_type}')
                            repair_skipped += 1
                    elif needs_update:
                        self.stdout.write(f'  [DRY RUN] Would update to: {formatted_type}')
                        repair_updated += 1
                    else:
                        repair_skipped += 1
                else:
                    self.stdout.write(f'Order {order.order_identifier}: No repair type found')
                    repair_skipped += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing order {order.order_identifier}: {e}'))
                repair_skipped += 1
        
        # Process customize orders
        self.stdout.write('\n=== Processing Customize Orders ===')
        for order in customize_orders:
            try:
                # Extract customize type
                customize_type = self.extract_customize_type(order)
                
                if customize_type:
                    formatted_type = self.format_customize_type(customize_type)
                    self.stdout.write(f'Order {order.order_identifier}: Extracted type = {formatted_type}')
                    
                    # Check if order items have generic "Customize Service" product
                    needs_update = False
                    for item in order.items.all():
                        if item.product and item.product.name:
                            product_name_lower = item.product.name.lower()
                            if 'customize service' in product_name_lower and formatted_type != 'Customize Service':
                                needs_update = True
                                break
                    
                    if needs_update and not dry_run:
                        # Try to find or create a more specific product
                        specific_product_name = f"Customize - {formatted_type}"
                        specific_product = Product.objects.filter(
                            name__iexact=specific_product_name,
                            product_type='service',
                            is_archived=False,
                            is_active=True
                        ).first()
                        
                        if not specific_product:
                            # Try to find similar product
                            specific_product = Product.objects.filter(
                                name__icontains=formatted_type.lower(),
                                product_type='service',
                                is_archived=False,
                                is_active=True
                            ).first()
                        
                        if specific_product:
                            # Update order items to use the specific product
                            for item in order.items.all():
                                if item.product and 'customize service' in item.product.name.lower():
                                    item.product = specific_product
                                    item.save()
                                    self.stdout.write(f'  Updated item to use product: {specific_product.name}')
                            customize_updated += 1
                        else:
                            self.stdout.write(f'  Could not find specific product for: {formatted_type}')
                            customize_skipped += 1
                    elif needs_update:
                        self.stdout.write(f'  [DRY RUN] Would update to: {formatted_type}')
                        customize_updated += 1
                    else:
                        customize_skipped += 1
                else:
                    self.stdout.write(f'Order {order.order_identifier}: No customize type found')
                    customize_skipped += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing order {order.order_identifier}: {e}'))
                customize_skipped += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('SUMMARY:'))
        self.stdout.write(f'Repair orders updated: {repair_updated}')
        self.stdout.write(f'Repair orders skipped: {repair_skipped}')
        self.stdout.write(f'Customize orders updated: {customize_updated}')
        self.stdout.write(f'Customize orders skipped: {customize_skipped}')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN. No changes were made.'))
            self.stdout.write('Run without --dry-run to apply changes.')

