def home(request):
    return render(request, 'home.html')


from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm


# registrazione iniziale dell'account (non profilo, account)
def register_account(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect('choose_profile_type')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from music.models import ArtistProfile, ListenerProfile


# dopo aver effettuato il login si viene indirizzato in modo intelligente
@login_required
def post_login_redirect(request):
    user = request.user
    if ListenerProfile.objects.filter(user=user).exists():
        return redirect('private_listener_profile', username=user.username)
    elif ArtistProfile.objects.filter(user=user).exists():
        return redirect('private_artist_profile', username=user.username)
    else:
        # Se nessun profilo esiste, reindirizza alla pagina di creazione del profilo
        return redirect('choose_profile_type')


from django.conf import settings
from django.shortcuts import redirect


# fallimento csrf
def csrf_failure(request, reason=""):
    return redirect(settings.LOGIN_URL)
