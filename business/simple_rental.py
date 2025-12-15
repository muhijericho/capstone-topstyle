from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
from .models import Order, Customer, Product, OrderItem, Category

@login_required
def create_rental_order_simple(request):
    """
    SIMPLE DIRECT APPROACH: Create rental order using ACTUAL rental products
    This function will definitely work!
    """
    if request.method == 'POST':
        try:
            data = request.POST
            
            print(f"[SIMPLE_RENTAL] Creating rental order with data: {data}")
            
            # Get customer info
            customer_name = data.get('customer_name', 'Unknown Customer')
            customer_phone = data.get('customer_phone', '')
            
            # Create or get customer
            customer, created = Customer.objects.get_or_create(
                phone=customer_phone,
                defaults={
                    'name': customer_name,
                    'email': '',
                    'address': ''
                }
            )
            print(f"[SIMPLE_RENTAL] Customer: {customer.name} (ID: {customer.id})")
            
            # Get selected rental products from the brochure
            selected_products = data.getlist('selected_products[]')
            print(f"[SIMPLE_RENTAL] Selected products: {selected_products}")
            
            if not selected_products:
                return JsonResponse({
                    'success': False,
                    'error': 'No rental products selected'
                })
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                order_type='rent',
                status='pending',
                total_amount=Decimal('0'),
                balance=Decimal('0'),
                notes=f'Rental order for {customer_name}'
            )
            
            print(f"[SIMPLE_RENTAL] Created order: {order.order_identifier}")
            
            total_cost = Decimal('0')
            rented_products = []
            
            # Process each selected product
            for product_name in selected_products:
                try:
                    # Find the ACTUAL rental product
                    product = Product.objects.get(name=product_name, product_type='rental')
                    print(f"[SIMPLE_RENTAL] Found rental product: {product.name} (ID: {product.id})")
                    
                    # Get quantity (default to 1)
                    quantity = int(data.get(f'quantity_{product_name}', 1))
                    unit_price = product.price
                    total_price = unit_price * quantity
                    
                    # Create order item
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )
                    
                    print(f"[SIMPLE_RENTAL] Created order item: {order_item.id}")
                    
                    # MARK PRODUCT AS RENTED IMMEDIATELY
                    product.rental_status = 'rented'
                    product.current_rental_order = order
                    product.rental_start_date = timezone.now()
                    product.rental_due_date = timezone.now() + timezone.timedelta(days=3)
                    product.save()
                    
                    print(f"[SIMPLE_RENTAL] SUCCESS: Product {product.name} marked as RENTED")
                    rented_products.append(product.name)
                    
                    total_cost += total_price
                    
                except Product.DoesNotExist:
                    print(f"[SIMPLE_RENTAL] ERROR: Rental product '{product_name}' not found!")
                    return JsonResponse({
                        'success': False,
                        'error': f'Rental product "{product_name}" not found in inventory'
                    })
            
            # Update order totals
            order.total_amount = total_cost
            order.balance = total_cost
            order.save()
            
            print(f"[SIMPLE_RENTAL] Order completed! Total: {total_cost}")
            print(f"[SIMPLE_RENTAL] Rented products: {rented_products}")
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'order_identifier': order.order_identifier,
                'total_cost': float(total_cost),
                'rented_products': rented_products,
                'message': f'Rental order created successfully! {len(rented_products)} products marked as rented.'
            })
            
        except Exception as e:
            print(f"[SIMPLE_RENTAL] ERROR: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })




















































