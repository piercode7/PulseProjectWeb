from django.core.management.base import BaseCommand
from music.models import Genre  # Assicurati di modificare il percorso di importazione con il percorso corretto del modello Genre

class Command(BaseCommand):
    help = 'Populates the genres in the database'

    def handle(self, *args, **kwargs):
        genre_list = [
            'Alternative', 'Ambient', 'Blues', 'Classical', 'Country',
            'Disco', 'Electronic/Dance', 'Folk', 'Funk', 'Gospel', 'Grunge',
            'Hip Hop/Rap', 'House', 'Indie', 'Jazz', 'K-Pop', 'Latin',
            'Metal', 'Musical', 'Opera', 'Pop', 'Punk', 'R&B/Soul', 'Reggae', 'Reggaeton',
            'Rock', 'Ska', 'Soundtrack', 'Swing', 'Techno', 'Trap'
        ]
        for genre_name in genre_list:
            Genre.objects.get_or_create(name=genre_name)
        self.stdout.write(self.style.SUCCESS('Successfully populated genres in the database'))

# Assicurati di eseguire questo codice all'interno dell'ambiente virtuale di Django e nel contesto del progetto Django

