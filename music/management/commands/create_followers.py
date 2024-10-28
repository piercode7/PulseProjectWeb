import random
from django.core.management.base import BaseCommand

from music.models import ListenerProfile, ArtistProfile, Follow


class Command(BaseCommand):
    help = 'Create random follow relationships between listeners and artists'

    def handle(self, *args, **kwargs):
        # Ottieni tutti i listener e gli artisti
        listeners = list(ListenerProfile.objects.all())
        artists = ArtistProfile.objects.all()

        follow_count = 0

        for artist in artists:
            followers_added = set()

            # Genera un numero casuale di follower tra 2 e 5 per ogni artista
            num_followers = random.randint(2, 5)

            while len(followers_added) < num_followers:
                listener = random.choice(listeners)

                # Controlla se la relazione di follow esiste già
                if not Follow.objects.filter(follower=listener, followed=artist).exists() and listener not in followers_added:
                    # Crea la relazione di follow
                    Follow.objects.create(follower=listener, followed=artist)
                    followers_added.add(listener)
                    follow_count += 1
                    self.stdout.write(f"{listener.user.username} started following {artist.user.username}")

        self.stdout.write(self.style.SUCCESS(f"Creati {follow_count} relazioni di follow!"))
