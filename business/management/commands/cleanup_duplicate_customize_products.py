"""
Management command to find and remove duplicate customize products
"""
from django.core.management.base import BaseCommand
from business.customize_product_manager import (
    find_duplicate_customize_products,
    remove_duplicate_customize_products
)


class Command(BaseCommand):
    help = 'Find and remove duplicate customize products based on image filename, hash, or name+category'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--keep-newest',
            action='store_true',
            help='Keep the newest duplicate instead of the oldest (default: keep oldest)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        keep_newest = options['keep_newest']
        force = options['force']
        
        self.stdout.write('Scanning for duplicate customize products...')
        self.stdout.write('')
        
        # Find duplicates
        duplicates = find_duplicate_customize_products()
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicate customize products found. System is clean!'))
            return
        
        # Show what was found
        self.stdout.write(self.style.WARNING('='*60))
        self.stdout.write(self.style.WARNING('DUPLICATE CUSTOMIZE PRODUCTS FOUND:'))
        self.stdout.write(self.style.WARNING('='*60))
        self.stdout.write('')
        
        total_duplicates = 0
        for key, duplicate_info in duplicates.items():
            method = duplicate_info['method']
            products = duplicate_info['products']
            total_duplicates += len(products)
            
            self.stdout.write(f'Duplicate Group ({method}): {duplicate_info["identifier"]}')
            self.stdout.write(f'  Found {len(products)} duplicate products:')
            for product in products:
                self.stdout.write(f'    - ID {product.id}: "{product.name}" (Created: {product.created_at})')
            self.stdout.write('')
        
        self.stdout.write(f'Total duplicate groups: {len(duplicates)}')
        self.stdout.write(f'Total duplicate products found: {total_duplicates}')
        self.stdout.write('')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No products were deleted'))
            self.stdout.write('Run without --dry-run to actually remove duplicates')
            return
        
        # Remove duplicates
        keep_oldest = not keep_newest
        result = remove_duplicate_customize_products(dry_run=False, keep_oldest=keep_oldest)
        
        if not force:
            self.stdout.write('')
            confirm = input(f'Are you sure you want to archive {result["products_to_delete"]} duplicate products? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Deletion cancelled.'))
                return
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('CLEANUP COMPLETE:'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'  Duplicate groups processed: {result["duplicate_groups"]}'))
        self.stdout.write(self.style.SUCCESS(f'  Products kept: {result["products_to_keep"]}'))
        self.stdout.write(self.style.SUCCESS(f'  Products archived: {result["products_to_delete"]}'))
        
        if result['deleted_products']:
            self.stdout.write('')
            self.stdout.write('Archived products:')
            for product in result['deleted_products']:
                self.stdout.write(f'  - ID {product["id"]}: "{product["name"]}"')
        
        self.stdout.write(self.style.SUCCESS('='*60))

