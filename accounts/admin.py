from django.contrib import admin
from .models import User, UserProfile
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class CustomUserAdmin(UserAdmin):
    list_display = [
        'email',
        'first_name',
        'last_name',
        'username',
        'last_login',
        'dated_joined',
        'is_active']
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'dated_joined')
    ordering = ('-dated_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'profile_picture',
        'city',
        'pincode',
        'state',
        'country']
    list_filter = ('state', 'city', 'pincode')


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
