# Generated by Django 5.2 on 2025-04-18 18:40

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0008_alter_coupon_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='coupon',
            unique_together={('code', 'user')},
        ),
    ]
