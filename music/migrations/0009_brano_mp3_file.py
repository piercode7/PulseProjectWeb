# Generated by Django 4.2.11 on 2024-04-22 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0008_alter_artistprofile_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='brano',
            name='mp3_file',
            field=models.FileField(blank=True, null=True, upload_to='brani_mp3/'),
        ),
    ]
