"""
Static Data Manager - Prevents and removes static/dummy data from the system
"""
from django.db.models import Q
from .models import Product, Order, OrderItem, Customer, Sales


def is_static_product(product):
    """
    Check if a product is static/dummy data based on naming patterns
    """
    if not product:
        return False
    
    name = product.name.lower()
    
    # Patterns that indicate static/auto-generated products
    static_patterns = [
        'repair -',
        'customize -',
        'rental -',
        'service -',
        'test product',
        'sample product',
        'dummy product',
        'example product',
        'repair service',  # Generic repair service (static)
        'customize service',  # Generic customize service (static)
        'general repair service',  # Generic repair service (static)
    ]
    
    # Check if name matches any static pattern (case-insensitive)
    for pattern in static_patterns:
        if pattern.lower() in name.lower():
            return True
    
    # Check for exact matches of generic service names
    generic_service_names = [
        'repair service',
        'customize service',
        'customization service',
        'general repair service',
    ]
    if name.lower().strip() in generic_service_names:
        return True
    
    # Check if it's a service product with auto-generated description
    if product.product_type == 'service':
        if product.description and any(keyword in product.description.lower() for keyword in ['repair service:', 'customization service:', 'rental item:']):
            return True
    
    # Check if product has no real inventory data (quantity 0 or 1, cost 0)
    if product.product_type == 'service' and product.quantity <= 1 and product.cost == 0:
        # Additional check: if created recently and matches pattern
        if any(pattern in name for pattern in ['repair', 'customize', 'rental']):
            return True
    
    return False


def is_static_order(order):
    """
    Check if an order is static/dummy data
    """
    if not order:
        return False
    
    # Check if order has static products
    static_items = order.items.filter(product__name__icontains='repair -').exists() or \
                   order.items.filter(product__name__icontains='customize -').exists() or \
                   order.items.filter(product__name__icontains='rental -').exists()
    
    if static_items:
        return True
    
    # Check for test customers
    if order.customer:
        test_customer_patterns = ['test', 'sample', 'dummy', 'example', 'john doe', 'jane smith']
        if any(pattern in order.customer.name.lower() for pattern in test_customer_patterns):
            return True
    
    return False


def get_static_products():
    """
    Get all static products in the system
    """
    products = Product.objects.all()
    static_products = []
    
    for product in products:
        if is_static_product(product):
            static_products.append(product)
    
    return static_products


def get_static_orders():
    """
    Get all orders that contain static products
    """
    orders = Order.objects.prefetch_related('items__product').all()
    static_orders = []
    
    for order in orders:
        if is_static_order(order):
            static_orders.append(order)
    
    return static_orders


def remove_static_data(dry_run=True):
    """
    Remove all static data from the system
    
    Args:
        dry_run: If True, only return counts without deleting
    
    Returns:
        dict with counts of items that would be/were removed
    """
    static_products = get_static_products()
    static_orders = get_static_orders()
    
    # Get order items with static products
    static_order_items = OrderItem.objects.filter(
        product__in=static_products
    )
    
    # Get sales records for static orders
    static_sales = Sales.objects.filter(order__in=static_orders)
    
    counts = {
        'products': len(static_products),
        'orders': len(static_orders),
        'order_items': static_order_items.count(),
        'sales': static_sales.count(),
    }
    
    if not dry_run:
        # Delete in correct order to avoid foreign key constraints
        static_sales.delete()
        static_order_items.delete()
        static_orders.delete()
        static_products.delete()
    
    return counts


def validate_product_exists(product_name, product_type=None, raise_error=True):
    """
    Validate that a product exists in the database.
    Prevents auto-creation of static products.
    
    Args:
        product_name: Name of the product to find
        product_type: Optional product type filter
        raise_error: If True, raise exception if not found
    
    Returns:
        Product object if found, None otherwise
    
    Raises:
        Product.DoesNotExist if raise_error=True and product not found
    """
    try:
        query = Product.objects.filter(name=product_name, is_archived=False, is_active=True)
        if product_type:
            query = query.filter(product_type=product_type)
        
        product = query.first()
        
        if not product and raise_error:
            raise Product.DoesNotExist(f'Product "{product_name}" not found. Please add it to inventory first.')
        
        return product
    except Product.DoesNotExist as e:
        if raise_error:
            raise
        return None



