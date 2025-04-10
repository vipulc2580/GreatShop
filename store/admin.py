from django.contrib import admin
from .models import Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={
        'slug':('product_name',)
    }
    list_display=['product_name','slug','updated_at','category','price','is_available']
    orderings=('-created_at',)

admin.site.register(Product,ProductAdmin)