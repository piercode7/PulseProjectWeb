# Generated by Django 4.2.11 on 2024-08-28 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0065_album_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='published',
            field=models.BooleanField(default=True),
        ),
    ]
