# Generated by Django 4.2.11 on 2024-04-26 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0021_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='genre',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='music.genre'),
        ),
    ]
