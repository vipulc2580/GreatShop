# Generated by Django 5.2 on 2025-04-14 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_tax'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tax',
            old_name='type',
            new_name='tax_type',
        ),
    ]
