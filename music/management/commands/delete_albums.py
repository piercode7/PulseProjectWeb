from django.core.management.base import BaseCommand
from music.models import Album

class Command(BaseCommand):
    help = 'Deletes all albums from the database'

    def handle(self, *args, **options):
        if input("Are you sure you want to delete all albums? This cannot be undone. Type 'yes' to continue: ") == 'yes':
            Album.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All albums have been deleted.'))
