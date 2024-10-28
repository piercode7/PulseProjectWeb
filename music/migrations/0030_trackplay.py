# Generated by Django 4.2.11 on 2024-04-26 23:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0029_brano_genre_genreinteraction'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackPlay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('played_at', models.DateTimeField(auto_now_add=True)),
                ('brano', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plays', to='music.brano')),
            ],
        ),
    ]
