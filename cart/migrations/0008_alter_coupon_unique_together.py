# Generated by Django 5.2 on 2025-04-18 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0007_alter_coupon_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='coupon',
            unique_together=set(),
        ),
    ]
