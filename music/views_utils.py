from django.conf import settings


def csrf_failure(request, reason=""):
    return redirect(settings.LOGIN_URL)




from django.shortcuts import redirect

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


# aumenta il counter di riproduzioni di ogni brano se ascoltato per 30 secondi non stop
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Brano

@login_required
@require_POST
def increment_play_count(request):
    if hasattr(request.user, 'artistprofile'):
        # Se l'utente è un artista, non deve poter incrementare il conteggio
        return JsonResponse({"message": "Artists cannot increment play count."}, status=403)

    try:
        data = json.loads(request.body)
        track_id = data.get('trackId')
        if not track_id:
            return JsonResponse({"message": "Track ID is missing."}, status=400)

        brano = Brano.objects.get(id=track_id)
        brano.play_count += 1
        brano.save()
        print("Incremento play count brano avvenuto")
        return JsonResponse({"message": "Play count incremented successfully."})

    except Brano.DoesNotExist:
        return JsonResponse({"message": "Track not found."}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)


from django.contrib.auth.decorators import login_required


# mostra l'album cover
@login_required
def show_album_cover(request, username, album_id):
    # Assicurati che l'artista corrisponda all'username
    artist = get_object_or_404(ArtistProfile, user__username=username)
    # Recupera l'album specifico con quel particolare ID
    album = get_object_or_404(Album, id=album_id, artist=artist)

    # Passa l'album al template
    return render(request, 'music/show_album_cover.html', {'album': album})


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render


# mostra una playlist completa
@login_required
def view_playlist(request, username, playlist_id):
    # Recupera la playlist usando l'id e l'username del proprietario
    playlist = get_object_or_404(Playlist, id=playlist_id, listener__user__username=username)
    # Recupera i brani associati alla playlist
    tracks = playlist.tracks.all()
    # Verifica se l'utente loggato è il proprietario della playlist
    is_owner = request.user.username == username

    return render(request, 'music/view_playlist.html', {
        'playlist': playlist,
        'tracks': tracks,
        'is_owner': is_owner,
    })


@login_required
def choose_playlist(request, username, track_id):
    listener_profile = get_object_or_404(ListenerProfile, user__username=username)
    track = get_object_or_404(Brano, id=track_id)
    playlists = listener_profile.playlists.all()  # Usa 'playlists' qui

    return render(request, 'music/choose_playlist.html', {
        'listener_profile': listener_profile,
        'track': track,
        'playlists': playlists
    })


import logging

logger = logging.getLogger(__name__)

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Genre, ListenerProfile, ArtistProfile, Album, Playlist, GenreInteraction, Follow
from .templatetags.genresdict import get_related_genres


# si attiva insieme all'aggiornamento del counter anche qui dopo 30 secondi di ascolto non stop
# modifica i parametri di ascolto dell'ascoltatore usando un dizionario ben preciso per favorire il genere interessato
# ed eventuali altri generi più o meno coinvolti in base alla modalità
@csrf_exempt
@login_required
@require_POST
def update_interactions(request, username):
    try:
        # Verifica se l'utente è autenticato
        if not request.user.is_authenticated:
            return JsonResponse({'message': 'User is not authorized.'}, status=401)

        # Verifica se l'utente ha un profilo di tipo listener
        if not hasattr(request.user, 'listenerprofile'):
            return JsonResponse({'message': 'User is not a listener.'}, status=403)

        data = json.loads(request.body.decode('utf-8'))
        track_genre_name = data.get('trackGenre')

        try:
            genre = Genre.objects.get(name=track_genre_name)
        except Genre.DoesNotExist:
            # Se il genere non è trovato, ignora e continua
            return JsonResponse({'message': 'Genre not found: ignored and continued with others'}, status=404)

        # Itera su tutte le modalità di ascolto
        for listening_mode in ['adventurer', 'seeker', 'connoisseur']:
            related_genres = get_related_genres(genre.name, listening_mode)
            update_genre_scores(request.user, genre, related_genres, listening_mode)
        print("Interazione generi applicata correttamente")
        return JsonResponse({'message': 'Genre interactions updated successfully'})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({'message': 'An unexpected error occurred. Please try again later.'}, status=500)


# agisce in azione con update_interaction
def update_genre_scores(user, genre, related_genres, listening_mode):
    try:
        # Determina il campo di punteggio in base alla modalità di ascolto
        score_field = f'score_{listening_mode}'

        # Aggiorna i punteggi per il genere principale e i generi correlati
        for related_genre_name, additional_score in related_genres.items():
            try:
                related_genre, _ = Genre.objects.get_or_create(name=related_genre_name)
                related_interaction, _ = GenreInteraction.objects.get_or_create(user=user, genre=related_genre)

                current_related_score = getattr(related_interaction, score_field)
                setattr(related_interaction, score_field, current_related_score + additional_score)
                related_interaction.save()
            except Genre.DoesNotExist:
                # Ignora il genere se non viene trovato
                continue
    except Exception as e:
        logger.error(f"An error occurred: {e}")


from django.http import JsonResponse
from .models import Brano



from django.contrib.auth.decorators import login_required

# mostra un album da solo per ascoltare
@login_required
def view_album(request, username, album_id):
    artist = get_object_or_404(ArtistProfile, user__username=username)
    album = get_object_or_404(Album, id=album_id, artist=artist)

    # Check if the user is following the artist
    is_following = False
    if request.user.is_authenticated and hasattr(request.user, 'listenerprofile'):
        is_following = Follow.objects.filter(follower=request.user.listenerprofile, followed=artist).exists()

    return render(request, 'music/album/view_album.html', {
        'artist': artist,
        'album': album,
        'is_following': is_following,
    })
