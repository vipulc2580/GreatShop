# Generated by Django 5.2 on 2025-04-18 18:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_assigncouponentry'),
        ('orders', '0006_order_tax_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='cart.coupon'),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_amount',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10),
        ),
    ]
