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

    path('profile/',views.profile,name='profile'),
]