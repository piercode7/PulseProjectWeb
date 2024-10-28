# Generated by Django 4.2.11 on 2024-08-26 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0060_temporderdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporderdata',
            name='is_order_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='temporderdata',
            name='payment_id',
            field=models.CharField(max_length=100),
        ),
    ]
