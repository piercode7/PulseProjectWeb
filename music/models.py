import datetime

from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.contrib.auth.models import User

from django.contrib.auth.models import User

from django.contrib.auth.models import User

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, default="Unknown")  # Aggiunto valore predefinito
    bio = models.TextField(max_length=800)
    photo_image = models.ImageField(upload_to='photo_users/', null=True, blank=True)

    class Meta:
        abstract = True


class ArtistProfile(UserProfile):
    pass

    def __str__(self):
        return self.user.username  # O


class ListenerProfile(UserProfile):
    listening_mode = models.CharField(
        max_length=20,
        choices=[
            ('adventurer', 'Soundscape Adventurer'),
            ('seeker', 'Harmony Seeker'),
            ('connoisseur', 'Devoted Connoisseur')
        ],
        default='seeker'
    )


    def __str__(self):
        return self.user.username


from django.db import models


class Follow(models.Model):
    follower = models.ForeignKey(ListenerProfile, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(ArtistProfile, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.user.username} follows {self.followed.user.username}"


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class GenreInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='genre_interactions')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='user_interactions')
    score_adventurer = models.FloatField(default=0)
    score_seeker = models.FloatField(default=0)
    score_connoisseur = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'genre')

    def __str__(self):
        return f"{self.user.username} - {self.genre.name} - Scores: Adventurer: {self.score_adventurer}, Seeker: {self.score_seeker}, Connoisseur: {self.score_connoisseur}"


class Album(models.Model):
    artist = models.ForeignKey(ArtistProfile, related_name='albums', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    release_date = models.DateField()
    cover_image = models.ImageField(upload_to='album_covers/', null=True, blank=True)
    published = models.BooleanField(default=False)

    class Meta:
        unique_together = ('artist', 'title')

    def __str__(self):
        return f"{self.title} by {self.artist.name}"


# Modello Playlist
class Playlist(models.Model):
    listener = models.ForeignKey(ListenerProfile, related_name='playlists', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    release_date = models.DateField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='playlist_covers/', null=True, blank=True)
    tracks = models.ManyToManyField('Brano', related_name='playlists', blank=True)

    class Meta:
        unique_together = ('listener', 'title')



    def __str__(self):
        return f"{self.title} by {self.listener.user.username}"


class LikedPlaylist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'playlist')

    def __str__(self):
        return f"{self.user.username} likes {self.playlist.title}"


default_creation_date = datetime.date(2024, 4, 25)  # Imposta la data desiderata come default

from django.db import models
from django.utils.text import slugify
import os


def upload_to(instance, filename):
    artist_slug = slugify(instance.artist.name)
    album_slug = slugify(instance.album.title)
    return os.path.join('brani_mp3', artist_slug, album_slug, filename)


from django.db import models


class Brano(models.Model):
    album = models.ForeignKey(Album, related_name='brani', on_delete=models.CASCADE)
    artist = models.ForeignKey(ArtistProfile, related_name='brani', on_delete=models.CASCADE, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=140)
    side = models.PositiveIntegerField()
    track_index = models.PositiveIntegerField()
    duration = models.DurationField()
    mp3_file = models.FileField(upload_to=upload_to, null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True)

    # Nuovo campo per il numero di riproduzioni
    play_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('album', 'track_index', 'side', 'artist')
        ordering = ['album', 'side', 'track_index']
        verbose_name = "Song"  # Nome singolare
        verbose_name_plural = "Songs"  # Nome plurale

    def __str__(self):
        return f"{self.side} Track {self.track_index}: {self.title} by {self.artist.name} from {self.album.title}"


from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Album)
def update_album_artist_on_brani(sender, instance, **kwargs):
    if instance.pk:
        old_album = Album.objects.get(pk=instance.pk)
        if old_album.artist != instance.artist:
            Brano.objects.filter(album=instance).update(artist=instance.artist)


# Ricordati di collegare questo signal nel tuo file di configurazione dell'app o in un modulo pronto all'uso.


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from django.db import models


class Merchandise(models.Model):
    artist = models.ForeignKey(ArtistProfile, related_name='merchandise', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='merch_images/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    original_stock_quantity = models.PositiveIntegerField(default=0)
    creation_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.original_stock_quantity = self.stock_quantity
        super(Merchandise, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} by {self.artist.user.username}"

    def is_available(self):
        return self.stock_quantity > 0

    def purchase(self, quantity):
        if quantity <= self.stock_quantity:
            self.stock_quantity -= quantity
            self.save()
        else:
            raise ValueError("Quantità in stock insufficiente")


class SheetMusic(models.Model):
    artist = models.ForeignKey(ArtistProfile, related_name='sheet_music', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='sheet_music_files/')
    COMPLEXITY_CHOICES = (
        (1, '1 - Molto semplice'),
        (2, '2 - Semplice'),
        (3, '3 - Moderato'),
        (4, '4 - Complesso'),
        (5, '5 - Molto complesso'),
    )
    Complexity = models.IntegerField(choices=COMPLEXITY_CHOICES)
    creation_date = models.DateField(auto_now_add=True)  # Aggiunto default qui

    class Meta:
        unique_together = ('title', 'artist')

    def __str__(self):
        return self.title


from django.db import models
from django.contrib.auth.models import User


class TrackPlay(models.Model):
    brano = models.ForeignKey('Brano', related_name='plays', on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brano.title} played at {self.played_at}"


class Comment(models.Model):
    listener = models.ForeignKey('ListenerProfile', on_delete=models.CASCADE)
    artist = models.ForeignKey('ArtistProfile', on_delete=models.CASCADE, related_name='comments')
    album = models.ForeignKey('Album', on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.album:
            return f"Comment by {self.listener.user.username} on {self.album.title} by {self.artist.name}"
        else:
            return f"Comment by {self.listener.user.username} on {self.artist.name}"

    @property
    def is_reply(self):
        return self.parent is not None


from django.db import models
from django.contrib.auth.models import User
from .models import Merchandise

# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='sales', on_delete=models.CASCADE)
    merchandise = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=20)
    order_date = models.DateTimeField(default=timezone.now)

    # Nuovi campi per le informazioni di spedizione
    shipping_address = models.CharField(max_length=255)
    shipping_city = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=10)
    shipping_phone = models.CharField(max_length=15)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"


# models.py


from django.db import models
from django.contrib.auth.models import User


class TempOrderData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    merch = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reservation_expiration = models.DateTimeField()
    is_order_completed = models.BooleanField(default=False)  # Nuovo campo aggiunto

    def __str__(self):
        return f"TempOrderData for {self.user} - {self.payment_id}"


# models.py

from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('follow', 'Follow'),
        ('comment', 'Comment'),
        ('album', 'Album'),
        ('like_playlist', 'Like Playlist'),  # Aggiunto tipo di notifica per il like della playlist
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.message}"

    class Meta:
        ordering = ['-created_at']
