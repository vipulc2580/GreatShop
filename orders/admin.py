from django.contrib import admin
from .models import Payment, Order, OrderProduct, Tax
# Register your models here.


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'payment_id',
        'payment_method',
        'amount_paid',
        'status']


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = (
        'user',
        'order',
        'product',
        'quantity',
        'product_price',
        'ordered',
        'payment')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'full_name',
        'email',
        'order_total',
        'tax',
        'status',
        'is_ordered',
        'created_at',
        'coupon',
        'general_coupon']
    list_filter = ['status', 'is_ordered','general_coupon','coupon']
    search_fields = [
        'order_number',
        'first_name',
        'last_name',
        'phone_number',
        'email']
    list_per_page = 20
    inlines = [OrderProductInline]


class OrderProductAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'order',
        'product',
        'quantity',
        'product_price',
        'ordered']


class TaxAdmin(admin.ModelAdmin):
    list_display = ['tax_type', 'tax_percent']


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(Tax, TaxAdmin)
