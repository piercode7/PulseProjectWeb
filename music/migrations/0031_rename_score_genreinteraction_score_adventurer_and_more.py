# Generated by Django 4.2.11 on 2024-04-28 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0030_trackplay'),
    ]

    operations = [
        migrations.RenameField(
            model_name='genreinteraction',
            old_name='score',
            new_name='score_adventurer',
        ),
        migrations.AddField(
            model_name='artistprofile',
            name='listening_mode',
            field=models.CharField(choices=[('adventurer', 'Soundscape Adventurer'), ('seeker', 'Harmony Seeker'), ('connoisseur', 'Devoted Connoisseur')], default='seeker', max_length=20),
        ),
        migrations.AddField(
            model_name='genreinteraction',
            name='score_connoisseur',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='genreinteraction',
            name='score_seeker',
            field=models.FloatField(default=0),
        ),
    ]
