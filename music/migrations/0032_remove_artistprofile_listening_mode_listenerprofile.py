# Generated by Django 4.2.11 on 2024-05-03 20:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('music', '0031_rename_score_genreinteraction_score_adventurer_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artistprofile',
            name='listening_mode',
        ),
        migrations.CreateModel(
            name='ListenerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=120, null=True)),
                ('bio', models.TextField(max_length=800)),
                ('photo_image', models.ImageField(blank=True, null=True, upload_to='photo_users/')),
                ('background_image', models.ImageField(blank=True, null=True, upload_to='background_images/')),
                ('listening_mode', models.CharField(choices=[('adventurer', 'Soundscape Adventurer'), ('seeker', 'Harmony Seeker'), ('connoisseur', 'Devoted Connoisseur')], default='seeker', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]