# Generated by Django 4.2.11 on 2024-04-22 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0007_album_cover_image_alter_brano_side'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artistprofile',
            name='bio',
            field=models.TextField(max_length=800),
        ),
    ]
