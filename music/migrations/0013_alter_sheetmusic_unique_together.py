# Generated by Django 4.2.11 on 2024-04-23 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0012_sheetmusic_merchandise_instrument'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sheetmusic',
            unique_together={('title', 'artist')},
        ),
    ]
