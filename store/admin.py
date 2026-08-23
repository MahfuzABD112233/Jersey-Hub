from django.contrib import admin
from .models import Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        'product',
        'quantity',
        'unit_price',
    )

    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'price',
        'stock',
    )

    search_fields = (
        'name',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'total_amount',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'id',
        'user__username',
        'user__email',
    )

    readonly_fields = (
        'user',
        'total_amount',
        'created_at',
    )

    inlines = [
        OrderItemInline,
    ]

    # Admin cannot manually create orders
    def has_add_permission(self, request):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'unit_price',
    )

    search_fields = (
        'product__name',
        'order__id',
    )

    # Admin cannot manually create order items
    def has_add_permission(self, request):
        return False