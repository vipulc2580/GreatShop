from django.urls import path,include 
from . import views
from website.views import home
urlpatterns=[
    path('',home),
    path('register/',views.register,name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('activate/<uidb64>/<token>/',views.activate_account,name='activate'),

    # password related urls
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('reset_password/<uidb64>/<token>/',views.validate_reset_password,name='reset_password_link'),
    path('reset-password/<stored_token>/',views.reset_password,name='reset_password'),
    path('change_password/',views.change_password,name='change_password'),

    path('profile/',views.profile,name='profile'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    #my _orders
    path('my_orders/',views.my_orders,name='my_orders'),
    path('order_detail/<str:order_id>/',views.order_detail,name='order_detail'),
]