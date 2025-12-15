from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from .models import (
    Category, Product, Customer, Order, OrderItem, 
    InventoryTransaction, Sales, QRCode, SMSNotification,
    MaterialType, MaterialPricing, ActivityLog, LandingPageImage
)

# Force unregister Order admin to clear any cached references
try:
    admin.site.unregister(Order)
except admin.sites.NotRegistered:
    pass

# Clear any admin cache
if hasattr(admin.site, '_registry'):
    admin.site._registry.clear()


# Re-register built-in auth models so the Users/Groups section appears in admin
admin.site.register(User, BaseUserAdmin)
admin.site.register(Group)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'material_type', 'product_type', 'price', 'quantity', 'is_active']
    list_filter = ['category', 'material_type', 'product_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'quantity', 'is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'product_type', 'image')
        }),
        ('Categorization', {
            'fields': ('category', 'material_type'),
            'classes': ('collapse',)
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'cost', 'quantity', 'current_quantity_in_stock', 'min_quantity', 'unit_of_measurement')
        }),
        ('Material Pricing', {
            'fields': ('material_pricing',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_archived')
        }),
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']


# REMOVED: OrderItemInline to avoid any potential field reference issues
# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 1
#     fields = ['product', 'quantity', 'unit_price', 'total_price']


# Ultra-minimal OrderAdmin to avoid any field reference issues
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_identifier', 'customer', 'order_type', 'status', 'total_amount']
    list_filter = ['order_type', 'status']
    search_fields = ['order_identifier']
    readonly_fields = ['order_id', 'created_at', 'updated_at']
    
    # Disable all potentially problematic features
    actions = None
    inlines = []
    list_editable = []
    list_select_related = []
    raw_id_fields = []
    autocomplete_fields = []
    
    def get_queryset(self, request):
        """Override to ensure clean queryset without any problematic fields"""
        return Order.objects.all()
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist_view to avoid any field reference issues"""
        try:
            # Call Django's built-in changelist_view to get proper ChangeList object
            response = super().changelist_view(request, extra_context=extra_context)
            
            # If we get here, everything worked fine
            return response
            
        except Exception as e:
            if 'created_by_id' in str(e):
                # If there's still a created_by_id reference, use a minimal queryset
                self.get_queryset = lambda request: Order.objects.only('id', 'order_identifier', 'customer_id', 'order_type', 'status', 'total_amount')
                # Try again with the minimal queryset
                return super().changelist_view(request, extra_context=extra_context)
            raise e

# Register the admin
admin.site.register(Order, OrderAdmin)


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


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit_of_measurement', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(MaterialPricing)
class MaterialPricingAdmin(admin.ModelAdmin):
    list_display = ['material_type', 'pricing_type', 'bundle_size', 'buy_price_per_unit', 'sell_price_per_unit', 'is_default']
    list_filter = ['material_type', 'pricing_type', 'is_default']
    search_fields = ['material_type__name']
    list_editable = ['buy_price_per_unit', 'sell_price_per_unit', 'is_default']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'description', 'user', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['description', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(LandingPageImage)
class LandingPageImageAdmin(admin.ModelAdmin):
    list_display = ['image_type', 'image_preview', 'is_active', 'created_at', 'updated_at']
    list_filter = ['image_type', 'is_active', 'created_at']
    search_fields = ['image_type', 'alt_text']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('image_type', 'image', 'image_preview_large', 'alt_text', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        """Show small thumbnail in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        """Show larger preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 500px; max-height: 300px; object-fit: contain; border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: #f8f9fa;" />',
                obj.image.url
            )
        return "No image uploaded yet"
    image_preview_large.short_description = 'Image Preview'
