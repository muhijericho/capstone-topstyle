"""
Backend manager for customize products to prevent and handle duplicates
"""
import os
from django.db.models import Q, Count
from django.db import transaction
from business.models import Product
import hashlib
from django.core.files.base import ContentFile


def get_image_hash(image_field):
    """
    Get a hash of the image file to compare duplicates
    Returns None if image doesn't exist
    """
    if not image_field or not image_field.name:
        return None
    
    try:
        file_content = None
        
        # Check if this is a newly uploaded file (from request.FILES)
        # These have a 'file' attribute that's already open
        if hasattr(image_field, 'file') and hasattr(image_field.file, 'read'):
            # For new uploads, read from the file object directly
            try:
                # Save current position
                current_pos = image_field.file.tell()
            except (AttributeError, IOError, OSError):
                current_pos = 0
            
            # Reset to beginning and read
            try:
                image_field.file.seek(0)
                file_content = image_field.file.read()
                # Restore position if possible
                try:
                    image_field.file.seek(current_pos)
                except (AttributeError, IOError, OSError):
                    pass
            except (IOError, OSError, AttributeError):
                # If seek/read fails, try reading directly
                try:
                    if hasattr(image_field, 'read'):
                        image_field.seek(0)
                        file_content = image_field.read()
                except (IOError, OSError, AttributeError):
                    return None
        elif hasattr(image_field, 'read'):
            # For file-like objects, try to read directly
            try:
                # Save current position
                try:
                    current_pos = image_field.tell()
                except (AttributeError, IOError, OSError):
                    current_pos = 0
                
                # Reset to beginning and read
                try:
                    image_field.seek(0)
                    file_content = image_field.read()
                    # Restore position
                    try:
                        image_field.seek(current_pos)
                    except (AttributeError, IOError, OSError):
                        pass
                except (IOError, OSError):
                    return None
            except (IOError, OSError, AttributeError):
                return None
        else:
            # For existing saved files (from database), open and read
            try:
                # Check if file is already open
                if hasattr(image_field, 'closed') and not image_field.closed:
                    # File is already open, just read it
                    try:
                        current_pos = image_field.tell()
                        image_field.seek(0)
                        file_content = image_field.read()
                        image_field.seek(current_pos)
                    except (IOError, OSError):
                        return None
                else:
                    # File needs to be opened
                    image_field.open('rb')
                    try:
                        file_content = image_field.read()
                    finally:
                        image_field.close()
            except (IOError, OSError, AttributeError):
                return None
        
        # Calculate hash if we have content
        if file_content:
            file_hash = hashlib.md5(file_content).hexdigest()
            return file_hash
        
        return None
    except Exception as e:
        # Log error for debugging but don't fail
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error getting image hash: {e}")
        return None


def get_image_filename(image_field):
    """
    Extract just the filename from the image field
    """
    if not image_field or not image_field.name:
        return None
    
    # Get the last part of the path (filename)
    return os.path.basename(image_field.name)


def find_duplicate_customize_products():
    """
    Find all duplicate customize products based on:
    1. Same image filename (base name without extension)
    2. Same image hash (actual file content)
    3. Same name + category combination
    
    Returns a dictionary with groups of duplicate products
    """
    customize_products = Product.objects.filter(
        product_type='service',
        is_archived=False,
        is_active=True
    ).select_related('category').order_by('created_at', 'id')
    
    # Group by image filename (base name)
    duplicates_by_filename = {}
    duplicates_by_hash = {}
    duplicates_by_name_category = {}
    
    for product in customize_products:
        # Check by image filename
        if product.image:
            filename = get_image_filename(product.image)
            if filename:
                base_name = os.path.splitext(filename)[0].lower()
                if base_name not in duplicates_by_filename:
                    duplicates_by_filename[base_name] = []
                duplicates_by_filename[base_name].append(product)
            
            # Check by image hash
            image_hash = get_image_hash(product.image)
            if image_hash:
                if image_hash not in duplicates_by_hash:
                    duplicates_by_hash[image_hash] = []
                duplicates_by_hash[image_hash].append(product)
        
        # Check by name + category
        key = f"{product.name.lower().strip()}_{product.category.id if product.category else 'none'}"
        if key not in duplicates_by_name_category:
            duplicates_by_name_category[key] = []
        duplicates_by_name_category[key].append(product)
    
    # Filter to only return groups with duplicates (2+ items)
    all_duplicates = {}
    
    # Merge duplicates from all methods
    for base_name, products in duplicates_by_filename.items():
        if len(products) > 1:
            key = f"filename_{base_name}"
            all_duplicates[key] = {
                'method': 'filename',
                'identifier': base_name,
                'products': products
            }
    
    for img_hash, products in duplicates_by_hash.items():
        if len(products) > 1:
            key = f"hash_{img_hash}"
            if key not in all_duplicates or len(products) > len(all_duplicates[key]['products']):
                all_duplicates[key] = {
                    'method': 'hash',
                    'identifier': img_hash,
                    'products': products
                }
    
    for name_cat_key, products in duplicates_by_name_category.items():
        if len(products) > 1:
            key = f"name_cat_{name_cat_key}"
            all_duplicates[key] = {
                'method': 'name_category',
                'identifier': name_cat_key,
                'products': products
            }
    
    return all_duplicates


def remove_duplicate_customize_products(dry_run=True, keep_oldest=True):
    """
    Remove duplicate customize products, keeping one instance
    
    Args:
        dry_run: If True, only report what would be deleted without actually deleting
        keep_oldest: If True, keep the oldest product (by created_at). If False, keep the newest.
    
    Returns:
        Dictionary with counts of found and removed duplicates
    """
    duplicates = find_duplicate_customize_products()
    
    products_to_delete = []
    products_to_keep = []
    
    # Process each duplicate group
    for key, duplicate_info in duplicates.items():
        products = duplicate_info['products']
        
        # Sort by created_at and id to ensure consistent selection
        products = sorted(products, key=lambda p: (p.created_at, p.id), reverse=not keep_oldest)
        
        # Keep the first one (oldest or newest based on keep_oldest)
        product_to_keep = products[0]
        products_to_keep.append(product_to_keep)
        
        # Mark the rest for deletion
        for product in products[1:]:
            products_to_delete.append(product)
    
    # Remove duplicates from deletion list (in case a product appears in multiple groups)
    products_to_delete = list(set(products_to_delete))
    
    result = {
        'duplicate_groups': len(duplicates),
        'total_duplicates_found': sum(len(info['products']) for info in duplicates.values()),
        'products_to_keep': len(products_to_keep),
        'products_to_delete': len(products_to_delete),
        'deleted_products': []
    }
    
    if dry_run:
        return result
    
    # Actually delete the duplicates
    if products_to_delete:
        with transaction.atomic():
            for product in products_to_delete:
                product_name = product.name
                product_id = product.id
                # Archive instead of delete to preserve order history
                product.is_archived = True
                product.is_active = False
                product.save()
                result['deleted_products'].append({
                    'id': product_id,
                    'name': product_name
                })
    
    return result


def get_unique_customize_products():
    """
    Get customize products with duplicates removed in real-time
    This ensures the inventory view always shows unique products
    
    IMPORTANT: Only returns products that:
    1. Have an image (customize products are visual)
    2. Are NOT repair products (exclude "Repair -" prefix)
    3. Are service type products
    """
    customize_products = Product.objects.filter(
        product_type='service',
        is_archived=False,
        is_active=True,
        image__isnull=False  # Only products with images
    ).exclude(
        name__istartswith='Repair -'  # Exclude repair products
    ).exclude(
        name__istartswith='repair -'  # Exclude repair products (case-insensitive)
    ).select_related('category').order_by('-created_at', '-id')
    
    seen_images = {}
    seen_hashes = {}
    seen_name_category = {}
    unique_products = []
    seen_product_ids = set()  # Track product IDs to prevent any duplicates
    
    for product in customize_products:
        # Skip if we've already added this exact product ID
        if product.id in seen_product_ids:
            continue
            
        is_duplicate = False
        
        # PRIORITY 1: Check by image hash first (most reliable)
        if product.image:
            image_hash = get_image_hash(product.image)
            if image_hash:
                if image_hash in seen_hashes:
                    # This is a duplicate by hash - same image file
                    is_duplicate = True
                else:
                    seen_hashes[image_hash] = product
            
            # PRIORITY 2: Check by image filename (if hash check didn't find duplicate)
            if not is_duplicate:
                filename = get_image_filename(product.image)
                if filename:
                    base_name = os.path.splitext(filename)[0].lower()
                    if base_name in seen_images:
                        # This is a duplicate by filename
                        is_duplicate = True
                    else:
                        seen_images[base_name] = product
        
        # PRIORITY 3: Check by name + category if not already marked as duplicate
        if not is_duplicate:
            key = f"{product.name.lower().strip()}_{product.category.id if product.category else 'none'}"
            if key in seen_name_category:
                # Check if they're actually duplicates (same category and same name)
                existing = seen_name_category[key]
                # Only consider duplicate if they have the same category
                if product.category == existing.category:
                    is_duplicate = True
                else:
                    seen_name_category[key] = product
            else:
                seen_name_category[key] = product
        
        # Only add if not a duplicate
        if not is_duplicate:
            unique_products.append(product)
            seen_product_ids.add(product.id)
    
    return unique_products


def ensure_no_duplicates(product):
    """
    Check if a product is a duplicate before saving
    Returns (is_duplicate, existing_product) tuple
    """
    if product.product_type != 'service':
        return (False, None)
    
    # Check by image if image exists
    if product.image:
        filename = get_image_filename(product.image)
        if filename:
            base_name = os.path.splitext(filename)[0].lower()
            existing = Product.objects.filter(
                product_type='service',
                is_archived=False,
                image__isnull=False
            ).exclude(image='').exclude(id=product.id if product.id else None)
            
            for existing_product in existing:
                if existing_product.image:
                    existing_filename = get_image_filename(existing_product.image)
                    if existing_filename:
                        existing_base_name = os.path.splitext(existing_filename)[0].lower()
                        if base_name == existing_base_name:
                            return (True, existing_product)
        
        # Check by image hash
        image_hash = get_image_hash(product.image)
        if image_hash:
            existing = Product.objects.filter(
                product_type='service',
                is_archived=False,
                image__isnull=False
            ).exclude(image='').exclude(id=product.id if product.id else None)
            
            for existing_product in existing:
                if existing_product.image:
                    existing_hash = get_image_hash(existing_product.image)
                    if existing_hash and image_hash == existing_hash:
                        return (True, existing_product)
    
    # Check by name + category
    existing = Product.objects.filter(
        product_type='service',
        is_archived=False,
        name__iexact=product.name,
        category=product.category if product.category else None
    ).exclude(id=product.id if product.id else None).first()
    
    if existing:
        return (True, existing)
    
    return (False, None)

