from django.contrib import admin
from .models import Product,Variation,ReviewRating,ProductGallery
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model=ProductGallery
    extra=1
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={
        'slug':('product_name',)
    }
    list_display=['product_name','stock','slug','updated_at','category','price','is_available']
    orderings=('-created_at',)
    inlines=[ProductGalleryInline,]

class VariationAdmin(admin.ModelAdmin):
    list_display=['product','variation_category','variation_value','is_active']
    list_editable=('is_active',)
    list_filter=('product','variation_category','variation_value',)

class ReviewRatingAdmin(admin.ModelAdmin):
    list_display=['subject','user','product','review','status','created_at']
    list_editable=('status',)
    list_filter=('user','status')

class ProductGalleryAdmin(admin.ModelAdmin):
    list_display=['product','image']
    list_filter=('product',)


admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating,ReviewRatingAdmin)
admin.site.register(ProductGallery,ProductGalleryAdmin)
