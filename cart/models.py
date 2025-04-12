from django.db import models
from store.models import Product,Variation

# Create your models here.
class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    created_at=models.DateField(auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural ="Carts"

    def __str__(self):
        return self.cart_id

   

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "CartItem"
        verbose_name_plural = "CartItems"

    def sub_total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"