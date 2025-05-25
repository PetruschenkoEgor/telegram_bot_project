from django.contrib import admin

from .models import Category, Subcategory, Product, Cart, CartItem, Order, Delivery, TelegramUser


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('title',)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'title', 'slug', 'is_active',)
    list_filter = ('is_active', 'category',)
    search_fields = ('title',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'subcategory', 'title', 'slug', 'description', 'price', 'stock', 'is_active', 'created_at', 'updated_at',)
    list_filter = ('subcategory', 'stock', 'is_active',)
    search_fields = ('title', 'description',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at',)
    list_filter = ('created_at',)
    search_fields = ('user',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity',)
    list_filter = ('quantity',)
    search_fields = ('cart', 'product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at', 'updated_at',)
    list_filter = ('status',)
    search_fields = ('user', 'total_price', 'created_at',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'address', 'phone', 'comment', 'delivery_date',)
    search_fields = ('order', 'address', 'phone', 'comment', 'delivery_date',)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'created_at',)
    list_filter = ('created_at',)
    search_fields = ('user_id', 'created_at',)
