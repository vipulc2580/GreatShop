from django.urls import path
from . import views
urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),

    # paypal approval urls
    path('demo/checkout/api/paypal/order/create/',
         views.create_order, name='create_paypal_order'),
    path(
        "demo/checkout/api/paypal/order/<str:order_id>/<str:order_number>/capture/",
        views.capture_order,
        name="capture_order"),


    path('order_complete/', views.order_complete, name='order_complete'),

    # coupon related urls
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),

]
