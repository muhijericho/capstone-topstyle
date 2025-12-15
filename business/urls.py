from django.shortcuts import redirect
from django.urls import path

from . import views


def redirect_to_landing(request):
    return redirect('landing')

urlpatterns = [
    # Landing page (home)
    path('', views.landing_page, name='landing'),
    path('home/', views.landing_page, name='home'),
    
    # Public track order (no login required)
    path('track-my-order/', views.public_track_order, name='public_track_order'),
    
    # Offline page
    path('offline/', views.offline_view, name='offline'),
    
    # Chrome DevTools well-known handler (suppresses 404 warnings)
    path('.well-known/appspecific/com.chrome.devtools.json', views.chrome_devtools_handler, name='chrome_devtools'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-reset-code/', views.verify_reset_code, name='verify_reset_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Estimator API endpoints (for create order page)
    path('api/estimator/add-product/', views.add_product_from_estimator, name='add_product_from_estimator'),
    path('api/estimator/create-order/', views.create_order_from_estimator, name='create_order_from_estimator'),
    
    # Test page
    # path('test-rental/', views.test_rental, name='test_rental'),
    
    # Orders
    path('orders/', views.orders_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/assign-staff/', views.assign_staff_to_order, name='assign_staff_to_order'),
    path('orders/<int:order_id>/mark-done/', views.mark_order_done_by_staff, name='mark_order_done_by_staff'),
    path('orders/archive-completed/', views.archive_completed_orders, name='archive_completed_orders'),
    path('api/revenue-details/', views.api_revenue_details, name='api_revenue_details'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/payment-method/', views.payment_method, name='payment_method'),
    path('orders/payment-process/', views.payment_process, name='payment_process'),
    path('orders/receipt/', views.order_receipt_new, name='order_receipt_new'),
    path('orders/track/', views.track_order, name='track_order'),
    path('api/orders/create/', views.create_order_from_session, name='create_order_from_session'),
    path('api/orders/check-materials/', views.api_check_repair_materials_availability, name='check_materials_availability'),
    
    # Activity Log
    path('activity-log/', views.activity_log, name='activity_log'),
    
    # API Endpoints for Database Connections
    path('api/inventory-status/', views.api_inventory_status, name='api_inventory_status'),
    path('api/sales-calculation/', views.api_sales_calculation, name='api_sales_calculation'),
    path('api/order-tracking/', views.api_order_tracking, name='api_order_tracking'),
    path('api/customers/', views.api_customers_list, name='api_customers_list'),
    path('api/customers/<int:customer_id>/', views.api_customer_detail, name='api_customer_detail'),
    path('api/products/', views.api_products_list, name='api_products_list'),
    path('api/zippers/', views.api_zippers_list, name='api_zippers_list'),
    path('api/buttons/', views.api_buttons_list, name='api_buttons_list'),
    path('api/patches/', views.api_patches_list, name='api_patches_list'),
    path('api/locks/', views.api_locks_list, name='api_locks_list'),
    path('api/garters/', views.api_garters_list, name='api_garters_list'),
    path('api/thread-availability/', views.api_thread_availability, name='api_thread_availability'),
    path('api/rental-status/', views.api_rental_status, name='api_rental_status'),
    # path('api/create-rental-simple/', views.create_rental_order_simple, name='create_rental_order_simple'),
    path('api/rental-availability-check/', views.api_rental_availability_check, name='api_rental_availability_check'),
    path('api/check-overdue-orders/', views.api_check_overdue_orders, name='api_check_overdue_orders'),
    path('api/return-individual-items/', views.api_return_individual_items, name='api_return_individual_items'),
    path('orders/<int:order_id>/items/', views.order_items, name='order_items'),
    path('orders/<int:order_id>/items/<int:item_id>/update/', views.update_order_item, name='update_order_item'),
    path('orders/<int:order_id>/items/<int:item_id>/delete/', views.delete_order_item, name='delete_order_item'),
    path('orders/<int:order_id>/payment/', views.order_payment, name='order_payment'),
    path('orders/<int:order_id>/receipt/', views.order_receipt, name='order_receipt'),
    path('orders/<int:order_id>/complete/', views.complete_order, name='complete_order'),
    path('orders/<int:order_id>/check-balance/', views.check_order_balance, name='check_order_balance'),
    
    # Inventory
    path('inventory/', views.inventory_list, name='inventory'),
    path('inventory/add/', views.add_product, name='add_product'),
    path('inventory/add-customize/', views.add_customize_product, name='add_customize_product'),
    path('api/customize-products/', views.api_customize_products_list, name='api_customize_products_list'),
    path('api/upload-customize-image/', views.upload_customize_image_immediate, name='upload_customize_image_immediate'),
    path('inventory/add-material/', views.add_material_product, name='add_material_product'),
    path('inventory/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('inventory/<int:product_id>/archive/', views.archive_product, name='archive_product'),
    path('inventory/<int:product_id>/return/', views.return_rental_product, name='return_rental_product'),
    path('inventory/<int:product_id>/notify/', views.send_overdue_notification, name='send_overdue_notification'),
    path('rentals/', views.rental_management, name='rental_management'),
    
    # Materials Management
    path('materials/', views.materials_management, name='materials_management'),
    path('materials/<int:product_id>/edit/', views.edit_material, name='edit_material'),
    path('materials/<int:product_id>/restock/', views.restock_material, name='restock_material'),
    
    # Material Management API
    path('api/material-pricing-options/', views.api_get_material_pricing_options, name='api_get_material_pricing_options'),
    path('api/material-availability-tracking/', views.api_material_availability_tracking, name='api_material_availability_tracking'),
    path('api/materials-details/', views.api_materials_details, name='api_materials_details'),
    path('api/material/<int:product_id>/detail/', views.api_material_detail, name='api_material_detail'),
    path('api/material-usage-history/', views.api_material_usage_history, name='api_material_usage_history'),
    path('api/product/<int:product_id>/detail/', views.api_product_detail, name='api_product_detail'),
    path('api/product/<int:product_id>/edit/', views.api_edit_product, name='api_edit_product'),
    path('api/product/<int:product_id>/adjust-stock/', views.api_adjust_stock, name='api_adjust_stock'),
    
    # Sales
    path('sales/', views.sales_page, name='sales'),
    path('api/accounting-details/', views.api_accounting_details, name='api_accounting_details'),
    path('reports/', views.reports_dashboard, name='reports'),
    
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
    
    # SMS functionality
    path('api/send-sms/', views.send_sms, name='send_sms'),
    
    # Rental functionality
    path('api/rental-availability/', views.api_rental_availability, name='api_rental_availability'),
    path('api/return-rental/', views.api_return_rental, name='api_return_rental'),
    path('api/rental-status/', views.api_rental_status, name='api_rental_status'),
    path('api/rental-items/', views.api_rental_items, name='api_rental_items'),
    path('api/rental-status-update/', views.api_rental_status_update, name='api_rental_status_update'),
    
    # Archive functionality
    path('archive/', views.archive, name='archive'),
    path('archive/restore/<str:item_type>/<int:item_id>/', views.restore_item, name='restore_item'),
    path('archive/delete-permanent/<str:item_type>/<int:item_id>/', views.delete_permanent, name='delete_permanent'),
    path('archive/bulk-delete/', views.bulk_delete_permanent, name='bulk_delete_permanent'),
    
    # Inventory availability checking
    path('api/check-inventory-availability/', views.api_check_inventory_availability, name='api_check_inventory_availability'),
    
    # Rental status management
    path('api/update-rental-status/', views.api_update_rental_status, name='api_update_rental_status'),
    path('api/fix-stuck-rental-products/', views.api_fix_stuck_rental_products, name='api_fix_stuck_rental_products'),
    
    # Customer data management
    path('api/order/<int:order_id>/customer-data/', views.api_get_order_customer_data, name='api_get_order_customer_data'),
    path('api/return-details/<int:order_id>/', views.api_return_details, name='api_return_details'),
    
    # QR Code generation
    path('api/generate-qr-code/', views.api_generate_qr_code, name='api_generate_qr_code'),
    path('api/generate-qr-code-for-order/', views.api_generate_qr_code_for_order, name='api_generate_qr_code_for_order'),
    path('api/decode-qr-image/', views.api_decode_qr_image, name='api_decode_qr_image'),
    
    # Order identifier management
    path('api/fix-order-identifiers/', views.api_fix_order_identifiers, name='api_fix_order_identifiers'),
    
    # Static order data management
    path('api/fix-static-orders/', views.api_fix_static_orders, name='api_fix_static_orders'),
    path('api/cleanup-all-static-orders/', views.api_cleanup_all_static_orders, name='api_cleanup_all_static_orders'),
    path('api/cleanup-duplicate-customize-products/', views.api_cleanup_duplicate_customize_products, name='api_cleanup_duplicate_customize_products'),
    path('api/ensure-only-real-orders/', views.api_ensure_only_real_orders, name='api_ensure_only_real_orders'),
    
    # Frontend-Backend synchronization
    path('api/sync-frontend-backend-orders/', views.api_sync_frontend_backend_orders, name='api_sync_frontend_backend_orders'),
    
    # Separate order type APIs
    path('api/sync-rental-orders/', views.api_sync_rental_orders, name='api_sync_rental_orders'),
    path('api/sync-repair-orders/', views.api_sync_repair_orders, name='api_sync_repair_orders'),
    path('api/sync-custom-orders/', views.api_sync_custom_orders, name='api_sync_custom_orders'),
    
    # Backfill repair order categories
    path('api/backfill-repair-categories/', views.api_backfill_repair_order_categories, name='api_backfill_repair_order_categories'),
    
    # Navigation Health Check
    path('api/navigation-health/', views.navigation_health_check, name='navigation_health_check'),
    path('api/quick-nav-check/', views.quick_nav_check, name='quick_nav_check'),
    
    # Admin Pages
    path('user/settings/', views.admin_settings, name='admin_settings'),
    path('user/help-support/', views.help_support, name='help_support'),
    path('user/display-accessibility/', views.display_accessibility, name='display_accessibility'),
    path('user/feedback/', views.feedback, name='feedback'),
    
    # Uniform Measurement Form
    path('uniform-measurement/', views.uniform_measurement_form, name='uniform_measurement_form'),
    
    # Auto-Save API
    path('api/autosave/sync/', views.api_autosave_sync, name='api_autosave_sync'),
    
    # Staff Management
    path('staff/', views.staff_management, name='staff_management'),
    path('staff/report/pdf/', views.staff_report_pdf, name='staff_report_pdf'),
    path('staff/report/excel/', views.staff_report_excel, name='staff_report_excel'),
    path('staff/<int:staff_id>/salary/', views.staff_salary, name='staff_salary'),
    path('staff/<int:staff_id>/withdraw/', views.withdraw_staff_revenue, name='withdraw_staff_revenue'),
    path('staff/<int:staff_id>/withdrawal-history/', views.staff_withdrawal_history, name='staff_withdrawal_history'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/<int:staff_id>/edit/', views.edit_staff, name='edit_staff'),
    path('staff/<int:staff_id>/delete/', views.delete_staff, name='delete_staff'),
    path('staff/<int:staff_id>/', views.staff_detail, name='staff_detail'),
]
 