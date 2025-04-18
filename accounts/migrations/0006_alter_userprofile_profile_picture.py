# Generated by Django 5.2 on 2025-04-16 18:01

import accounts.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='userprofile/',
                validators=[
                    accounts.validators.validate_profile_picture]),
        ),
    ]
