import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from music.forms import AlbumForm, MerchandiseForm
from music.models import Comment, ArtistProfile, ListenerProfile, Order, Album, \
    Brano, Playlist

logger = logging.getLogger(__name__)

# modifica info album
@login_required
def edit_album(request, username, album_id):
    artist_profile = get_object_or_404(ArtistProfile, user__username=username)
    album = get_object_or_404(Album, pk=album_id, artist=artist_profile)

    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Album successfully updated.")
                return redirect('my_albums', username=username)
            except Exception as e:
                form.add_error(None, "Error saving album. Please try again later.")
        else:
            messages.error(request, "The form is invalid. Correct the errors and try again.")
    else:
        form = AlbumForm(instance=album)

    return render(request, 'music/album/edit_album.html', {'form': form, 'album': album})


from django.contrib.auth.decorators import login_required

import os
import shutil

# cancellazione album
@login_required
def delete_album(request, username, album_id):
    try:
        artist_profile = get_object_or_404(ArtistProfile, user__username=username)
        album = get_object_or_404(Album, pk=album_id, artist=artist_profile)

        if request.method == 'POST':
            if album.cover_image:
                album_dir = os.path.dirname(album.cover_image.path)
                if os.path.exists(album_dir):
                    shutil.rmtree(album_dir)
            album.delete()
            messages.success(request, 'Album deleted successfully!')
            return redirect('my_albums', username=username)

        return render(request, 'music/album/confirm_delete_album.html', {
            'album': album,
        })
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        messages.error(request, 'An error occurred while deleting the album.')
        return redirect('home')

# cancellazione canzone
@login_required
def delete_song(request, username, album_id, brano_id):
    try:
        # Verifica che l'utente autenticato corrisponda all'artista
        if request.user.username != username:
            messages.error(request, "You are not authorized to delete this song.")
            return redirect('home')

        artist_profile = get_object_or_404(ArtistProfile, user__username=username)
        album = get_object_or_404(Album, pk=album_id, artist=artist_profile)
        brano = get_object_or_404(Brano, pk=brano_id, album=album)

        if request.method == 'POST':
            try:
                # Controlla se c'è un file MP3 associato e rimuovilo
                if brano.mp3_file:
                    brano.mp3_file.delete(save=False)  # Elimina il file senza salvare nuovamente l'oggetto

                brano.delete()
                messages.success(request, "Song successfully deleted.")
                return redirect('my_albums', username=username)
            except Exception as e:
                messages.error(request, "Error deleting song. Please try again later.")
                return redirect('edit_album', username=username, album_id=album_id)

        return render(request, 'music/Brano/confirm_delete_brano.html', {'brano': brano, 'album': album})

    except ArtistProfile.DoesNotExist:
        messages.error(request, "Artist profile not found.")
        return redirect('home')
    except Album.DoesNotExist:
        messages.error(request, "Album not found.")
        return redirect('home')
    except Brano.DoesNotExist:
        messages.error(request, "Brano not found.")
        return redirect('home')
    except Exception as e:
        messages.error(request, "An unexpected error occurred.")
        return redirect('home')

# modifica merch
@login_required
def edit_merch(request, username, merch_id):
    artist_profile = get_object_or_404(ArtistProfile, user__username=username)
    merchandise = get_object_or_404(Merchandise, id=merch_id, artist=artist_profile)

    if request.method == 'POST':
        form = MerchandiseForm(request.POST, request.FILES, instance=merchandise)
        if form.is_valid():
            form.save()
            return redirect('my_merch', username=artist_profile.user.username)  # Redirigi alla lista di merchandise
    else:
        form = MerchandiseForm(instance=merchandise)

    return render(request, 'music/merchandise/edit_merch.html', {
        'form': form,
        'artist_profile': artist_profile,
        'merchandise': merchandise
    })


from django.contrib.auth.decorators import login_required
from .forms import BranoForm

# modifica brano
@login_required
def edit_brano(request, username, album_id, brano_id):
    try:
        if request.user.username != username:
            messages.error(request, "You are not authorized to modify this album.")
            return redirect('login')

        artist_profile = get_object_or_404(ArtistProfile, user__username=username)
        album = get_object_or_404(Album, pk=album_id, artist=artist_profile)
        brano = get_object_or_404(Brano, pk=brano_id, album=album)

        if request.method == 'POST':
            form = BranoForm(request.POST, request.FILES, instance=brano, album=album)
            if form.is_valid():
                brano = form.save(commit=False)
                brano.album = album
                brano.artist = artist_profile
                brano.genre = album.genre  # Imposta il genere dell'album
                brano.save()
                messages.success(request,
                                 f"Successfully updated the song '{brano.title}' in the album '{album.title}'.")
                return redirect('my_albums', username=username)
            else:
                messages.error(request, f"Error in the form: {form.errors}")
        else:
            form = BranoForm(instance=brano, album=album)

        return render(request, 'music/Brano/edit_brano.html', {
            'form': form,
            'album': album,
            'artist': artist_profile,
            'brano': brano,
        })

    except Album.DoesNotExist:
        messages.error(request, "Album not found.")
        return redirect('home')
    except Brano.DoesNotExist:
        messages.error(request, "Song not found.")
        return redirect('home')
    except Exception as e:
        messages.error(request, "An error occurred during the operation.")
        return redirect('home')


from .forms import AlbumCoverForm

# modifica cover di un album
@login_required
def update_album_cover(request, username, album_id):
    artist_profile = get_object_or_404(ArtistProfile, user__username=username)
    album = get_object_or_404(Album, pk=album_id, artist=artist_profile)

    if request.method == 'POST':
        form = AlbumCoverForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Album cover successfully updated.")
                return redirect('my_albums', username=username)
            except Exception as e:
                form.add_error(None, "Error updating album art. Please try again later.")
        else:
            messages.error(request, "The form is invalid. Correct the errors and try again.")
    else:
        form = AlbumCoverForm(instance=album)

    return render(request, 'music/update_album_cover.html', {'form': form, 'album': album})


from django.contrib.auth.decorators import login_required

# cancellazione playlist
@login_required
def delete_playlist(request, username, playlist_id):
    try:
        listener_profile = get_object_or_404(ListenerProfile, user__username=username)

        # Assicurati che l'utente corrente sia il proprietario della playlist
        if request.user != listener_profile.user:
            return redirect('my_playlists', username=username)

        playlist = get_object_or_404(Playlist, id=playlist_id, listener=listener_profile)
        playlist.delete()
        messages.success(request, 'Playlist deleted successfully!')
        return redirect('my_playlists', username=username)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        messages.error(request, 'An error occurred while deleting the playlist.')
        return redirect('home')

# cancella brano da playlist
@login_required
def delete_track_from_playlist(request, username, playlist_id, track_id):
    try:
        playlist = get_object_or_404(Playlist, id=playlist_id, listener__user__username=username)
        track = get_object_or_404(Brano, id=track_id)

        if request.method == "POST":
            if track in playlist.tracks.all():
                playlist.tracks.remove(track)
                messages.success(request, 'Track removed from playlist successfully!')
            else:
                messages.info(request, 'Track is not in the playlist.')
            return redirect('view_playlist', username=username, playlist_id=playlist_id)

        return render(request, 'music/Brano/confirm_delete_track.html', {
            'playlist': playlist,
            'track': track,
        })
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        messages.error(request, 'An error occurred while removing the track from the playlist.')
        return redirect('home')


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

# cancella commento dal centro discussioni
@login_required
def delete_comment(request, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)

        if comment.listener.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this comment.")

        if request.method == 'POST':
            artist_username = comment.artist.user.username
            comment.delete()
            messages.success(request, "Comment deleted successfully.")
            return redirect('artist_discussion', username=artist_username)
        else:
            return render(request, 'music/vlog/confirm_delete.html', {'comment': comment})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return redirect('home')


from django.utils import timezone
from .models import Merchandise
from django.db import transaction

# cancellazione ordini
def clean_expired_orders():
    expired_orders = Order.objects.filter(
        payment_status='Pending',
        merchandise__reservation_expires_at__lt=timezone.now()
    )
    for order in expired_orders:
        with transaction.atomic():
            merch = order.merchandise
            merch.release_reservation(order.quantity)
            order.delete()


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Notification

# cancellazione notifiche ricevute
@login_required
def delete_all_notifications(request):
    # Elimina tutte le notifiche dell'utente attuale
    Notification.objects.filter(user=request.user).delete()
    return redirect('notification_center')


from django.contrib.auth.decorators import login_required
from .models import GenreInteraction

# reset delle interazioni com i conteunti musicali
@login_required
def reset_interactions(request, username):
    if request.user.username != username:
        return JsonResponse({'message': 'Action not authorized'}, status=403)

    # Cancella tutte le interazioni del listener corrente
    GenreInteraction.objects.filter(user__username=username).delete()
    return redirect('my_interactions', username=username)
