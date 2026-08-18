from django.contrib import admin
from .models import (
    shopform, indexshop, UserProfile, ContactForm, indexform, Book, Order, OrderItem
)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'total_amount', 'status', 'created_at')
    inlines = [OrderItemInline]
    list_filter = ('status',)
    search_fields = ('name', 'email', 'phone')
    list_editable = ('status',)
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'quantity', 'price')

admin.site.register(shopform)
admin.site.register(indexshop)
admin.site.register(UserProfile)
admin.site.register(ContactForm)
admin.site.register(indexform)
admin.site.register(Book)