# Generated by Django 4.2.11 on 2024-08-21 22:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0045_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='album',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='music.album'),
        ),
    ]
