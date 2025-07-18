from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_count', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    inlines = [CartItemInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'book', 'quantity', 'total_price']
    list_filter = ['added_at']
    search_fields = ['cart__user__username', 'book__title']
