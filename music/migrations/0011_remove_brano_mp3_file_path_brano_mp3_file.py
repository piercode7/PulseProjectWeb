# Generated by Django 4.2.11 on 2024-04-22 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0010_remove_brano_mp3_file_brano_mp3_file_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brano',
            name='mp3_file_path',
        ),
        migrations.AddField(
            model_name='brano',
            name='mp3_file',
            field=models.FileField(blank=True, null=True, upload_to='brani_mp3/'),
        ),
    ]