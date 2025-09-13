from django.contrib import admin
from .models import (
    Category, Product, Customer, Order, OrderItem, 
    InventoryTransaction, Sales, QRCode, SMSNotification
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'product_type', 'price', 'quantity', 'is_active']
    list_filter = ['category', 'product_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'quantity', 'is_active']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'order_type', 'status', 'total_amount', 'created_at']
    list_filter = ['order_type', 'status', 'created_at']
    search_fields = ['order_id', 'customer__name']
    inlines = [OrderItemInline]
    readonly_fields = ['order_id', 'created_at', 'updated_at']


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['product__name']


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['order', 'created_at']


@admin.register(SMSNotification)
class SMSNotificationAdmin(admin.ModelAdmin):
    list_display = ['order', 'phone_number', 'status', 'created_at']
    list_filter = ['status', 'created_at']
