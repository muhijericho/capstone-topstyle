from django.urls import path
from django.shortcuts import redirect
from . import views

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    # Root redirect to login
    path('', redirect_to_login, name='home'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Estimator API endpoints (for create order page)
    path('api/estimator/add-product/', views.add_product_from_estimator, name='add_product_from_estimator'),
    path('api/estimator/create-order/', views.create_order_from_estimator, name='create_order_from_estimator'),
    
    # Orders
    path('orders/', views.orders_list, name='orders'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/payment-method/', views.payment_method, name='payment_method'),
    path('orders/payment-process/', views.payment_process, name='payment_process'),
    path('orders/receipt/', views.order_receipt_new, name='order_receipt_new'),
    path('orders/track/', views.track_order, name='track_order'),
    path('api/orders/create/', views.create_order_from_session, name='create_order_from_session'),
    
    # Activity Log
    path('activity-log/', views.activity_log, name='activity_log'),
    
    # API Endpoints for Database Connections
    path('api/inventory-status/', views.api_inventory_status, name='api_inventory_status'),
    path('api/sales-calculation/', views.api_sales_calculation, name='api_sales_calculation'),
    path('api/order-tracking/', views.api_order_tracking, name='api_order_tracking'),
    path('api/customers/', views.api_customers_list, name='api_customers_list'),
    path('api/customers/<int:customer_id>/', views.api_customer_detail, name='api_customer_detail'),
    path('orders/<int:order_id>/items/', views.order_items, name='order_items'),
    path('orders/<int:order_id>/payment/', views.order_payment, name='order_payment'),
    path('orders/<int:order_id>/receipt/', views.order_receipt, name='order_receipt'),
    path('orders/<int:order_id>/complete/', views.complete_order, name='complete_order'),
    
    # Inventory
    path('inventory/', views.inventory_list, name='inventory'),
    path('inventory/add/', views.add_product, name='add_product'),
    path('inventory/<int:product_id>/archive/', views.archive_product, name='archive_product'),
    path('inventory/<int:product_id>/return/', views.return_rental_product, name='return_rental_product'),
    path('inventory/<int:product_id>/notify/', views.send_overdue_notification, name='send_overdue_notification'),
    path('rentals/', views.rental_management, name='rental_management'),
    
    # Sales
    path('sales/', views.sales_page, name='sales'),
    
    # Tracking
    path('track/', views.track_order, name='track_order'),
    
    # Customer Management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    
    # Reports
    path('reports/pdf/<str:report_type>/', views.generate_pdf_report, name='pdf_report'),
    path('reports/excel/<str:report_type>/', views.generate_excel_report, name='excel_report'),
    
    # Track Order
    path('track/result/', views.track_result, name='track_result'),
]
 