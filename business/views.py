from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import json
import qrcode
import io
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from openpyxl import Workbook
from .models import *
from .forms import *


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'business/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    # Get real-time statistics using database connection functions
    inventory_status = get_inventory_status()
    sales_data = calculate_actual_sales()
    
    # Get order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='completed').count()
    in_progress_orders = Order.objects.filter(status='in_progress').count()
    total_products = inventory_status['total_products']
    low_stock_products = inventory_status['low_stock']
    
    # Sales data for the last 30 days (only completed orders)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_sales = Sales.objects.filter(
        created_at__gte=thirty_days_ago,
        order__status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Monthly sales data for chart (only completed orders)
    monthly_sales = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        month_sales = Sales.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end,
            order__status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_sales.append({
            'month': month_start.strftime('%b'),
            'amount': float(month_sales)
        })
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    # Low stock products
    low_stock = Product.objects.filter(quantity__lte=models.F('min_quantity'))[:5]
    
    # Rental status data
    rental_available = inventory_status['rental_available']
    rental_rented = inventory_status['rental_rented']
    rental_overdue = inventory_status['rental_overdue']
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'in_progress_orders': in_progress_orders,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': inventory_status['out_of_stock'],
        'recent_sales': recent_sales,
        'monthly_sales': json.dumps(monthly_sales),
        'recent_orders': recent_orders,
        'low_stock': low_stock,
        'rental_available': rental_available,
        'rental_rented': rental_rented,
        'rental_overdue': rental_overdue,
        'inventory_status': inventory_status,
        'sales_data': sales_data,
    }
    
    return render(request, 'business/dashboard.html', context)


@login_required
def orders_list(request):
    """Orders list with real-time database connections and comprehensive tracking"""
    # Get filter parameter
    order_type_filter = request.GET.get('type', 'all')
    
    # Base queryset with related data for better performance
    orders = Order.objects.select_related('customer').prefetch_related('items__product').order_by('-created_at')
    
    # Apply filter if specified
    if order_type_filter != 'all':
        orders = orders.filter(order_type=order_type_filter)
    
    # Calculate statistics for pie chart
    completed_orders = orders.filter(status='completed').count()
    pending_orders = orders.filter(status='pending').count()
    in_progress_orders = orders.filter(status='in_progress').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    # Calculate revenue statistics
    from django.db.models import Sum
    from datetime import datetime, timedelta
    
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Monthly revenue (current month)
    current_month = datetime.now().replace(day=1)
    monthly_revenue = orders.filter(
        created_at__gte=current_month
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Daily revenue (today)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    daily_revenue = orders.filter(
        created_at__gte=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Weekly revenue (this week - Monday to Sunday)
    today = datetime.now().date()
    days_since_monday = today.weekday()  # Monday is 0, Sunday is 6
    start_of_week = today - timedelta(days=days_since_monday)
    start_of_week_datetime = datetime.combine(start_of_week, datetime.min.time())
    weekly_revenue = orders.filter(
        created_at__gte=start_of_week_datetime
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Yearly revenue (current year)
    current_year = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    yearly_revenue = orders.filter(
        created_at__gte=current_year
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate order type statistics
    rental_orders = Order.objects.filter(order_type='rental').count()
    repair_orders = Order.objects.filter(order_type='repair').count()
    customize_orders = Order.objects.filter(order_type='customize').count()
    
    # Get inventory status for order-related products
    inventory_status = get_inventory_status()
    
    # Get orders with inventory issues
    orders_with_issues = []
    for order in orders[:10]:  # Check first 10 orders for performance
        for item in order.items.all():
            if item.product.is_low_stock or (item.product.product_type == 'rental' and item.product.is_overdue):
                orders_with_issues.append({
                    'order': order,
                    'issue': 'Low stock' if item.product.is_low_stock else 'Overdue rental',
                    'product': item.product
                })
    
    # Get recent activity from activity log
    recent_activities = ActivityLog.objects.filter(
        activity_type__in=['order_created', 'order_updated', 'order_completed']
    ).order_by('-created_at')[:5]
    
    context = {
        'orders': orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'in_progress_orders': in_progress_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'yearly_revenue': yearly_revenue,
        'monthly_revenue': monthly_revenue,
        'weekly_revenue': weekly_revenue,
        'daily_revenue': daily_revenue,
        'rental_orders': rental_orders,
        'repair_orders': repair_orders,
        'customize_orders': customize_orders,
        'current_filter': order_type_filter,
        'inventory_status': inventory_status,
        'orders_with_issues': orders_with_issues,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'business/orders.html', context)


@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            return redirect('order_items', order_id=order.id)
    else:
        form = OrderForm()
    
    return render(request, 'business/create_order.html', {'form': form})


@login_required
def payment_method(request):
    return render(request, 'business/payment_method.html')

@login_required
def payment_process(request):
    """View for payment processing (like grocery store POS)"""
    return render(request, 'business/payment_process.html')

@login_required
def track_order_qr(request):
    """View for tracking order via QR code scan"""
    if request.method == 'POST':
        try:
            import json
            qr_data = json.loads(request.body)
            
            # Extract order ID from QR data
            order_id = qr_data.get('orderId')
            
            if order_id:
                # Use database connection function to get comprehensive tracking data
                tracking_data = get_order_tracking_data(order_id)
                if tracking_data:
                    context = {
                        'tracking_data': tracking_data,
                        'qr_data': qr_data, 
                        'found': True,
                        'order': tracking_data['order'],
                        'customer': tracking_data['customer'],
                        'items': tracking_data['items'],
                        'inventory_status': tracking_data['inventory_status'],
                        'sales_info': tracking_data['sales_info']
                    }
                else:
                    # Order not found in database, show QR data only
                    context = {
                        'qr_data': qr_data,
                        'found': False,
                        'order_id': order_id
                    }
            else:
                context = {
                    'error': 'Invalid QR code data',
                    'found': False
                }
                
        except json.JSONDecodeError:
            context = {
                'error': 'Invalid QR code format',
                'found': False
            }
        except Exception as e:
            context = {
                'error': f'Error processing QR code: {str(e)}',
                'found': False
            }
    else:
        context = {
            'error': 'No QR code data provided',
            'found': False
        }
    
    return render(request, 'business/track_order.html', context)

@login_required
def activity_log(request):
    """View to display system activity log"""
    activities = ActivityLog.objects.all()[:100]  # Show last 100 activities
    
    # Filter by activity type if provided
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    # Filter by date range if provided
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        activities = activities.filter(created_at__date__gte=date_from)
    if date_to:
        activities = activities.filter(created_at__date__lte=date_to)
    
    context = {
        'activities': activities,
        'activity_types': ActivityLog.ACTIVITY_TYPES,
        'selected_type': activity_type,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'business/activity_log.html', context)


# ==================== DATABASE CONNECTION FUNCTIONS ====================

def check_inventory_availability(products_data, order_type):
    """Check if all required products are available in inventory"""
    unavailable_items = []
    
    for product_data in products_data:
        product_name = product_data.get('name', '')
        product_type = product_data.get('type', 'material')
        quantity_needed = product_data.get('quantity', 1)
        
        try:
            product = Product.objects.get(name=product_name, product_type=product_type)
            
            if order_type == 'rental':
                # For rental orders, check if product is available for rental
                if not product.is_available or product.rental_status != 'available':
                    unavailable_items.append({
                        'name': product_name,
                        'reason': 'Not available for rental',
                        'current_status': product.rental_status
                    })
            else:
                # For repair/customize orders, check quantity
                if product.quantity < quantity_needed:
                    unavailable_items.append({
                        'name': product_name,
                        'reason': f'Insufficient quantity (needed: {quantity_needed}, available: {product.quantity})',
                        'available': product.quantity,
                        'needed': quantity_needed
                    })
                    
        except Product.DoesNotExist:
            # Product doesn't exist, will be created
            pass
    
    return {
        'available': len(unavailable_items) == 0,
        'unavailable_items': unavailable_items
    }


def update_inventory_for_order(product, quantity, order, order_type):
    """Update inventory based on order type and create transaction record"""
    from datetime import timedelta
    
    # Ensure quantity is an integer
    quantity = int(quantity) if quantity else 0
    
    if order_type == 'rental':
        # For rental orders, mark as rented
        product.rental_status = 'rented'
        product.current_rental_order = order
        product.rental_start_date = timezone.now()
        product.rental_due_date = timezone.now() + timedelta(days=3)
        
        # Create inventory transaction
        InventoryTransaction.objects.create(
            product=product,
            transaction_type='rental_out',
            quantity=1,  # Rental is always 1 item
            reference_order=order,
            notes=f'Rented out for order {order.order_identifier}',
            created_by=order.created_by
        )
        
    else:
        # For repair/customize orders, deduct from inventory
        if product.quantity >= quantity:
            product.quantity -= quantity
            
            # Create inventory transaction
            InventoryTransaction.objects.create(
                product=product,
                transaction_type='out',
                quantity=-quantity,  # Negative for stock out
                reference_order=order,
                notes=f'Used for {order_type} order {order.order_identifier}',
                created_by=order.created_by
            )
    
    product.save()


def update_dashboard_statistics():
    """Update dashboard statistics in real-time"""
    # This function can be called to refresh dashboard data
    # Statistics are calculated in real-time in the dashboard view
    pass


def calculate_actual_sales():
    """Calculate actual sales from completed orders"""
    from decimal import Decimal
    
    # Get all completed orders
    completed_orders = Order.objects.filter(status='completed')
    
    total_sales = Decimal('0')
    sales_count = 0
    
    for order in completed_orders:
        # Check if sales record exists
        sales, created = Sales.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total_amount,
                'payment_method': 'cash'  # Default payment method
            }
        )
        
        if created:
            total_sales += order.total_amount
            sales_count += 1
    
    return {
        'total_sales': total_sales,
        'sales_count': sales_count,
        'new_sales_created': sales_count
    }


def get_inventory_status():
    """Get real-time inventory status for all products"""
    products = Product.objects.filter(is_active=True, is_archived=False)
    
    inventory_status = {
        'total_products': products.count(),
        'low_stock': 0,
        'out_of_stock': 0,
        'rental_available': 0,
        'rental_rented': 0,
        'rental_overdue': 0,
        'products': []
    }
    
    for product in products:
        product_status = {
            'id': product.id,
            'name': product.name,
            'type': product.product_type,
            'quantity': product.quantity,
            'price': float(product.price),
            'is_available': product.is_available,
            'is_low_stock': product.is_low_stock,
            'rental_status': product.rental_status if product.product_type == 'rental' else None,
            'is_overdue': product.is_overdue if product.product_type == 'rental' else False
        }
        
        inventory_status['products'].append(product_status)
        
        # Update counters
        if product.is_low_stock:
            inventory_status['low_stock'] += 1
        if product.quantity == 0:
            inventory_status['out_of_stock'] += 1
        if product.product_type == 'rental':
            if product.rental_status == 'available':
                inventory_status['rental_available'] += 1
            elif product.rental_status == 'rented':
                inventory_status['rental_rented'] += 1
                if product.is_overdue:
                    inventory_status['rental_overdue'] += 1
    
    return inventory_status


def get_order_tracking_data(order_identifier):
    """Get comprehensive order tracking data"""
    try:
        order = Order.objects.get(order_identifier=order_identifier)
        
        tracking_data = {
            'order': {
                'id': order.id,
                'identifier': order.order_identifier,
                'type': order.get_order_type_display(),
                'status': order.get_status_display(),
                'total_amount': float(order.total_amount),
                'paid_amount': float(order.paid_amount),
                'balance': float(order.balance),
                'created_at': order.created_at,
                'due_date': order.due_date,
                'notes': order.notes
            },
            'customer': {
                'name': order.customer.name,
                'phone': order.customer.phone,
                'email': order.customer.email,
                'address': order.customer.address
            },
            'items': [],
            'inventory_status': [],
            'sales_info': None
        }
        
        # Get order items
        for item in order.items.all():
            tracking_data['items'].append({
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price)
            })
            
            # Get inventory status for each product
            product_status = {
                'product_name': item.product.name,
                'current_quantity': item.product.quantity,
                'is_available': item.product.is_available,
                'rental_status': item.product.rental_status if item.product.product_type == 'rental' else None,
                'is_overdue': item.product.is_overdue if item.product.product_type == 'rental' else False
            }
            tracking_data['inventory_status'].append(product_status)
        
        # Get sales information if exists
        try:
            sales = Sales.objects.get(order=order)
            tracking_data['sales_info'] = {
                'sales_identifier': sales.sales_identifier,
                'amount': float(sales.amount),
                'payment_method': sales.payment_method,
                'created_at': sales.created_at
            }
        except Sales.DoesNotExist:
            pass
        
        return tracking_data
        
    except Order.DoesNotExist:
        return None


@login_required
def api_inventory_status(request):
    """API endpoint to get real-time inventory status"""
    if request.method == 'GET':
        inventory_status = get_inventory_status()
        return JsonResponse(inventory_status)
    
    return JsonResponse({'error': 'Invalid request method'})


@login_required
def api_sales_calculation(request):
    """API endpoint to calculate and update sales"""
    if request.method == 'POST':
        sales_data = calculate_actual_sales()
        return JsonResponse(sales_data)
    
    return JsonResponse({'error': 'Invalid request method'})


@login_required
def api_order_tracking(request):
    """API endpoint for order tracking"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_identifier = data.get('order_identifier')
            
            if order_identifier:
                tracking_data = get_order_tracking_data(order_identifier)
                if tracking_data:
                    return JsonResponse({
                        'success': True,
                        'data': tracking_data
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Order not found'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Order identifier required'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
    
    return JsonResponse({'error': 'Invalid request method'})


@login_required
def order_receipt_new(request):
    return render(request, 'business/order_receipt_new.html')


@login_required
def create_order_from_session(request):
    if request.method == 'POST':
        try:
            import json
            from decimal import Decimal
            from django.utils import timezone
            
            # Get order data from request
            order_data = json.loads(request.body)
            
            # Create customer
            customer, created = Customer.objects.get_or_create(
                phone=order_data['mobileNumber'],
                defaults={
                    'name': order_data['customerName'],
                    'email': f"{order_data['customerName'].lower().replace(' ', '')}@example.com"
                }
            )
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                order_type=order_data['orderType'],
                status='pending',
                total_amount=Decimal(str(order_data['totalCost'])),
                paid_amount=Decimal(str(order_data['totalCost'])),
                balance=Decimal('0'),
                created_by=request.user
            )
            
            # Generate unique identifier
            order.generate_order_identifier()
            order.save()
            
            # Create order items
            for item in order_data['items']:
                # Get the product name and class from the item
                product_name = item.get('name', f"{order_data['orderType']} Service")
                item_class = item.get('class', 'standard')
                
                # For rental orders, find existing rental products
                if order_data['orderType'] == 'rental':
                    # Try to find an available rental product
                    product = Product.objects.filter(
                        product_type='rental',
                        name__icontains=product_name,
                        rental_status='available',
                        is_active=True
                    ).first()
                    
                    if not product:
                        # Create a new rental product if none available
                        product, created = Product.objects.get_or_create(
                            name=f"Rental - {product_name} (Class {item_class})",
                            defaults={
                                'category': Category.objects.first(),
                                'product_type': 'rental',
                                'price': Decimal(str(item['cost'])),
                                'quantity': 1,
                                'description': f"Rental service: {product_name} - Class {item_class}",
                                'rental_status': 'available'
                            }
                        )
                    
                    # Check if product is available for rental
                    if not product.is_available:
                        return JsonResponse({
                            'success': False, 
                            'error': f'Product {product.name} is not available for rental'
                        })
                    
                    # Update product rental status
                    product.rental_status = 'rented'
                    product.current_rental_order = order
                    product.rental_start_date = timezone.now()
                    # Set due date (3 days from now for rental)
                    product.rental_due_date = timezone.now() + timezone.timedelta(days=3)
                    product.save()
                    
                else:
                    # For repair/customize orders, find or create material/service products
                    product, created = Product.objects.get_or_create(
                        name=f"{order_data['orderType']} - {product_name} (Class {item_class})",
                        defaults={
                            'category': Category.objects.first(),
                            'product_type': 'material' if order_data['orderType'] == 'repair' else 'service',
                            'price': Decimal(str(item['cost'])),
                            'quantity': 100,
                            'description': f"{order_data['orderType']} service: {product_name} - Class {item_class}"
                        }
                    )
                    
                    # Check availability for materials
                    item_quantity = int(item['quantity'])
                    if product.product_type == 'material' and product.quantity < item_quantity:
                        return JsonResponse({
                            'success': False, 
                            'error': f'Insufficient quantity for {product.name}. Available: {product.quantity}'
                        })
                    
                    # Update material quantity
                    if product.product_type == 'material':
                        product.quantity -= item_quantity
                        product.save()
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=int(item['quantity']),
                    unit_price=Decimal(str(item['cost'])),
                    total_price=Decimal(str(item['cost']))
                )
            
            # Note: Sales record will be created automatically when order status changes to 'completed'
            
            # Generate QR code
            qr_data = {
                'order_id': order.id,
                'customer_name': customer.name,
                'total_amount': str(order.total_amount),
                'order_type': order.order_type,
                'date': order.created_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'order_identifier': order.order_identifier,
                'message': 'Order created successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def order_items(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        
        # Check availability
        if product.product_type == 'rental':
            if product.quantity < quantity:
                messages.error(request, f'Only {product.quantity} {product.name} available for rent.')
                return redirect('order_items', order_id=order_id)
        else:
            if product.quantity < quantity:
                messages.error(request, f'Only {product.quantity} {product.name} available in stock.')
                return redirect('order_items', order_id=order_id)
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price
        )
        
        # Update inventory
        if product.product_type == 'rental':
            InventoryTransaction.objects.create(
                product=product,
                transaction_type='rental_out',
                quantity=-quantity,
                reference_order=order,
                notes=f'Rental order {order.order_id}',
                created_by=request.user
            )
        else:
            InventoryTransaction.objects.create(
                product=product,
                transaction_type='out',
                quantity=-quantity,
                reference_order=order,
                notes=f'Order {order.order_id}',
                created_by=request.user
            )
        
        # Update product quantity
        product.quantity -= quantity
        product.save()
        
        # Update order total
        from decimal import Decimal
        total = order.items.aggregate(total=Sum('total_price'))['total'] or 0
        order.total_amount = Decimal(str(total))
        order.save()
        
        messages.success(request, f'{product.name} added to order.')
        return redirect('order_items', order_id=order_id)
    
    products = Product.objects.filter(is_active=True)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'products': products,
        'order_items': order_items,
    }
    
    return render(request, 'business/order_items.html', context)


@login_required
def order_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        from decimal import Decimal
        paid_amount = Decimal(str(request.POST.get('paid_amount', 0)))
        order.paid_amount = paid_amount
        order.status = 'confirmed'
        order.save()
        
        # Create or update sales record
        sales_record, created = Sales.objects.get_or_create(
            order=order,
            defaults={
                'amount': paid_amount,
                'payment_method': request.POST.get('payment_method', 'cash')
            }
        )
        
        # If sales record already exists, update it
        if not created:
            sales_record.amount = paid_amount
            sales_record.payment_method = request.POST.get('payment_method', 'cash')
            sales_record.save()
        
        # Generate QR code
        generate_qr_code(order)
        
        # Send SMS notification
        send_sms_notification(order)
        
        messages.success(request, 'Order confirmed and payment recorded.')
        return redirect('order_receipt', order_id=order.id)
    
    return render(request, 'business/order_payment.html', {'order': order})


@login_required
def order_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    qr_code = QRCode.objects.filter(order=order).first()
    
    return render(request, 'business/order_receipt.html', {
        'order': order,
        'qr_code': qr_code
    })


@login_required
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Update order status to completed
        order.status = 'completed'
        order.save()
        
        messages.success(request, f'Order {order.order_identifier} has been marked as completed.')
        return redirect('orders')
    
    return render(request, 'business/complete_order.html', {'order': order})


@login_required
def inventory_list(request):
    """Inventory list with real-time database connections and status tracking"""
    # Get filter parameter
    product_type_filter = request.GET.get('type', 'all')
    
    # Get real-time inventory status
    inventory_status = get_inventory_status()
    
    # Base queryset with real-time status
    products = Product.objects.filter(is_archived=False).order_by('name')
    
    # Apply filter if specified
    if product_type_filter != 'all':
        products = products.filter(product_type=product_type_filter)
    
    # Calculate product type statistics from real-time data
    rental_products = inventory_status['rental_available'] + inventory_status['rental_rented']
    material_products = inventory_status['total_products'] - rental_products
    total_products = inventory_status['total_products']
    
    # Get low stock and out of stock products
    low_stock_products = Product.objects.filter(
        is_archived=False,
        quantity__lte=models.F('min_quantity')
    ).order_by('quantity')
    
    out_of_stock_products = Product.objects.filter(
        is_archived=False,
        quantity=0
    ).order_by('name')
    
    # Get overdue rental products
    overdue_rentals = Product.objects.filter(
        is_archived=False,
        product_type='rental',
        rental_status='rented',
        rental_due_date__lt=timezone.now()
    ).order_by('rental_due_date')
    
    context = {
        'products': products,
        'rental_products': rental_products,
        'material_products': material_products,
        'total_products': total_products,
        'current_filter': product_type_filter,
        'inventory_status': inventory_status,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'overdue_rentals': overdue_rentals,
        'low_stock_count': inventory_status['low_stock'],
        'out_of_stock_count': inventory_status['out_of_stock'],
        'rental_available': inventory_status['rental_available'],
        'rental_rented': inventory_status['rental_rented'],
        'rental_overdue': inventory_status['rental_overdue'],
    }
    
    return render(request, 'business/inventory.html', context)


@login_required
def archive_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.is_archived = True
        product.is_active = False  # Also deactivate the product
        product.save()
        messages.success(request, f'{product.name} has been archived successfully.')
    return redirect('inventory')


@login_required
def return_rental_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        if product.rental_status == 'rented':
            # Return the product
            product.rental_status = 'available'
            product.current_rental_order = None
            product.rental_start_date = None
            product.rental_due_date = None
            product.save()
            
            messages.success(request, f'{product.name} has been returned successfully.')
        else:
            messages.error(request, f'{product.name} is not currently rented.')
    return redirect('inventory')


@login_required
def send_overdue_notification(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        if product.is_overdue and product.current_rental_order:
            # Send SMS notification
            customer = product.current_rental_order.customer
            message = f"Hello {customer.name}, your rental item '{product.name}' is overdue. Please return it as soon as possible. Due date: {product.rental_due_date.strftime('%Y-%m-%d')}"
            
            # Here you would integrate with your SMS service
            # For now, we'll just show a success message
            messages.success(request, f'Overdue notification sent to {customer.name} for {product.name}')
        else:
            messages.error(request, f'{product.name} is not overdue.')
    return redirect('inventory')


@login_required
def rental_management(request):
    """View to manage all rental items and their status"""
    # Get all rental products
    rental_products = Product.objects.filter(
        product_type='rental',
        is_archived=False
    ).order_by('rental_status', 'name')
    
    # Calculate statistics
    available_rentals = rental_products.filter(rental_status='available').count()
    rented_items = rental_products.filter(rental_status='rented').count()
    overdue_items = rental_products.filter(
        rental_status='rented',
        rental_due_date__lt=timezone.now()
    ).count()
    maintenance_items = rental_products.filter(rental_status='maintenance').count()
    
    context = {
        'rental_products': rental_products,
        'available_rentals': available_rentals,
        'rented_items': rented_items,
        'overdue_items': overdue_items,
        'maintenance_items': maintenance_items,
    }
    
    return render(request, 'business/rental_management.html', context)


@login_required
def add_product_from_estimator(request):
    """API endpoint to add product to inventory from estimator"""
    if request.method == 'POST':
        try:
            import json
            from decimal import Decimal
            
            data = json.loads(request.body)
            
            # Get or create category
            category, created = Category.objects.get_or_create(
                name=data.get('category', 'General'),
                defaults={'description': f'Category for {data.get("category", "General")} products'}
            )
            
            # Create product
            product = Product.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                category=category,
                product_type=data['product_type'],
                price=Decimal(str(data['price'])),
                cost=Decimal(str(data.get('cost', 0))),
                quantity=data.get('quantity', 1),
                min_quantity=data.get('min_quantity', 0),
                is_active=True,
                is_archived=False
            )
            
            return JsonResponse({
                'success': True,
                'product_id': product.id,
                'message': f'Product "{product.name}" added to inventory successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def create_order_from_estimator(request):
    """API endpoint to create order from estimator"""
    if request.method == 'POST':
        try:
            import json
            from decimal import Decimal
            from django.utils import timezone
            
            data = json.loads(request.body)
            
            # Create or get customer
            customer, created = Customer.objects.get_or_create(
                phone=data.get('mobile_number', '00000000000'),
                defaults={
                    'name': data['customer_name'],
                    'email': f"{data['customer_name'].lower().replace(' ', '')}@example.com"
                }
            )
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                order_type=data['service_type'],
                status='pending',
                total_amount=Decimal(str(data['total_cost'])),
                paid_amount=Decimal('0'),
                balance=Decimal(str(data['total_cost'])),
                created_by=request.user
            )
            
            # Generate unique identifier
            order.generate_order_identifier()
            order.save()
            
            # Create order item based on service type
            if data['service_type'] == 'rent':
                # For rental, create a rental product if it doesn't exist
                product, created = Product.objects.get_or_create(
                    name=f"Rental - {data['rent_type'].title()}",
                    defaults={
                        'category': Category.objects.first(),
                        'product_type': 'rental',
                        'price': Decimal(str(data['total_cost'])),
                        'quantity': 1,
                        'description': f"Rental item: {data['rent_type']}",
                        'rental_status': 'available'
                    }
                )
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=int(data.get('rent_quantity', 1)),
                    unit_price=Decimal(str(data['total_cost'])),
                    total_price=Decimal(str(data['total_cost']))
                )
                
            elif data['service_type'] == 'repair':
                # For repair, create a service product
                product, created = Product.objects.get_or_create(
                    name=f"Repair - {data['repair_type'].replace('_', ' ').title()}",
                    defaults={
                        'category': Category.objects.first(),
                        'product_type': 'service',
                        'price': Decimal(str(data['total_cost'])),
                        'quantity': 1,
                        'description': f"Repair service: {data['repair_type']}"
                    }
                )
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1,
                    unit_price=Decimal(str(data['total_cost'])),
                    total_price=Decimal(str(data['total_cost']))
                )
                
            elif data['service_type'] == 'customize':
                # For customize, create a service product
                product, created = Product.objects.get_or_create(
                    name=f"Customize - {data['customize_type'].replace('_', ' ').title()}",
                    defaults={
                        'category': Category.objects.first(),
                        'product_type': 'service',
                        'price': Decimal(str(data['total_cost'])),
                        'quantity': 1,
                        'description': f"Customization service: {data['customize_type']}"
                    }
                )
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1,
                    unit_price=Decimal(str(data['total_cost'])),
                    total_price=Decimal(str(data['total_cost']))
                )
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'order_identifier': order.order_identifier,
                'message': f'Order {order.order_identifier} created successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'{product.name} added to inventory.')
            return redirect('inventory')
    else:
        form = ProductForm()
    
    return render(request, 'business/add_product.html', {'form': form})


@login_required
def sales_page(request):
    """Sales page with real-time database connections and automatic calculations"""
    # Use database connection function to calculate actual sales
    sales_calculation = calculate_actual_sales()
    
    # Only show sales from completed orders
    completed_sales = Sales.objects.filter(order__status='completed')
    
    # Sales statistics with real-time data
    total_sales = completed_sales.aggregate(total=Sum('amount'))['total'] or 0
    monthly_sales = completed_sales.filter(
        created_at__gte=timezone.now().replace(day=1)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Sales by payment method
    sales_by_method = completed_sales.values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Recent sales with order details
    recent_sales = completed_sales.select_related('order__customer').order_by('-created_at')[:10]
    
    # Calculate average sale
    from decimal import Decimal
    average_sale = Decimal('0')
    if recent_sales:
        total_recent_sales = sum(sale.amount for sale in recent_sales)
        average_sale = total_recent_sales / len(recent_sales)
    
    # Get sales trends (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    daily_sales = completed_sales.filter(
        created_at__gte=seven_days_ago
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        daily_total=Sum('amount')
    ).order_by('day')
    
    # Get top selling products/services
    top_products = OrderItem.objects.filter(
        order__status='completed'
    ).values('product__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_revenue')[:5]
    
    context = {
        'total_sales': total_sales,
        'monthly_sales': monthly_sales,
        'sales_by_method': sales_by_method,
        'recent_sales': recent_sales,
        'average_sale': average_sale,
        'daily_sales': list(daily_sales),
        'top_products': top_products,
        'sales_calculation': sales_calculation,
        'new_sales_created': sales_calculation['new_sales_created'],
    }
    
    return render(request, 'business/sales.html', context)


@login_required
def track_order(request):
    """Enhanced track order view with QR code support and better error handling"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id', '').strip()
        
        if not order_id:
            messages.error(request, 'Please enter an Order ID')
            return render(request, 'business/track_order.html')
        
        try:
            # Try to find by order_identifier field first (custom identifiers like TS03-04)
            order = Order.objects.get(order_identifier=order_id)
        except Order.DoesNotExist:
            try:
                # Try to find order by order_id field (UUID)
                order = Order.objects.get(order_id=order_id)
            except (Order.DoesNotExist, ValidationError):
                try:
                    # Try to find by ID if it's a number
                    if order_id.isdigit():
                        order = Order.objects.get(id=int(order_id))
                    else:
                        raise Order.DoesNotExist
                except (Order.DoesNotExist, ValueError):
                    messages.error(request, f'Order "{order_id}" not found. Please check your Order ID and try again.')
                    return render(request, 'business/track_order.html')
        
        # Add to recent searches (you could implement this with a model)
        return render(request, 'business/track_result.html', {
            'order': order, 
            'found': True,
            'order_id': order_id
        })
    
    return render(request, 'business/track_order.html')

@login_required
def track_result(request):
    """Display track order result"""
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(order_id=order_id)
            return render(request, 'business/track_result.html', {'order': order, 'found': True})
        except Order.DoesNotExist:
            return render(request, 'business/track_result.html', {'found': False, 'order_id': order_id})
    
    return render(request, 'business/track_result.html', {'found': False})


def generate_qr_code(order):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"Order ID: {order.order_id}")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to file
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    qr_code_obj, created = QRCode.objects.get_or_create(order=order)
    qr_code_obj.qr_code_image.save(
        f'qr_{order.order_id}.png',
        ContentFile(buffer.getvalue()),
        save=True
    )


def send_sms_notification(order):
    # This is a placeholder for SMS functionality
    # In a real implementation, you would integrate with an SMS service
    SMSNotification.objects.create(
        order=order,
        phone_number=order.customer.phone,
        message=f"Your order {order.order_id} has been confirmed. Total: ₱{order.total_amount}",
        status='sent'
    )


@login_required
def generate_pdf_report(request, report_type):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, f"{report_type.title()} Report")
    p.drawString(100, 730, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    
    if report_type == 'sales':
        sales = Sales.objects.all()
        y = 700
        for sale in sales:
            p.drawString(100, y, f"Order: {sale.order.order_id} - Amount: ₱{sale.amount}")
            y -= 20
    
    p.showPage()
    p.save()
    return response


@login_required
def generate_excel_report(request, report_type):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"{report_type.title()} Report"
    
    if report_type == 'sales':
        ws['A1'] = 'Order ID'
        ws['B1'] = 'Customer'
        ws['C1'] = 'Amount'
        ws['D1'] = 'Date'
        
        row = 2
        for sale in Sales.objects.all():
            ws[f'A{row}'] = str(sale.order.order_id)
            ws[f'B{row}'] = sale.order.customer.name
            ws[f'C{row}'] = float(sale.amount)
            ws[f'D{row}'] = sale.created_at.strftime('%Y-%m-%d')
            row += 1
    
    wb.save(response)
    return response


# ==================== CUSTOMER MANAGEMENT VIEWS ====================

@login_required
def customer_list(request):
    """Customer list with search and filtering"""
    search_query = request.GET.get('search', '')
    customers = Customer.objects.all()
    
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Get customer statistics
    total_customers = customers.count()
    customers_with_orders = customers.filter(order__isnull=False).distinct().count()
    customers_without_orders = total_customers - customers_with_orders
    
    # Recent customers (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_customers = customers.filter(created_at__gte=thirty_days_ago).count()
    
    context = {
        'customers': customers.order_by('-created_at'),
        'search_query': search_query,
        'total_customers': total_customers,
        'customers_with_orders': customers_with_orders,
        'customers_without_orders': customers_without_orders,
        'recent_customers': recent_customers,
    }
    
    return render(request, 'business/customer_list.html', context)


@login_required
def add_customer(request):
    """Add new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" added successfully.')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'business/add_customer.html', {'form': form})


@login_required
def edit_customer(request, customer_id):
    """Edit existing customer"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" updated successfully.')
            return redirect('customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'business/edit_customer.html', {'form': form, 'customer': customer})


@login_required
def delete_customer(request, customer_id):
    """Delete customer"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        customer_name = customer.name
        customer.delete()
        messages.success(request, f'Customer "{customer_name}" deleted successfully.')
        return redirect('customer_list')
    
    return render(request, 'business/delete_customer.html', {'customer': customer})


@login_required
def customer_detail(request, customer_id):
    """Customer detail view with order history and loyalty status"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Get customer's orders
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    # Calculate customer statistics
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    completed_orders = orders.filter(status='completed').count()
    pending_orders = orders.filter(status='pending').count()
    
    # Check for loyalty customer status (10+ orders in last 2 months)
    two_months_ago = timezone.now() - timedelta(days=60)
    recent_orders_count = orders.filter(
        created_at__gte=two_months_ago,
        status='completed'
    ).count()
    
    is_loyal_customer = recent_orders_count >= 10
    
    # Get detailed purchase history with order items
    purchase_history = []
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        purchase_history.append({
            'order': order,
            'items': order_items,
            'total': order.total_amount,
            'date': order.created_at,
            'status': order.status,
            'order_type': order.order_type
        })
    
    # Get order type breakdown
    order_types = orders.values('order_type').annotate(count=Count('id')).order_by('-count')
    
    # Get monthly spending breakdown for last 6 months
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_spending = orders.filter(
        created_at__gte=six_months_ago,
        status='completed'
    ).annotate(
        month=TruncDate('created_at')
    ).values('month').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('month')
    
    context = {
        'customer': customer,
        'orders': orders,
        'purchase_history': purchase_history,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'order_types': order_types,
        'is_loyal_customer': is_loyal_customer,
        'recent_orders_count': recent_orders_count,
        'monthly_spending': monthly_spending,
    }
    
    return render(request, 'business/customer_detail.html', context)


# ==================== CUSTOMER API VIEWS ====================

@login_required
def api_customers_list(request):
    """API endpoint to get list of customers"""
    if request.method == 'GET':
        customers = Customer.objects.all().order_by('name')
        customers_data = []
        
        for customer in customers:
            customers_data.append({
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'address': customer.address,
                'created_at': customer.created_at.isoformat(),
                'order_count': customer.order_set.count()
            })
        
        return JsonResponse({
            'success': True,
            'customers': customers_data
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def api_customer_detail(request, customer_id):
    """API endpoint to get customer details"""
    if request.method == 'GET':
        try:
            customer = Customer.objects.get(id=customer_id)
            customer_data = {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'address': customer.address,
                'created_at': customer.created_at.isoformat(),
                'order_count': customer.order_set.count()
            }
            
            return JsonResponse({
                'success': True,
                'customer': customer_data
            })
            
        except Customer.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Customer not found'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
