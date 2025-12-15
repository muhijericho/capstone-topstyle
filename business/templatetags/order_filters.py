from django import template

register = template.Library()

@register.filter
def group_rental_items(items):
    """
    Groups rental items by category.
    If all items have the same category, returns a single entry with total quantity.
    If items have different categories, returns them grouped by category with quantities.
    Returns a list of dicts: [{'category': 'Coat', 'quantity': 4}, ...]
    """
    try:
        if items is None:
            return []
        
        # Convert queryset to list if needed
        # Check if it's a queryset (has iterator method) or a manager (has all method)
        if hasattr(items, 'all') and not hasattr(items, 'iterator'):
            # It's a manager, get the queryset
            items = items.all()
        if hasattr(items, 'iterator'):
            # It's a queryset, convert to list
            items = list(items)
        elif not isinstance(items, (list, tuple)):
            try:
                items = list(items)
            except (TypeError, AttributeError):
                return []
        
        if not items:
            return []
        
        # Group items by category
        category_groups = {}
        for item in items:
            try:
                # Get category name - never use 'N/A'
                category_name = None
                if hasattr(item, 'product') and item.product:
                    product = item.product
                    if hasattr(product, 'category') and product.category:
                        category_name = product.category.name
                    elif hasattr(product, 'name') and product.name:
                        category_name = product.name
                
                # Ensure we always have a valid category name
                if not category_name or category_name.strip() == '' or category_name == 'N/A':
                    category_name = 'Rental Service'
                
                # Get quantity
                quantity = getattr(item, 'quantity', 0)
                if not isinstance(quantity, (int, float)):
                    try:
                        quantity = int(quantity)
                    except (ValueError, TypeError):
                        quantity = 0
                
                # Sum quantities for same category
                if category_name in category_groups:
                    category_groups[category_name] += quantity
                else:
                    category_groups[category_name] = quantity
            except Exception as e:
                # Skip items that cause errors
                continue
        
        # Convert to list of dicts
        result = [{'category': cat, 'quantity': qty} for cat, qty in category_groups.items()]
        
        return result
    except Exception as e:
        # Return empty list on any error
        return []

@register.filter
def format_rental_categories(items):
    """
    Formats rental categories for display.
    If all items are the same category, shows category once.
    If different categories, shows all categories separated by commas.
    """
    grouped = group_rental_items(items)
    
    if not grouped:
        return 'Rental Service'
    
    # Filter out any 'N/A' categories and replace with 'Rental Service'
    valid_categories = []
    for item in grouped:
        cat = item['category']
        if cat and cat != 'N/A' and cat.strip() != '':
            valid_categories.append(cat)
        else:
            valid_categories.append('Rental Service')
    
    if not valid_categories:
        return 'Rental Service'
    
    # If only one category, return it
    if len(valid_categories) == 1:
        return valid_categories[0]
    
    # Multiple categories, return comma-separated
    return ', '.join(valid_categories)

@register.filter
def format_rental_quantities(items):
    """
    Formats rental quantities for display.
    If all items are the same category, shows total quantity.
    If different categories, shows quantities separated by commas.
    """
    grouped = group_rental_items(items)
    
    if not grouped:
        return '0'
    
    # If only one category, return total quantity
    if len(grouped) == 1:
        return str(grouped[0]['quantity'])
    
    # Multiple categories, return comma-separated quantities
    return ', '.join([str(item['quantity']) for item in grouped])

