from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from music.models import Comment, GenreInteraction, ArtistProfile, Merchandise, ListenerProfile, Order, Follow

from django.core.paginator import Paginator

@login_required
def my_comments(request, username):
    user = get_object_or_404(User, username=username)
    comments = Comment.objects.filter(listener__user=user).order_by('-created_at')

    # Paginazione - 10 commenti per pagina
    paginator = Paginator(comments, 10)  # Cambia il numero di commenti per pagina se necessario
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user_profile': user,
        'comments': page_obj,  # Passa l'oggetto della pagina al template
        'page_obj': page_obj,  # Per gestire la paginazione nel template
    }
    return render(request, 'music/my_stuff/my_comments.html', context)

# mostra le interazioni dell'utente loggato con i vari generi nelle 3 modalità (ricordo che vengono aggiornate sempre tutte e 3, utente decide quale usare per il sistema di raccomandazione
@login_required
def my_interactions(request, username):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Utente not logged'}, status=401)

    # Recupera le interazioni per l'utente corrente
    interactions = GenreInteraction.objects.filter(user__username=username)

    # Dizionario per organizzare i dati per modalità
    interaction_data = {
        'Adventurer': sorted(interactions, key=lambda x: x.score_adventurer, reverse=True),
        'Seeker': sorted(interactions, key=lambda x: x.score_seeker, reverse=True),
        'Connoisseur': sorted(interactions, key=lambda x: x.score_connoisseur, reverse=True)
    }

    return render(request, 'music/my_stuff/my_interactions.html', {'interaction_data': interaction_data})


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, CustomPasswordChangeForm

# mostra all'artista il proprio merchandise
@login_required
def my_merch(request, username):
    if request.user.username != username:
        return redirect('login')

    artist_profile = get_object_or_404(ArtistProfile, user__username=username)
    merch_items = Merchandise.objects.filter(
        artist=artist_profile)  # Recupera gli articoli di merchandise per l'artista

    return render(request, 'music/my_stuff/my_merch.html', {
        'artist_profile': artist_profile,
        'merch_items': merch_items,
        'user': request.user
    })

# mostra all'artista i propri album per modificarli
@login_required
def my_albums(request, username):
    if request.user.username != username:
        return redirect('login')

    artist_profile = get_object_or_404(ArtistProfile, user__username=username)
    albums = artist_profile.albums.all()

    return render(request, 'music/my_stuff/my_albums.html', {
        'artist_profile': artist_profile,
        'albums': albums
    })

# mostra all'asoltatore le proprie playlisst
@login_required
def my_playlists(request, username):
    if request.user.username != username:
        return redirect('login')

    listener_profile = get_object_or_404(ListenerProfile, user__username=username)
    playlists = listener_profile.playlists.all().order_by(
        'title')  # Usa 'playlists' qui, corrispondente a related_name='playlists'

    return render(request, 'music/my_stuff/my_playlists.html', {
        'listener_profile': listener_profile,
        'playlists': playlists
    })


from django.contrib.auth.decorators import login_required
from .models import ListenerProfile

# mostra all'ascoltatore i propri ordini fatti
@login_required
def my_shopping(request, username):
    # Ottieni il profilo del listener tramite username
    listener_profile = get_object_or_404(ListenerProfile, user__username=username)

    # Verifica che l'utente loggato sia il proprietario del profilo
    if request.user != listener_profile.user:
        return redirect('home')  # Reindirizza alla home se l'utente non è autorizzato

    # Filtra gli ordini per il listener corrente
    orders = Order.objects.filter(buyer=listener_profile.user).order_by('-order_date')

    # Aggiungi la paginazione - 10 ordini per pagina
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'music/my_stuff/my_shopping.html', {
        'orders': page_obj,  # Passa l'oggetto della pagina
        'paginator': paginator,
        'page_obj': page_obj
    })

# mostra all'artista la lista dei suoi followers
def followers_list(request, username):
    user_followers = Follow.objects.filter(followed__user__username=username).select_related('follower__user')

    # Aggiungi il paginatore
    paginator = Paginator(user_followers, 20)  # 20 follower per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'music/vlog/followers_list.html', {'page_obj': page_obj})

# mostra all'artista tutte le vendite mai fatte
@login_required
def artist_orders(request, username):
    artist_profile = get_object_or_404(ArtistProfile, user__username=username)  # Ottieni il profilo dell'artista
    orders = Order.objects.filter(merchandise__artist=artist_profile).order_by(
        '-order_date')  # Filtra gli ordini relativi ai suoi prodotti

    # Paginazione - 10 ordini per pagina
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'music/profile/artist_orders.html', {
        'artist_profile': artist_profile,
        'page_obj': page_obj  # Passa l'oggetto della pagina al template
    })


from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Follow
