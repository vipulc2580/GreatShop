# Generated by Django 5.2 on 2025-04-18 23:23

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0011_generalcoupon"),
    ]

    operations = [
        migrations.AddField(
            model_name="generalcoupon",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="generalcoupon",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="discount_percent",
            field=models.PositiveIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(60),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="generalcoupon",
            name="code",
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
