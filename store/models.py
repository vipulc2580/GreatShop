from django.db import models
from django.urls import reverse
from category.models import Category
# Create your models here.
class Product(models.Model):
    product_name=models.CharField(max_length=200,unique=True)
    slug=models.SlugField(max_length=200,unique=True)
    description=models.TextField(max_length=500,blank=True)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    image=models.ImageField(upload_to='photos/products')
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name ="Product"
        verbose_name_plural ="Products"

    def __str__(self):
        return self.product_name

    def get_url(self):
        # return reverse("Product_detail", kwargs={"pk": self.pk})
        return reverse('product_detail',args=[self.category.category_slug,self.slug])


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True).values_list('variation_value', flat=True)

    def size(self):
        return super(VariationManager,self).filter(variation_category='size').values_list('variation_value', flat=True)

class Variation(models.Model):

    objects = models.Manager()  # default manager
    variations = VariationManager()  # custom manager

    variation_category_choices=(
        ('color','color'),
        ('size','size'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_category=models.CharField(max_length=50,choices=variation_category_choices)
    variation_value=models.CharField(max_length=50)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name ="Variation"
        verbose_name_plural = "Variations"

    def __str__(self):
        return self.variation_value
    # def get_absolute_url(self):
        # return reverse("Variation_detail", kwargs={"pk": self.pk})
