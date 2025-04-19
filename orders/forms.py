from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    coupon_code = forms.CharField(max_length=20, required=False)

    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'state',
            'city',
            'country',
            'pincode',
            'address_line_1',
            'address_line_2',
            'order_note',
            'coupon_code']
