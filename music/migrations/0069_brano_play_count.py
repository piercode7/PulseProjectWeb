# Generated by Django 4.2.11 on 2024-09-05 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0068_alter_brano_title_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='brano',
            name='play_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]