# Generated by Django 4.2.11 on 2024-04-25 01:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0015_artistprofile_background_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='creation_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='artistprofile',
            name='creation_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='brano',
            name='creation_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='merchandise',
            name='creation_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='sheetmusic',
            name='creation_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
