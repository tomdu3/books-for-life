# Generated by Django 4.1 on 2023-10-01 13:12

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image',
            field=cloudinary.models.CloudinaryField(default='profile_image', max_length=255, verbose_name='Profile Image'),
        ),
    ]
