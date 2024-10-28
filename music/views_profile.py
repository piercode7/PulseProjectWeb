import logging
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .forms import ProfileCreationForm
from .models import LikedPlaylist, Playlist, ListenerProfile, Follow, Merchandise, ArtistProfile, Album, Notification

logger = logging.getLogger(__name__)
from django.urls import reverse

# view per scegliere che tipo di profilo diventare all'inizio
@login_required
def choose_profile_type(request):
    try:
        if request.method == 'POST':
            form = ProfileCreationForm(request.POST)
            if form.is_valid():
                profile_type = form.cleaned_data['profile_type']
                if profile_type == 'artist':
                    return redirect('create_artist_profile')
                elif profile_type == 'listener':
                    return redirect('create_listener_profile')
                else:
                    messages.error(request, "Not Valid profile type. Try again.")
                    return redirect('choose_profile_type')
            else:
                messages.error(request, "Not valid form. Try again.")
        else:
            form = ProfileCreationForm()

        return render(request, 'choose_profile_type.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in choosing the profile type: {e}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('home')

# creazione profilo artista
@login_required
def create_artist_profile(request):
    try:
        if request.method == 'POST':
            artist_form = ArtistProfileForm(request.POST, request.FILES)
            if artist_form.is_valid():
                artist_profile = artist_form.save(commit=False)
                artist_profile.user = request.user
                artist_profile.save()
                messages.success(request, "Artist profile successfully created.")
                return redirect('private_artist_profile', username=request.user.username)
            else:
                messages.error(request, "Error creating artist profile. Correct the errors below.")
        else:
            artist_form = ArtistProfileForm()

        return render(request, 'create_artist_profile.html', {'artist_form': artist_form})
    except Exception as e:
        logger.error(f"Error creating artist profile: {e}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('home')

# creazione profilo asoltatore
@login_required
def create_listener_profile(request):
    try:
        storage = messages.get_messages(request)
        storage.used = True

        if request.method == 'POST':
            listener_form = ListenerProfileForm(request.POST, request.FILES)
            if listener_form.is_valid():
                listener_profile = listener_form.save(commit=False)
                listener_profile.user = request.user
                listener_profile.save()
                messages.success(request, "Listener profile successfully created.")
                return redirect('private_listener_profile', username=request.user.username)
            else:
                logger.warning("Form non valido: %s", listener_form.errors)
                messages.error(request, "Error creating listener profile. Correct the errors below.")
        else:
            listener_form = ListenerProfileForm()

        return render(request, 'create_listener_profile.html', {'listener_form': listener_form})
    except Exception as e:
        logger.error(f"Error creating listener profile: {e}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('home')

# in base al profilo scelto si viene reindirizzato in modo sicuro altrimenti se account esiste ma il profilo ancora no si va alla scelta del profilo
@login_required
def profile_redirect(request, username):
    user = request.user
    if hasattr(user, 'artistprofile'):
        return redirect('private_artist_profile', username=username)
    elif hasattr(user, 'listenerprofile'):
        return redirect('private_listener_profile', username=username)
    else:
        # Gestisci i casi in cui l'utente non ha un profilo
        messages.error(request, "No profiles found for this user. Create a profile first.")
        return redirect('choose_profile_type')

# mostra il proprio profilo per editarlo (anche qui reindirizzamento intelligente), altriment home
@login_required
def my_profile(request):
    try:
        user = request.user
        if ArtistProfile.objects.filter(user=user).exists():
            return redirect('private_artist_profile', username=user.username)
        elif ListenerProfile.objects.filter(user=user).exists():
            return redirect('private_listener_profile', username=user.username)
        else:
            messages.warning(request, "No profiles were found. Create one first.")
            return redirect('choose_profile_type')
    except Exception as e:
        logger.error(f"Error logging in to profile: {e}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('home')

# stesso reindirizzamento ma per la parte pubblica del profilo
@login_required
def my_page(request):
    user = request.user
    if ArtistProfile.objects.filter(user=user).exists():
        return redirect('public_artist_profile', username=user.username)
    elif ListenerProfile.objects.filter(user=user).exists():
        return redirect('public_listener_artists', username=user.username)
    else:
        return redirect('choose_profile_type')


from .forms import ListenerProfileForm
from django.contrib.auth.decorators import login_required
from .forms import ArtistProfileForm

# si va nella sezione privata del profilo artista per editare i contenuti
@login_required
def private_artist_profile(request, username):
    if request.user.username != username:
        return redirect('login')
    artist_profile = get_object_or_404(ArtistProfile, user__username=username)
    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES, instance=artist_profile)
        if form.is_valid():
            form.save()
            return redirect('public_artist_profile', username=username)
    else:
        form = ArtistProfileForm(instance=artist_profile)
    albums = artist_profile.albums.all()
    return render(request, 'music/profile/private_artist_profile.html', {
        'form': form,
        'albums': albums,
        'user': request.user,
        'artist_profile': artist_profile
    })

# si va nella sezione privata dell'ascoltatore per editarlo
@login_required
def private_listener_profile(request, username):
    if request.user.username != username:
        return redirect('login')

    listener_profile = get_object_or_404(ListenerProfile, user__username=username)
    if request.method == 'POST':
        form = ListenerProfileForm(request.POST, request.FILES, instance=listener_profile)
        if form.is_valid():
            form.save()
            return redirect('public_listener_artists', username=username)
    else:
        form = ListenerProfileForm(instance=listener_profile)

    return render(request, 'music/profile/private_listener_profile.html', {
        'form': form,
        'user': request.user
    })





from django.contrib.auth.decorators import login_required

# toggle per gestire il booleano che mostra o non mostra un album nella pagina pubblica in base che sia pubblicato o meno
@login_required
def toggle_album_published(request, username, album_id):
    try:
        artist_profile = get_object_or_404(ArtistProfile, user__username=username)

        # Assicurati che solo l'artista stesso o un amministratore possa modificare lo stato
        if request.user != artist_profile.user:
            messages.error(request, "You do not have permission to edit this album.")
            return redirect('my_albums', username=username)

        album = get_object_or_404(Album, id=album_id, artist=artist_profile)

        # Controlla lo stato corrente prima di modificarlo
        was_published = album.published

        # Cambia lo stato di 'published'
        album.published = not album.published
        album.save()

        # Se lo stato cambia da False a True, invia notifiche ai follower
        if not was_published and album.published:
            followers = Follow.objects.filter(followed=artist_profile)
            for follow in followers:
                follower_user = follow.follower.user
                artist_name = artist_profile.user.username
                artist_url = reverse("public_artist_profile", args=[artist_name])
                notification_message = f'<a href="{artist_url}">{artist_name}</a> just released the album: "{album.title}".'

                Notification.objects.create(
                    user=follower_user,
                    notification_type='album_release',
                    message=notification_message
                )

        messages.success(request, "Album status updated successfully.")
        return redirect('my_albums', username=username)

    except Album.DoesNotExist:
        messages.error(request, "The specified album does not exist.")
        return redirect('my_albums', username=username)
    except Exception as e:
        logger.error(f"Error changing album status: {e}")
        messages.error(request, "SAn unexpected error occurred. Please try again.")
        return redirect('my_albums', username=username)


from django.contrib.auth.decorators import login_required

# pagina pubblica dell'artista
@login_required
def public_artist_profile(request, username):
    try:
        artist = get_object_or_404(ArtistProfile, user__username=username)
        albums = Album.objects.filter(artist=artist, published=True).order_by('title').prefetch_related('brani')

        # Verifica se l'utente autenticato sta seguendo l'artista
        is_following = False
        if request.user.is_authenticated and hasattr(request.user, 'listenerprofile'):
            is_following = Follow.objects.filter(follower=request.user.listenerprofile, followed=artist).exists()

        # Calcola il numero di follower
        follower_count = Follow.objects.filter(followed=artist).count()

        return render(request, 'music/profile/public_artist_profile.html', {
            'artist': artist,
            'albums': albums,
            'is_following': is_following,
            'follower_count': follower_count,
        })
    except Exception as e:
        messages.error(request, "An error occurred while loading the artist's profile.")
        return redirect('home')


from django.shortcuts import redirect

from django.contrib import messages

# pagina pubblica dell'artista che mostra il suo merch
@login_required
def public_artist_merch(request, username):
    artist = get_object_or_404(ArtistProfile, user__username=username)
    merchs = Merchandise.objects.filter(artist=artist)

    is_following = False
    if request.user.is_authenticated and hasattr(request.user, 'listenerprofile'):
        is_following = Follow.objects.filter(follower=request.user.listenerprofile, followed=artist).exists()

    follower_count = Follow.objects.filter(followed=artist).count()

    return render(request, 'music/profile/public_artist_merchs.html', {
        'artist': artist,
        'merchs': merchs,
        'is_following': is_following,
        'follower_count': follower_count,  # Passa il conteggio dei follower al template

    })

# mostra gli artisti seguiti dall'ascoltatore
@login_required
def public_listener_artists(request, username):
    listener = get_object_or_404(ListenerProfile, user__username=username)
    followed_artists = Follow.objects.filter(follower=listener).order_by('followed__name')

    # Pagination
    paginator = Paginator(followed_artists, 30)  # Show 30 artists per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'music/profile/public_listener_artists.html', {
        'listener': listener,
        'page_obj': page_obj,
    })


from django.contrib.auth.decorators import login_required

# mostra le playlist dell'ascoltatore e quelle piaciute pubblicamente
@login_required
def public_listener_playlists(request, username):
    listener = get_object_or_404(ListenerProfile, user__username=username)

    # Paginazione per le playlist create dall'utente
    playlists = Playlist.objects.filter(listener=listener).order_by('title')
    paginator_playlists = Paginator(playlists, 5)  # Visualizza 5 playlist per pagina
    page_number_playlists = request.GET.get('page_playlists')
    page_obj_playlists = paginator_playlists.get_page(page_number_playlists)

    # Paginazione per le playlist piaciute dall'utente
    liked_playlists = LikedPlaylist.objects.filter(user=listener.user).select_related('playlist')
    paginator_liked_playlists = Paginator(liked_playlists, 5)  # Visualizza 5 playlist piaciute per pagina
    page_number_liked_playlists = request.GET.get('page_liked_playlists')
    page_obj_liked_playlists = paginator_liked_playlists.get_page(page_number_liked_playlists)

    # Controlla se l'utente loggato ha messo like su ogni playlist
    liked_playlists_by_user = LikedPlaylist.objects.filter(user=request.user).values_list('playlist_id', flat=True)

    return render(request, 'music/profile/public_listener_playlists.html', {
        'listener': listener,
        'page_obj_playlists': page_obj_playlists,
        'page_obj_liked_playlists': page_obj_liked_playlists,
        'liked_playlists_by_user': liked_playlists_by_user,  # Passa le playlist che l'utente ha già piaciuto
    })
