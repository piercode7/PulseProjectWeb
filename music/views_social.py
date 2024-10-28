import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Notification

logger = logging.getLogger(__name__)

# rappresenta il like verso un playlist per poterla vedere nella propria pagina comodamente
@login_required
def link_playlist(request, playlist_id):
    user = request.user
    playlist = get_object_or_404(Playlist, pk=playlist_id)

    if request.method == 'POST':
        if LikedPlaylist.objects.filter(user=user, playlist=playlist).exists():
            return JsonResponse({'message': 'Playlist already liked'}, status=400)
        else:
            LikedPlaylist.objects.create(user=user, playlist=playlist)

            # Crea una notifica per il proprietario della playlist se non è l'utente che ha messo like
            if playlist.listener.user != user:
                Notification.objects.create(
                    user=playlist.listener.user,  # Il destinatario della notifica è il proprietario della playlist
                    notification_type='like_playlist',
                    message=f'{user.username} liked your playlist "{playlist.title}"'
                )

            return JsonResponse({'message': 'Playlist liked'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)


from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import LikedPlaylist

# smettere di seguire una certa playlist
@login_required
@require_POST
def unlink_playlist(request, playlist_id):
    user = request.user
    playlist = get_object_or_404(Playlist, pk=playlist_id)

    liked_playlist = LikedPlaylist.objects.filter(user=user, playlist=playlist).first()
    if liked_playlist:
        liked_playlist.delete()
        return JsonResponse({'message': 'Playlist unliked successfully'}, status=200)
    else:
        return JsonResponse({'error': 'You have not liked this playlist'}, status=400)


from django.contrib.auth.decorators import login_required

# follow da ascoltatore a artista
@login_required
def follow_artist(request, username):
    artist_to_follow = get_object_or_404(ArtistProfile, user__username=username)

    Follow.objects.get_or_create(follower=request.user.listenerprofile, followed=artist_to_follow)
    return redirect('public_artist_profile', username=username)

# unfollow da ascoltatore ad artista
@login_required
def unfollow_artist(request, username):
    artist_to_unfollow = get_object_or_404(ArtistProfile, user__username=username)

    Follow.objects.filter(follower=request.user.listenerprofile, followed=artist_to_unfollow).delete()
    return redirect('public_artist_profile', username=username)


# errore generico
def error_page(request):
    return render(request, 'music/error_page.html', {'message': 'You are not authorized to access this page.'})

# lista artisti seguiti ma non utilizzata per ora
def following_list(request, username):
    user_following = Follow.objects.filter(follower__user__username=username).values_list('followed__user__username',
                                                                                          flat=True)
    return render(request, 'music/vlog/following_list.html', {'user_following': user_following})


from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Album, ArtistProfile, Playlist
from .forms import CommentForm

@login_required
def artist_discussion(request, username):
    try:
        artist = get_object_or_404(ArtistProfile, user__username=username)

        # Recupera il parametro di ordinamento e di filtro per album dalla richiesta GET
        sort_by = request.GET.get('sort_by', 'recent')
        album_id = request.GET.get('album_id', None)

        # Applica il filtro per album se presente
        comments = Comment.objects.filter(artist=artist, parent__isnull=True)
        if album_id:
            comments = comments.filter(album__id=album_id)

        # Applica l'ordinamento in base al parametro
        if sort_by == 'filotto':
            comments = comments.annotate(filotto_length=Count('replies') + 1).order_by('-filotto_length', '-created_at')
        else:  # Ordinamento predefinito per recentità
            comments = comments.order_by('-created_at')

        listener = None
        if request.user.is_authenticated and hasattr(request.user, 'listenerprofile'):
            listener = request.user.listenerprofile

        if request.method == 'POST':
            if listener:
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.listener = listener
                    comment.artist = artist
                    comment.save()
                    messages.success(request, "Comment posted successfully.")
                    return redirect('artist_discussion', username=artist.user.username)
                else:
                    messages.error(request, "Failed to post comment. Please check the form for errors.")
            else:
                messages.warning(request, "You must be logged in as a listener to post a comment.")
                return redirect('login')
        else:
            form = CommentForm()

        # Filtra gli album per l'artista
        albums = Album.objects.filter(artist=artist)

        form.fields['album'].queryset = albums

        return render(request, 'music/vlog/artist_discussion.html', {
            'artist': artist,
            'comments': comments,
            'form': form,
            'albums': albums,  # Passa gli album al template
            'selected_album': album_id  # Passa l'album selezionato al template
        })
    except Exception as e:
        # Log the exception e fornisci un messaggio di errore amichevole per l'utente
        logger.error(f"An error occurred: {e}")
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return redirect('home')






# follow artista
@login_required
def follow_artist(request, username):
    try:
        artist = get_object_or_404(ArtistProfile, user__username=username)
        listener = request.user.listenerprofile

        # Controlla se la relazione di follow esiste già per evitare duplicati
        follow, created = Follow.objects.get_or_create(follower=listener, followed=artist)

        if created:
            messages.success(request, f"You are now following {artist.user.username}!")
        else:
            messages.info(request, f"You are already following {artist.user.username}!")

        return redirect('public_artist_profile', username=username)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')

# unfollow artista
@login_required
def unfollow_artist(request, username):
    try:
        artist = get_object_or_404(ArtistProfile, user__username=username)
        listener = request.user.listenerprofile
        follow = get_object_or_404(Follow, follower=listener, followed=artist)
        follow.delete()
        messages.success(request, f"You are no longer following {artist.user.username}!")
        return redirect('public_artist_profile', username=username)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')


from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, Follow

# notifica creata se qualcuno inizia a seguirti
@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        try:
            listener_name = instance.follower.user.username
            listener_url = reverse("public_listener_artists", args=[listener_name])
            notification_message = f'<a href="{listener_url}">{listener_name}</a> started following you.'

            Notification.objects.create(
                user=instance.followed.user,  # l'artista che viene seguito
                notification_type='follow',
                message=notification_message
            )
        except Exception as e:
            logger.error(f"An error occurred: {e}")

# notifica se qualcuno commenta nella discussione
@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        try:
            commenter = instance.listener.user.username
            commenter_url = reverse("public_listener_artists", args=[commenter])
            comment_text = (instance.content[:50] + '...') if len(instance.content) > 10 else instance.content

            # Controlla se il commento è associato a un album
            if instance.album:
                album_title = instance.album.title
                notification_message = f'<a href="{commenter_url}">{commenter}</a> commented l\'album "{album_title}": "{comment_text}"'
            else:
                notification_message = f'<a href="{commenter_url}">{commenter}</a> commented: "{comment_text}"'

            Notification.objects.create(
                user=instance.artist.user,  # Notifica all'artista associato
                notification_type='comment',
                message=notification_message
            )
        except Exception as e:
            logger.error(f"An error occurred: {e}")


from django.contrib.auth.decorators import login_required

# mostra tutte le notifiche
@login_required
def notification_center(request):
    try:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
        return render(request, 'music/vlog/notifications.html', {'notifications': notifications})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')

# marca una notifica come letta
@login_required
def mark_notification_as_read(request, notification_id):
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return redirect('notification_center')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')
