from django.core.management.base import BaseCommand
from business.models import Order
from django.utils import timezone
from django.db import transaction

class Command(BaseCommand):
    help = 'BACKEND: Automatically update rental order statuses based on due dates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write(self.style.SUCCESS('BACKEND: Starting automatic rental order status updates...'))

        # Get all rental orders that need status updates
        rental_orders = Order.objects.filter(
            order_type__in=['rent', 'rental'],
            status__in=['rented', 'almost_due']
        ).exclude(due_date__isnull=True)
        
        self.stdout.write(f'Found {rental_orders.count()} rental orders to check')

        updated_almost_due = 0
        updated_due = 0
        updated_overdue = 0
        
        with transaction.atomic():
            for order in rental_orders:
                self.stdout.write(f'\nChecking Order: {order.order_identifier}')
                self.stdout.write(f'   Current Status: {order.status}')
                self.stdout.write(f'   Due Date: {order.due_date}')
                self.stdout.write(f'   Days Until Due: {order.days_until_due}')
                
                # Check if order is overdue
                if order.days_until_due < 0:
                    if order.status != 'overdue':
                        if not dry_run:
                            order.status = 'overdue'
                            order.save()
                        self.stdout.write(f'   Status updated: {order.status} -> overdue')
                        updated_overdue += 1
                
                # Check if order is due today
                elif order.is_due_today:
                    if order.status != 'due':
                        if not dry_run:
                            order.status = 'due'
                            order.save()
                        self.stdout.write(f'   Status updated: {order.status} -> due')
                        updated_due += 1
                
                # Check if order is 1 day before due
                elif order.is_one_day_before_due:
                    if order.status != 'almost_due':
                        if not dry_run:
                            order.status = 'almost_due'
                            order.save()
                        self.stdout.write(f'   Status updated: {order.status} -> almost_due')
                        updated_almost_due += 1
                
                else:
                    self.stdout.write(f'   No status update needed')

        # Summary
        self.stdout.write(f'\nBACKEND SUMMARY:')
        self.stdout.write(f'   Orders updated to "almost_due": {updated_almost_due}')
        self.stdout.write(f'   Orders updated to "due": {updated_due}')
        self.stdout.write(f'   Orders updated to "overdue": {updated_overdue}')
        
        if not dry_run:
            # Verify the updates
            almost_due_count = Order.objects.filter(
                order_type__in=['rent', 'rental'],
                status='almost_due'
            ).count()
            
            due_count = Order.objects.filter(
                order_type__in=['rent', 'rental'],
                status='due'
            ).count()
            
            overdue_count = Order.objects.filter(
                order_type__in=['rent', 'rental'],
                status='overdue'
            ).count()
            
            self.stdout.write(f'   Current "almost_due" orders: {almost_due_count}')
            self.stdout.write(f'   Current "due" orders: {due_count}')
            self.stdout.write(f'   Current "overdue" orders: {overdue_count}')
            
            if updated_almost_due + updated_due + updated_overdue > 0:
                self.stdout.write(self.style.SUCCESS('SUCCESS: Rental order statuses updated automatically!'))
            else:
                self.stdout.write(self.style.SUCCESS('SUCCESS: All rental order statuses are up to date!'))
        else:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - Run without --dry-run to apply changes'))




















































