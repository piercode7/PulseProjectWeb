# Generated by Django 4.2.11 on 2024-04-25 02:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0018_alter_brano_unique_together_brano_artist_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='brano',
            name='creation_date',
            field=models.DateField(default=datetime.date(2024, 4, 25)),
        ),
    ]
