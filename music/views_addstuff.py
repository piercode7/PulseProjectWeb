import logging

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from .models import ListenerProfile, ArtistProfile, Brano, Album, Genre

# registrazione album per un artista
@login_required
def register_album(request, username):
    try:
        artist_profile = get_object_or_404(ArtistProfile, user__username=username)

        if request.method == 'POST':
            form = AlbumForm(request.POST, request.FILES)
            if form.is_valid():
                album = form.save(commit=False)
                album.artist = artist_profile
                try:
                    album.save()
                    messages.success(request, "Album successfully recorded.")
                    return redirect('my_albums', username=username)
                except IntegrityError:
                    form.add_error('title', 'An album with this title already exists for this artist.')
                except Exception as e:
                    form.add_error(None, "Error recording album. Please try again later.")
            else:
                messages.error(request, "The form is invalid. Correct the errors and try again.")
        else:
            form = AlbumForm()

        return render(request, 'music/album/register_album.html', {'form': form, 'artist_profile': artist_profile})

    except ArtistProfile.DoesNotExist:
        messages.error(request, "Profilo dell'artista non trovato.")
        return redirect('home')
    except Exception as e:
        messages.error(request, "An unexpected error occurred.")
        return redirect('home')


from django.contrib.auth.decorators import login_required
from .forms import PlaylistForm, AlbumForm, BranoForm, MerchandiseForm

# registrazione playlist per un ascoltatore
@login_required
def register_playlist(request, username):
    try:
        listener_profile = get_object_or_404(ListenerProfile, user__username=username)
        redirect_url = request.GET.get('next') or request.META.get('HTTP_REFERER')

        if request.method == 'POST':
            form = PlaylistForm(request.POST, request.FILES)
            if form.is_valid():
                playlist = form.save(commit=False)
                playlist.listener = listener_profile
                try:
                    playlist.save()
                    messages.success(request, "Playlist created successfully.")
                    if redirect_url:
                        return redirect(redirect_url)
                    return redirect('private_listener_profile', username=username)
                except IntegrityError:
                    form.add_error('title', 'A playlist with this title already exists for this listener.')
        else:
            form = PlaylistForm()

        return render(request, 'music/register_playlist.html', {
            'form': form,
            'listener_profile': listener_profile,
        })
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        messages.error(request, "An error occurred while creating the playlist.")
        return redirect('home')


from django.contrib import messages

logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required

# aggiunta di un brano di un artista alla playlist di un ascoltatore
@login_required
def add_to_playlist(request, username, playlist_id, track_id):
    listener_profile = get_object_or_404(ListenerProfile, user__username=username)
    playlist = get_object_or_404(Playlist, id=playlist_id, listenerprofile=listener_profile)
    track = get_object_or_404(Brano, id=track_id)

    # Supponiamo che tu abbia un metodo per aggiungere una traccia alla playlist
    if track not in playlist.tracks.all():
        playlist.tracks.add(track)
        playlist.save()

        # Aggiungi un messaggio di successo specificando in quale playlist è stata aggiunta la traccia
        messages.success(request, f"Track '{track.title}' has been added to playlist '{playlist.name}'.")

    else:
        messages.info(request, f"Track '{track.title}' is already in playlist '{playlist.name}'.")

    return redirect('public_artist_profile', username=track.artist.user.username)


from django.contrib.auth.decorators import login_required

# aggiunta di un brano all'album
@login_required
def add_brano_to_album(request, username, album_id):
    if request.user.username != username:
        return redirect('login')

    artist_profile = get_object_or_404(ArtistProfile, user__username=username)
    album = get_object_or_404(Album, pk=album_id, artist=artist_profile)

    if request.method == 'POST':
        form = BranoForm(request.POST, request.FILES, album=album)
        if form.is_valid():
            brano = form.save(commit=False)
            brano.album = album
            brano.artist = artist_profile  # Assumi che l'artista del brano sia l'artista dell'album
            if 'upload_mp3' not in request.POST:
                brano.mp3_file = None

            brano.save()
            return redirect('my_albums', username=username)
    else:
        form = BranoForm(album=album)

    return render(request, 'music/Brano/add_brano.html', {
        'form': form,
        'album': album,
        'artist': artist_profile
    })


from django.contrib.auth.decorators import login_required

# aggiunta di più brani insieme allìalbum con mutagen
@login_required
def add_multiple_brani(request, username, album_id):
    try:
        if request.user.username != username:
            messages.error(request, "You are not authorized to modify this album.")
            return redirect('login')

        artist_profile = get_object_or_404(ArtistProfile, user__username=username)
        album = get_object_or_404(Album, pk=album_id, artist=artist_profile)
        genres = Genre.objects.all()

        if request.method == 'POST':
            successfully_added = 0  # Counter for successfully added songs
            for i, file in enumerate(request.FILES.getlist('mp3_files')):
                try:
                    form_data = {
                        'title': request.POST.get(f'title_{i}'),
                        'track_index': request.POST.get(f'track_index_{i}'),
                        'side': request.POST.get(f'side_{i}'),
                        'duration': request.POST.get(f'duration_{i}')
                    }

                    if request.POST.get(f'upload_mp3_{i}') == 'true':
                        form = BranoForm(form_data, {'mp3_file': file}, album=album)
                    else:
                        form = BranoForm(form_data, album=album)

                    if form.is_valid():
                        brano = form.save(commit=False)
                        brano.album = album
                        brano.artist = artist_profile
                        brano.genre = album.genre  # Set the genre to match the album's genre
                        brano.save()
                        successfully_added += 1  # Increment the success counter
                    else:
                        messages.error(request, f"Error in the form for the song {i + 1}: {form.errors}")
                except (ValueError, IntegrityError) as e:
                    messages.error(request, f"Error while processing the song {i + 1}: {str(e)}")
                except Exception as e:
                    messages.error(request, f"Unexpected error loading songs: {str(e)}")

            # If at least one song was added successfully, show a success message
            if successfully_added > 0:
                messages.success(request,
                                 f"Successfully added {successfully_added} song(s) to the album '{album.title}'.")

            return redirect('my_albums', username=username)
        else:
            form = BranoForm(album=album)

        return render(request, 'music/Brano/add_multiple_brani.html', {
            'form': form,
            'album': album,
            'artist': artist_profile,
            'genres': genres
        })

    except Album.DoesNotExist:
        messages.error(request, "Album not found.")
        return redirect('home')
    except Exception as e:
        messages.error(request, "An error occurred during the operation.")
        return redirect('home')


from django.contrib.auth.decorators import login_required
from .models import Playlist

# aggiunta alla playlist
@login_required
def add_to_playlist(request, username, playlist_id, track_id):
    try:
        listener_profile = get_object_or_404(ListenerProfile, user__username=username)
        playlist = get_object_or_404(Playlist, id=playlist_id, listener=listener_profile)
        track = get_object_or_404(Brano, id=track_id)

        # Check if the track is already in the playlist
        if track in playlist.tracks.all():
            messages.info(request, 'Track is already in the playlist.')
            return redirect('public_artist_profile', username=track.artist.user.username)

        playlist.tracks.add(track)  # Aggiungi il brano alla playlist
        messages.success(request, 'Track added to playlist successfully!')
        return redirect('public_artist_profile', username=track.artist.user.username)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        messages.error(request, 'An error occurred while adding the track to the playlist.')
        return redirect('home')


from django.contrib.auth.decorators import login_required

# registrazione di un nuovo merch
@login_required
def register_merch(request, username):
    try:
        if request.user.username != username:
            messages.warning(request, "Access Denied: You cannot register merchandise for another user.")
            return redirect('login')

        artist_profile = get_object_or_404(ArtistProfile, user__username=username)

        if request.method == 'POST':
            form = MerchandiseForm(request.POST, request.FILES)
            if form.is_valid():
                merch = form.save(commit=False)
                merch.artist = artist_profile
                merch.save()
                messages.success(request, "Merchandise registered successfully.")
                return redirect('my_merch', username=username)
            else:
                messages.error(request, "Failed to register merchandise. Please check the form for errors.")
        else:
            form = MerchandiseForm()

        return render(request, 'music/register_merch.html', {
            'form': form,
            'artist_profile': artist_profile
        })
    except Exception as e:
        # Log the exception and provide a user-friendly error message
        logger.error(f"An error occurred: {e}")
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return redirect('home')


from django.contrib.auth.decorators import login_required

# creazione di un nuovo merch
@login_required
def create_merchandise(request, username):
    try:
        artist_profile = get_object_or_404(ArtistProfile, user__username=username)

        if request.method == 'POST':
            form = MerchandiseForm(request.POST, request.FILES)
            if form.is_valid():
                merch = form.save(commit=False)
                merch.artist = artist_profile  # Associate merchandise with artist
                merch.save()
                return redirect('my_merch', username=artist_profile.user.username)  # Redirect to merchandise list
        else:
            form = MerchandiseForm()

        return render(request, 'music/merchandise/create_merchandise.html', {
            'form': form,
            'artist_profile': artist_profile
        })
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')
