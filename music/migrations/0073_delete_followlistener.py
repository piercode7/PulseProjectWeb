# Generated by Django 4.2.11 on 2024-09-05 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0072_followlistener'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FollowListener',
        ),
    ]