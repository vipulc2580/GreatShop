from django.contrib import admin
from .models import Cart, CartItem, Coupon, GeneralCoupon
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import models


class AssignCouponAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_content=None):
        return HttpResponseRedirect(reverse('admin_assign_coupons'))

    def has_module_permission(self, request):
        return True


class AssignCouponEntry(models.Model):
    class Meta:
        verbose_name_plural = "Assign Coupons"
        managed = False  # Prevents Django from trying to create a DB table


# Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'created_at']


class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'cart', 'quantity', 'is_active']


class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'user',
        'discount_percent',
        'used',
        'expires_at',
        'created_at']
    list_filter = ('code', 'user', 'used', 'expires_at')
    search_fields = ('code', 'user__first_name', 'user__email')


class GeneralCouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'is_active']
    list_editable = ['is_active']


admin.site.register(Coupon, CouponAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(AssignCouponEntry, AssignCouponAdmin)
admin.site.register(GeneralCoupon, GeneralCouponAdmin)
