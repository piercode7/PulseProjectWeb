# Generated by Django 4.2.11 on 2024-06-15 01:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0036_alter_artistprofile_name_alter_listenerprofile_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='album',
            name='price',
        ),
    ]