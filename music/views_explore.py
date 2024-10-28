import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404

logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required

from .models import ArtistProfile, ListenerProfile, Brano, Album, Genre, GenreInteraction

# ricerca artisti per caratteri
def search_artist(request):
    if request.method == 'POST':
        form = ArtistSearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            results = ArtistProfile.objects.filter(name__icontains=search_term)
            return render(request, 'music/search/search_results.html', {'form': form, 'results': results})
    else:
        form = ArtistSearchForm()

    return render(request, 'music/search/artist_search.html', {'form': form})

# ricerca ascoltatori per caratteri
@login_required
def search_listener(request):
    try:
        if request.method == 'POST':
            form = ListenerSearchForm(request.POST)
            if form.is_valid():
                search_term = form.cleaned_data['search_term']
                results = ListenerProfile.objects.filter(user__username__icontains=search_term)
                return render(request, 'music/search/search_results.html', {'form': form, 'results': results})
            else:
                messages.error(request, "Invalid search term. Try again.")
        else:
            form = ListenerSearchForm()

        return render(request, 'music/listener_search.html', {'form': form})
    except Exception as e:
        logger.error(f"Error searching for listeners: {e}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('home')


from .forms import ArtistSearchForm, ListenerSearchForm

# ricerca generale di un po tutti i contenuti
def search_profiles(request):
    search_form = SearchForm()
    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_term = search_form.cleaned_data['search_term']
            if 'artist_search' in request.POST:
                return redirect('artist_results', search_term=search_term)
            elif 'listener_search' in request.POST:
                return redirect('listener_results', search_term=search_term)
            elif 'album_search' in request.POST:  # Add this condition
                return redirect('album_results', search_term=search_term)
            elif 'song_search' in request.POST:  # Add this condition
                return redirect('song_results', search_term=search_term)
    return render(request, 'music/search/search_profiles.html', {'search_form': search_form})

# risultati canzoni in ordine di ascolti
def song_results(request, search_term):
    # Filtra i brani in base al termine di ricerca
    song_results = Brano.objects.filter(title__icontains=search_term)

    # Controlla l'ordine specificato dall'utente
    order_by = request.GET.get('order_by', 'play_count')  # Ordina per play count di default
    if order_by == 'play_count':
        # Ordina in base a 'play_count' in ordine decrescente
        song_results = song_results.order_by('-play_count')
    else:
        # Ordina in base al titolo in ordine alfabetico
        song_results = song_results.order_by('title')

    # Limita i risultati a un massimo di 100
    song_results = song_results[:100]

    # Imposta il paginatore per mostrare 20 risultati per pagina
    paginator = Paginator(song_results, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'music/search/song_search_results.html', {
        'results': page_obj,
        'search_term': search_term,
        'order_by': order_by,
        'page_obj': page_obj,
    })


from .forms import SearchForm

# risultati artisti in ordine di popolarità
def artist_results(request, search_term):
    # Filtra e annota i profili degli artisti con il numero di follower
    artist_results = ArtistProfile.objects.filter(name__icontains=search_term).annotate(
        follower_count=Count('followers'))

    # Controlla l'ordine specificato dall'utente
    order_by = request.GET.get('order_by', 'follower_count')  # Ordina di default per numero di follower
    if order_by == 'name':
        artist_results = artist_results.order_by('name')
    else:
        artist_results = artist_results.order_by('-follower_count')

    # Limita i risultati a 100
    artist_results = artist_results[:100]

    # Impaginazione
    paginator = Paginator(artist_results, 10)  # 10 risultati per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'music/search/artist_search_results.html', {
        'results': page_obj,
        'search_term': search_term,
        'order_by': order_by,
        'paginator': paginator,
        'page_obj': page_obj,
    })

# risultati album in ordini selezionabili
def album_results(request, search_term):
    # Filtra gli album in base al termine di ricerca
    album_results = Album.objects.filter(title__icontains=search_term)[:100]  # Limita i risultati a 100

    # Ordina in base alla richiesta dell'utente
    order_by = request.GET.get('order_by', 'title')  # Ordina per titolo di default
    if order_by == 'release_date':
        album_results = sorted(album_results, key=lambda x: x.release_date, reverse=True)
    else:
        album_results = sorted(album_results, key=lambda x: x.title)

    # Paginazione
    paginator = Paginator(album_results, 10)  # Mostra 10 risultati per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'music/search/album_search_results.html', {
        'results': page_obj,
        'search_term': search_term,
        'order_by': order_by,
        'paginator': paginator,
        'page_obj': page_obj,
    })


from django.contrib.auth.decorators import login_required

# risultati ascoltatori semplice
@login_required
def listener_results(request, search_term):
    # Filtra i listener, ordina alfabeticamente e limita a 100 risultati
    listener_results = ListenerProfile.objects.filter(user__username__icontains=search_term).order_by('user__username')[
                       :100]

    # Impaginazione, 20 risultati per pagina
    paginator = Paginator(listener_results, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'music/listener_search_results.html', {
        'page_obj': page_obj,
        'search_term': search_term,
    })


import logging
import random
import numpy as np
from django.contrib.auth.decorators import login_required

# Configura il logger
logger = logging.getLogger(__name__)

# view per offrire all'ascoltatore contenuti nuovi in base alle sue interazioni musicali. La view guarda le interazioni dell'utente loggato e propone
# musica in base alla modalità attiva dell'utente contenuti più o meno inclusivi
@login_required
def explore_view(request):
    try:
        user = request.user
        if hasattr(user, 'artistprofile'):
            messages.warning(request,
                             "Access Denied: This section is reserved for listener profiles. Please log in with a listener profile.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        listener_profile = user.listenerprofile
        current_mode = listener_profile.listening_mode

        # Recupera le interazioni con i generi per l'utente loggato
        interactions = GenreInteraction.objects.filter(user=user)

        selected_tracks = []

        if interactions.exists():
            genre_scores = {}

            if current_mode == 'adventurer':
                # In modalità "adventurer", scegli i brani casualmente indipendentemente dal genere
                all_tracks = Brano.objects.select_related('artist', 'album').all()
                album_ids = set()
                unique_tracks = []
                for track in all_tracks:
                    if track.album_id not in album_ids:
                        unique_tracks.append(track)
                        album_ids.add(track.album_id)
                selected_tracks = random.sample(unique_tracks, min(10, len(unique_tracks)))

            elif current_mode == 'seeker':
                genre_scores = {interaction.genre.name: interaction.score_seeker for interaction in interactions}
                top_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:6]
                top_genre_names = [genre[0] for genre in top_genres]
                tracks = Brano.objects.filter(genre__name__in=top_genre_names).select_related('artist', 'album')

            elif current_mode == 'connoisseur':
                genre_scores = {interaction.genre.name: interaction.score_connoisseur for interaction in interactions}
                top_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                top_genre_names = [genre[0] for genre in top_genres]
                tracks = Brano.objects.filter(genre__name__in=top_genre_names).select_related('artist', 'album')

            # Per le modalità "seeker" e "connoisseur"
            if current_mode in ['seeker', 'connoisseur'] and genre_scores:
                tracks_with_weights = []
                for track in tracks:
                    track_genre = track.genre.name
                    if track_genre in genre_scores:
                        track_weight = genre_scores[track_genre]
                        tracks_with_weights.append((track, track_weight))

                if tracks_with_weights:
                    album_ids = set()
                    filtered_tracks_with_weights = []
                    for track, weight in tracks_with_weights:
                        if track.album_id not in album_ids:
                            filtered_tracks_with_weights.append((track, weight))
                            album_ids.add(track.album_id)

                    if filtered_tracks_with_weights:  # Assicura che ci siano brani filtrati
                        all_tracks, weights = zip(*filtered_tracks_with_weights)
                        weights = np.array(weights)

                        # Verifica se ci sono elementi e se esiste almeno un valore positivo
                        if weights.size > 0 and np.any(weights > 0):
                            probabilities = weights / weights.sum()
                            selected_tracks = np.random.choice(all_tracks, size=min(10, len(all_tracks)), replace=False,
                                                               p=probabilities)
                        else:
                            selected_tracks = random.sample(list(all_tracks), min(len(all_tracks), 10))
                    else:
                        selected_tracks = random.sample(list(Brano.objects.select_related('artist', 'album').all()), 10)
                else:
                    selected_tracks = random.sample(list(Brano.objects.select_related('artist', 'album').all()), 10)

        else:
            # Se non ci sono interazioni registrate, seleziona brani casuali senza ripetere album
            all_tracks = Brano.objects.select_related('artist', 'album').all()
            album_ids = set()
            unique_tracks = []
            for track in all_tracks:
                if track.album_id not in album_ids:
                    unique_tracks.append(track)
                    album_ids.add(track.album_id)
            selected_tracks = random.sample(unique_tracks, min(10, len(unique_tracks)))

        return render(request, 'music/search/explore.html', {'combined_content': list(selected_tracks)})

    except Exception as e:
        # Log the exception e fornisce un messaggio di errore user-friendly
        logger.error(f"An error occurred: {e}")
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return redirect('home')

# view che mostra la lista di generi
def genre_list(request):
    genres = Genre.objects.all()  # Recupera tutti i generi dal database
    return render(request, 'music/vlog/genrelist.html', {'genres': genres})

# view che mostra per il genere selezionato i migliori artisti dello stesso (top 20) e alcuni dei loro album casuali
def genre_area(request, genre_id):
    genre = get_object_or_404(Genre, pk=genre_id)

    # Recupera i 30 artisti con più followers che hanno almeno un album nel genere selezionato
    artists = ArtistProfile.objects.filter(albums__genre=genre).annotate(
        num_followers=Count('followers')).order_by('-num_followers')[:20]

    # Recupera gli album associati ai 30 artisti più popolari selezionati, in ordine casuale
    albums = Album.objects.filter(genre=genre, artist__in=artists).select_related('artist').order_by('?')[:30]

    return render(request, 'music/vlog/genre_area.html', {'genre': genre, 'artists': artists, 'albums': albums})
