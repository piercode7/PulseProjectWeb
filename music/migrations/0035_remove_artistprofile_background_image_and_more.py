# Generated by Django 4.2.11 on 2024-05-03 21:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0034_artistprofile_background_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artistprofile',
            name='background_image',
        ),
        migrations.RemoveField(
            model_name='listenerprofile',
            name='background_image',
        ),
    ]
