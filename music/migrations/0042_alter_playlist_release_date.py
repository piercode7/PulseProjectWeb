# Generated by Django 4.2.11 on 2024-07-28 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0041_playlist_brano_playlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='release_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
