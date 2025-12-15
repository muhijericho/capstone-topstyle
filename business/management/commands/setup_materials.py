from django.core.management.base import BaseCommand
from business.models import MaterialType, MaterialPricing


class Command(BaseCommand):
    help = 'Set up initial material types and pricing data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up material types and pricing...')
        
        # Create material types
        material_types_data = [
            {
                'name': 'Buttons',
                'description': 'Various types of buttons for clothing - formal, normal, assorted colors',
                'unit_of_measurement': 'piece',
                'pricing_options': [
                    {'pricing_type': 'per_piece', 'buy_price': 2.00, 'sell_price': 3.00},
                    {'pricing_type': 'per_bundle', 'bundle_size': 12, 'buy_price': 20.00, 'sell_price': 30.00},
                ]
            },
            {
                'name': 'Zippers',
                'description': 'Various sizes and types of zippers - #3, #5, #7, #8, #10',
                'unit_of_measurement': 'piece',
                'pricing_options': [
                    {'pricing_type': 'per_piece', 'buy_price': 15.00, 'sell_price': 25.00},
                    {'pricing_type': 'per_bundle', 'bundle_size': 10, 'buy_price': 120.00, 'sell_price': 200.00},
                ]
            },
            {
                'name': 'Patches',
                'description': 'Decorative patches and patches for repairs',
                'unit_of_measurement': 'piece',
                'pricing_options': [
                    {'pricing_type': 'per_piece', 'buy_price': 5.00, 'sell_price': 8.00},
                    {'pricing_type': 'per_bundle', 'bundle_size': 20, 'buy_price': 80.00, 'sell_price': 120.00},
                ]
            },
            {
                'name': 'Thread',
                'description': 'Sewing thread in various colors - polyester, edging, rugged',
                'unit_of_measurement': 'meter',
                'pricing_options': [
                    {'pricing_type': 'per_meter', 'buy_price': 0.50, 'sell_price': 0.75},
                    {'pricing_type': 'per_bundle', 'bundle_size': 100, 'buy_price': 40.00, 'sell_price': 60.00},
                ]
            },
            {
                'name': 'Needles',
                'description': 'Sewing needles of various sizes and types',
                'unit_of_measurement': 'piece',
                'pricing_options': [
                    {'pricing_type': 'per_piece', 'buy_price': 1.00, 'sell_price': 1.50},
                    {'pricing_type': 'per_bundle', 'bundle_size': 50, 'buy_price': 40.00, 'sell_price': 60.00},
                ]
            },
            {
                'name': 'Measuring Tape',
                'description': 'Flexible measuring tapes for tailoring',
                'unit_of_measurement': 'piece',
                'pricing_options': [
                    {'pricing_type': 'per_piece', 'buy_price': 25.00, 'sell_price': 40.00},
                    {'pricing_type': 'per_bundle', 'bundle_size': 5, 'buy_price': 100.00, 'sell_price': 150.00},
                ]
            },
            {
                'name': 'Locks',
                'description': 'Various types of locks and fasteners',
                'unit_of_measurement': 'piece',
                'pricing_options': [
                    {'pricing_type': 'per_piece', 'buy_price': 8.00, 'sell_price': 12.00},
                    {'pricing_type': 'per_bundle', 'bundle_size': 15, 'buy_price': 100.00, 'sell_price': 150.00},
                ]
            },
            {
                'name': 'Fabric',
                'description': 'Various types of fabric materials',
                'unit_of_measurement': 'meter',
                'pricing_options': [
                    {'pricing_type': 'per_meter', 'buy_price': 50.00, 'sell_price': 75.00},
                    {'pricing_type': 'per_yard', 'buy_price': 45.00, 'sell_price': 68.00},
                ]
            },
            {
                'name': 'Elastic',
                'description': 'Elastic bands for clothing',
                'unit_of_measurement': 'meter',
                'pricing_options': [
                    {'pricing_type': 'per_meter', 'buy_price': 5.00, 'sell_price': 8.00},
                    {'pricing_type': 'per_bundle', 'bundle_size': 50, 'buy_price': 200.00, 'sell_price': 350.00},
                ]
            },
            {
                'name': 'Ribbons',
                'description': 'Decorative ribbons and trims',
                'unit_of_measurement': 'meter',
                'pricing_options': [
                    {'pricing_type': 'per_meter', 'buy_price': 3.00, 'sell_price': 5.00},
                    {'pricing_type': 'per_bundle', 'bundle_size': 20, 'buy_price': 50.00, 'sell_price': 85.00},
                ]
            },
            {
                'name': 'Garter',
                'description': 'Elastic garter bands for clothing',
                'unit_of_measurement': 'meter',
                'pricing_options': [
                    {'pricing_type': 'per_meter', 'buy_price': 8.00, 'sell_price': 12.00},
                    {'pricing_type': 'per_bundle', 'bundle_size': 25, 'buy_price': 150.00, 'sell_price': 250.00},
                ]
            },
        ]
        
        for material_data in material_types_data:
            material_type, created = MaterialType.objects.get_or_create(
                name=material_data['name'],
                defaults={
                    'description': material_data['description'],
                    'unit_of_measurement': material_data['unit_of_measurement'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created material type: {material_type.name}')
            else:
                self.stdout.write(f'Material type already exists: {material_type.name}')
            
            # Create pricing options
            for i, pricing_data in enumerate(material_data['pricing_options']):
                pricing, created = MaterialPricing.objects.get_or_create(
                    material_type=material_type,
                    pricing_type=pricing_data['pricing_type'],
                    bundle_size=pricing_data.get('bundle_size'),
                    defaults={
                        'buy_price_per_unit': pricing_data['buy_price'],
                        'sell_price_per_unit': pricing_data['sell_price'],
                        'is_default': i == 0  # First option is default
                    }
                )
                
                if created:
                    self.stdout.write(f'  Created pricing: {pricing}')
                else:
                    self.stdout.write(f'  Pricing already exists: {pricing}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up material types and pricing!')
        )

