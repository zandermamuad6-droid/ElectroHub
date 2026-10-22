
from django.contrib import admin
from .models import CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("component_name", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "total_amount",
        "status",
        "payment_method",
        "payment_status",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_method",
        "payment_status",
        "created_at",
    )
    search_fields = ("order_number", "user__username")
    readonly_fields = (
        "order_number",
        "total_amount",
        "created_at",
        "updated_at",
    )
    inlines = [OrderItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "component", "price", "quantity", "created_at")
    search_fields = ("user__username", "component__name")
