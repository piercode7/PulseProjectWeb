# Generated by Django 4.2.11 on 2024-08-23 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0053_merchandise_reservation_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='merchandise',
            name='reservation_time',
        ),
        migrations.RemoveField(
            model_name='merchandise',
            name='reserved_quantity',
        ),
    ]
