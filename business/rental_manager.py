from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, InventoryTransaction
import logging

logger = logging.getLogger(__name__)

class RentalStatusManager:
    """
    Comprehensive rental status management system
    Handles all rental status updates across the entire application
    """
    
    @staticmethod
    def mark_products_as_rented(order, items=None):
        """
        Mark products as rented when a rental order is created
        Updates status across all systems
        """
        try:
            with transaction.atomic():
                updated_count = 0
                current_time = timezone.now()
                
                logger.info(f"[RENTAL_MANAGER] Starting rental status update for order {order.order_identifier}")
                
                # Get items from order if not provided
                if items is None:
                    items = order.items.filter(product__product_type='rental')
                else:
                    # Convert items list to OrderItem queryset format
                    item_objects = []
                    for item in items:
                        try:
                            product = Product.objects.get(name=item.get('name'), product_type='rental')
                            item_objects.append({
                                'product': product,
                                'quantity': int(item.get('quantity', 1)),
                                'cost': float(item.get('cost', 0))
                            })
                        except Product.DoesNotExist:
                            logger.warning(f"[RENTAL_MANAGER] Product '{item.get('name')}' not found")
                            continue
                    items = item_objects
                
                logger.info(f"[RENTAL_MANAGER] Processing {len(items)} rental items")
                
                for item in items:
                    if hasattr(item, 'product'):  # OrderItem object
                        product = item.product
                        quantity = item.quantity
                    else:  # Dictionary format
                        product = item['product']
                        quantity = item['quantity']
                    
                    # Skip if product is not rental type
                    if product.product_type != 'rental':
                        continue
                    
                    # Skip if already rented
                    if product.rental_status == 'rented':
                        logger.warning(f"[RENTAL_MANAGER] Product {product.name} is already rented, skipping")
                        continue
                    
                    # Update product status
                    old_status = product.rental_status
                    product.rental_status = 'rented'
                    product.current_rental_order = order
                    product.rental_start_date = current_time
                    product.rental_due_date = current_time + timezone.timedelta(days=3)
                    product.save()
                    
                    logger.info(f"[RENTAL_MANAGER] Product {product.name} (ID: {product.id}) status changed from '{old_status}' to 'rented'")
                    
                    # Create inventory transaction
                    try:
                        InventoryTransaction.objects.create(
                            product=product,
                            transaction_type='rental_out',
                            quantity=quantity,
                            reference_order=order,
                            notes=f'Rental item rented for order {order.order_identifier}',
                            created_by=order.created_by if hasattr(order, 'created_by') else None
                        )
                        logger.info(f"[RENTAL_MANAGER] Created inventory transaction for {product.name}")
                    except Exception as trans_error:
                        logger.error(f"[RENTAL_MANAGER] Failed to create inventory transaction: {trans_error}")
                    
                    updated_count += 1
                
                logger.info(f"[RENTAL_MANAGER] Completed. Updated {updated_count} products to rented status")
                return updated_count
                
        except Exception as e:
            logger.error(f"[RENTAL_MANAGER] Error in mark_products_as_rented: {e}")
            return 0
    
    @staticmethod
    def mark_products_as_available(order, user=None):
        """
        Mark products as available when a rental order is returned
        Updates status across all systems
        """
        try:
            with transaction.atomic():
                updated_count = 0
                
                logger.info(f"[RENTAL_MANAGER] Starting return process for order {order.order_identifier}")
                
                # Get all rental items in this order
                rental_items = order.items.filter(product__product_type='rental')
                logger.info(f"[RENTAL_MANAGER] Found {rental_items.count()} rental items to return")
                
                for item in rental_items:
                    product = item.product
                    
                    logger.info(f"[RENTAL_MANAGER] Processing return for product: {product.name} (ID: {product.id})")
                    logger.info(f"[RENTAL_MANAGER] Current rental status: {product.rental_status}")
                    
                    # Update product status to available
                    old_status = product.rental_status
                    product.rental_status = 'available'
                    product.current_rental_order = None
                    product.rental_start_date = None
                    product.rental_due_date = None
                    product.save()
                    
                    logger.info(f"[RENTAL_MANAGER] Product {product.name} status changed from '{old_status}' to 'available'")
                    
                    # Create inventory transaction
                    try:
                        InventoryTransaction.objects.create(
                            product=product,
                            transaction_type='rental_in',
                            quantity=item.quantity,
                            reference_order=order,
                            notes=f'Rental item returned for order {order.order_identifier}',
                            created_by=user
                        )
                        logger.info(f"[RENTAL_MANAGER] Created return inventory transaction for {product.name}")
                    except Exception as trans_error:
                        logger.error(f"[RENTAL_MANAGER] Failed to create return inventory transaction: {trans_error}")
                    
                    updated_count += 1
                
                logger.info(f"[RENTAL_MANAGER] Return process completed. Updated {updated_count} products to available")
                return updated_count
                
        except Exception as e:
            logger.error(f"[RENTAL_MANAGER] Error in mark_products_as_available: {e}")
            return 0
    
    @staticmethod
    def get_rental_status_for_all_products():
        """
        Get comprehensive rental status for all products
        Used by API endpoints to provide real-time status
        """
        try:
            rental_products = Product.objects.filter(
                is_active=True,
                is_archived=False,
                product_type='rental'
            ).select_related('category', 'current_rental_order')
            
            status_data = {}
            
            for product in rental_products:
                # Determine rental status using multiple methods
                # PRIORITY: Check active orders first (most reliable source of truth)
                is_rented = False
                rental_info = {
                    'product_id': product.id,
                    'product_name': product.name,
                    'rental_status': product.rental_status,
                    'has_current_order': bool(product.current_rental_order),
                    'current_order_id': product.current_rental_order.id if product.current_rental_order else None,
                    'rental_start_date': product.rental_start_date.isoformat() if product.rental_start_date else None,
                    'rental_due_date': product.rental_due_date.isoformat() if product.rental_due_date else None,
                    'is_overdue': False
                }
                
                # FIRST: Check for active rental orders containing this product (most reliable)
                # Check both through OrderItems and through direct order filtering
                # Active rental orders are those that haven't been returned, completed, or cancelled
                
                # Method 1: Check through OrderItems (most direct)
                from .models import OrderItem
                active_order_items = OrderItem.objects.filter(
                    product=product,
                    order__order_type__in=['rent', 'rental'],
                    order__status__in=['rented', 'pending', 'almost_due', 'due', 'overdue', 'in_progress']
                ).select_related('order').first()
                
                # Log if we found an order item
                if active_order_items:
                    logger.debug(f"[RENTAL_MANAGER] Product {product.name} (ID: {product.id}) found in active order {active_order_items.order.order_identifier}")
                
                # Method 2: Check through Order reverse relation (backup)
                active_rental_order = None
                if active_order_items:
                    active_rental_order = active_order_items.order
                else:
                    active_rental_order = Order.objects.filter(
                        order_type__in=['rent', 'rental'],
                        status__in=['rented', 'pending', 'almost_due', 'due', 'overdue', 'in_progress'],
                        items__product=product
                    ).distinct().first()
                
                if active_rental_order:
                    is_rented = True
                    rental_info['rental_status'] = 'rented'
                    rental_info['has_current_order'] = True
                    rental_info['current_order_id'] = active_rental_order.id
                    
                    # Get rental dates from order if available
                    # Order has due_date, Product has rental_start_date and rental_due_date
                    if active_rental_order.created_at:
                        rental_info['rental_start_date'] = active_rental_order.created_at.isoformat()
                    if active_rental_order.due_date:
                        rental_info['rental_due_date'] = active_rental_order.due_date.isoformat()
                        # Check if overdue or almost due
                        now = timezone.now()
                        time_until_due = active_rental_order.due_date - now
                        days_until_due = time_until_due.days
                        
                        if now > active_rental_order.due_date:
                            # Overdue
                            rental_info['is_overdue'] = True
                            rental_info['is_almost_due'] = False
                            rental_info['rental_status'] = 'overdue'
                        elif days_until_due == 0 or days_until_due == 1 or (time_until_due.total_seconds() > 0 and time_until_due.total_seconds() <= 86400):
                            # Almost due (1 day before or on due date, or within 24 hours)
                            rental_info['is_overdue'] = True  # Treat almost due as overdue for display
                            rental_info['is_almost_due'] = True
                            rental_info['rental_status'] = 'overdue'
                
                # SECOND: Check current_rental_order field
                elif product.current_rental_order:
                    is_rented = True
                    rental_info['rental_status'] = 'rented'
                    rental_info['has_current_order'] = True
                    rental_info['current_order_id'] = product.current_rental_order.id
                    # Check if overdue or almost due
                    if product.rental_due_date:
                        now = timezone.now()
                        time_until_due = product.rental_due_date - now
                        days_until_due = time_until_due.days
                        
                        if now > product.rental_due_date:
                            # Overdue
                            rental_info['is_overdue'] = True
                            rental_info['is_almost_due'] = False
                            rental_info['rental_status'] = 'overdue'
                        elif days_until_due == 0 or days_until_due == 1 or (time_until_due.total_seconds() > 0 and time_until_due.total_seconds() <= 86400):
                            # Almost due (1 day before or on due date, or within 24 hours)
                            rental_info['is_overdue'] = True  # Treat almost due as overdue for display
                            rental_info['is_almost_due'] = True
                            rental_info['rental_status'] = 'overdue'
                
                # THIRD: Check product.rental_status field (may be out of sync)
                elif product.rental_status == 'rented':
                    is_rented = True
                    # Check if overdue or almost due
                    if product.rental_due_date:
                        now = timezone.now()
                        time_until_due = product.rental_due_date - now
                        days_until_due = time_until_due.days
                        
                        if now > product.rental_due_date:
                            # Overdue
                            rental_info['is_overdue'] = True
                            rental_info['is_almost_due'] = False
                            rental_info['rental_status'] = 'overdue'
                        elif days_until_due == 0 or days_until_due == 1 or (time_until_due.total_seconds() > 0 and time_until_due.total_seconds() <= 86400):
                            # Almost due (1 day before or on due date, or within 24 hours)
                            rental_info['is_overdue'] = True  # Treat almost due as overdue for display
                            rental_info['is_almost_due'] = True
                            rental_info['rental_status'] = 'overdue'
                
                rental_info['is_rented'] = is_rented
                status_data[product.id] = rental_info
                
                # Log rented products for debugging
                if is_rented:
                    logger.info(f"[RENTAL_MANAGER] Product {product.name} (ID: {product.id}) marked as RENTED")
            
            rented_count = sum(1 for info in status_data.values() if info.get('is_rented', False))
            logger.info(f"[RENTAL_MANAGER] Generated status for {len(status_data)} products, {rented_count} are rented")
            return status_data
            
        except Exception as e:
            logger.error(f"[RENTAL_MANAGER] Error in get_rental_status_for_all_products: {e}")
            return {}
    
    @staticmethod
    def get_order_rental_status(order):
        """
        Get rental status information for a specific order
        Returns a dictionary with overdue_items, total_items, and other status info
        """
        try:
            from .models import OrderItem
            
            # Get all rental items in this order
            rental_items = order.items.filter(product__product_type='rental').select_related('product')
            
            total_items = rental_items.count()
            overdue_items = 0
            almost_due_items = 0
            items_info = []
            
            now = timezone.now()
            
            for item in rental_items:
                product = item.product
                is_overdue = False
                is_almost_due = False
                
                # Check if product is overdue or almost due
                if product.rental_due_date:
                    time_until_due = product.rental_due_date - now
                    days_until_due = time_until_due.days
                    
                    if now > product.rental_due_date:
                        # Overdue
                        is_overdue = True
                        overdue_items += 1
                    elif days_until_due == 0 or days_until_due == 1 or (time_until_due.total_seconds() > 0 and time_until_due.total_seconds() <= 86400):
                        # Almost due (1 day before or on due date, or within 24 hours)
                        is_almost_due = True
                        almost_due_items += 1
                        overdue_items += 1  # Count almost due as overdue for display
                
                # Also check order's due_date if product doesn't have one
                elif order.due_date:
                    time_until_due = order.due_date - now
                    days_until_due = time_until_due.days
                    
                    if now > order.due_date:
                        is_overdue = True
                        overdue_items += 1
                    elif days_until_due == 0 or days_until_due == 1 or (time_until_due.total_seconds() > 0 and time_until_due.total_seconds() <= 86400):
                        is_almost_due = True
                        almost_due_items += 1
                        overdue_items += 1
                
                items_info.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': item.quantity,
                    'is_overdue': is_overdue,
                    'is_almost_due': is_almost_due,
                    'due_date': product.rental_due_date.isoformat() if product.rental_due_date else (order.due_date.isoformat() if order.due_date else None)
                })
            
            return {
                'overdue_items': overdue_items,
                'almost_due_items': almost_due_items,
                'total_items': total_items,
                'items': items_info,
                'order_id': order.id,
                'order_identifier': order.order_identifier,
                'order_due_date': order.due_date.isoformat() if order.due_date else None
            }
            
        except Exception as e:
            logger.error(f"[RENTAL_MANAGER] Error in get_order_rental_status: {e}")
            return {
                'overdue_items': 0,
                'almost_due_items': 0,
                'total_items': 0,
                'items': [],
                'order_id': order.id if order else None,
                'order_identifier': order.order_identifier if order else None,
                'order_due_date': None
            }
    
    @staticmethod
    def sync_all_rental_status():
        """
        Sync all rental statuses to ensure consistency
        This can be run as a maintenance task
        """
        try:
            logger.info("[RENTAL_MANAGER] Starting comprehensive rental status sync")
            
            # Get all active rental orders
            active_orders = Order.objects.filter(
                order_type__in=['rent', 'rental'],
                status__in=['rented', 'pending']
            ).prefetch_related('items__product')
            
            logger.info(f"[RENTAL_MANAGER] Found {active_orders.count()} active rental orders")
            
            # Track products that should be rented
            products_that_should_be_rented = set()
            
            for order in active_orders:
                for item in order.items.filter(product__product_type='rental'):
                    products_that_should_be_rented.add(item.product.id)
            
            # Get all rental products
            all_rental_products = Product.objects.filter(
                product_type='rental',
                is_active=True,
                is_archived=False
            )
            
            synced_count = 0
            
            for product in all_rental_products:
                should_be_rented = product.id in products_that_should_be_rented
                is_currently_rented = product.rental_status == 'rented'
                
                if should_be_rented and not is_currently_rented:
                    # Product should be rented but isn't marked as such
                    product.rental_status = 'rented'
                    product.save()
                    logger.info(f"[RENTAL_MANAGER] Synced product {product.name} to rented status")
                    synced_count += 1
                    
                elif not should_be_rented and is_currently_rented:
                    # Product is marked as rented but shouldn't be
                    product.rental_status = 'available'
                    product.current_rental_order = None
                    product.rental_start_date = None
                    product.rental_due_date = None
                    product.save()
                    logger.info(f"[RENTAL_MANAGER] Synced product {product.name} to available status")
                    synced_count += 1
            
            logger.info(f"[RENTAL_MANAGER] Sync completed. Updated {synced_count} products")
            return synced_count
            
        except Exception as e:
            logger.error(f"[RENTAL_MANAGER] Error in sync_all_rental_status: {e}")
            return 0
