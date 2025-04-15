from django.urls import path,include 
from . import views
urlpatterns = [
    path('',views.cart,name='cart'),
    path('add_cart/<int:product_id>',views.add_cart,name='add_cart'),
    path('increment_cart_item/',views.increment_cart_item,name='increment_cart_item'),
    path('decrement_cart_item/',views.decrement_cart_item,name='decrement_cart_item'),
    path('remove_cart_item/',views.remove_cart_item,name='remove_cart_item'),
    path('checkout/',views.checkout,name='checkout'),
]
