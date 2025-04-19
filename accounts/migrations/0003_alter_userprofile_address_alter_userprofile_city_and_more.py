# Generated by Django 5.2 on 2025-04-16 15:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile', name='address', field=models.CharField(
                blank=True, max_length=200, null=True), ), migrations.AlterField(
            model_name='userprofile', name='city', field=models.CharField(
                blank=True, max_length=50, null=True), ), migrations.AlterField(
            model_name='userprofile', name='country', field=models.CharField(
                blank=True, max_length=50, null=True), ), migrations.AlterField(
            model_name='userprofile', name='pincode', field=models.IntegerField(
                blank=True, null=True, validators=[
                    django.core.validators.MaxValueValidator(899999)]), ), migrations.AlterField(
            model_name='userprofile', name='state', field=models.CharField(
                blank=True, max_length=50, null=True), ), ]
