from django.db import models
from store.models import Product, Variation
from accounts.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, UniqueConstraint
# Create your models here.


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "CartItem"
        verbose_name_plural = "CartItems"

    def sub_total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"




class Coupon(models.Model):   
    code = models.CharField(max_length=20)  # You may want this longer for user-specific ones
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)]
    ) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        constraints = [
            UniqueConstraint(
                fields=['code', 'user'],
                condition=Q(used=False),
                name='unique_active_coupon_per_user'
            )
        ]

    def is_valid(self):
        return not self.used and self.expires_at > timezone.now()

    def get_discount_amount(self, amount):
        discount_amount = float(amount * (self.discount_percent / 100))
        return round(discount_amount, 2)

    def __str__(self):
        return self.code


class GeneralCoupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)]
    ) 
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'GeneralCoupon'
        verbose_name_plural = 'GeneralCoupon'

    def __str__(self):
        return self.code

    def is_valid(self):
        return self.is_active

    def get_discount_amount(self, amount):
        discount_amount = float(amount * (self.discount_percent / 100))
        return round(discount_amount, 2)

    