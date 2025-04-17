from django.db import models
from store.models import Product,Variation
from accounts.models import User
from django.utils import timezone
# Create your models here.
class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    created_at=models.DateField(auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural ="Carts"

    def __str__(self):
        return self.cart_id

   

class CartItem(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True)
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
    code=models.CharField(max_length=20)
    discount_percent=models.PositiveIntegerField()
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now=True)
    expires_at=models.DateTimeField()
    used=models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def is_valid(self):
        return not used and self.expires_at> timezone.now()
    

    def __str__(self):
        return self.code
