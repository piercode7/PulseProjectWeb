# Generated by Django 4.2.11 on 2024-09-05 20:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0070_friendship'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Friendship',
        ),
    ]