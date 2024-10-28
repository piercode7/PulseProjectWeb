import logging

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from music.forms import UserUpdateForm, CustomPasswordChangeForm

logger = logging.getLogger(__name__)

from django.contrib import messages

# view per mostrare le opzioni relative al proprio account (uguale per i due tipi di user)
@login_required
def my_account(request, username):
    try:
        if request.user.username != username:
            return redirect('login')

        user = request.user
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, instance=user)
            password_form = CustomPasswordChangeForm(user, request.POST)

            if user_form.is_valid():
                user_form.save()
                return redirect('my_account', username=user.username)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Mantieni l'utente loggato dopo il cambio password
                return redirect('my_account', username=user.username)
        else:
            user_form = UserUpdateForm(instance=user)
            password_form = CustomPasswordChangeForm(user)

        # Determina il tipo di profilo e l'URL di reindirizzamento
        if hasattr(user, 'artistprofile'):
            back_url = 'private_artist_profile'
        else:
            back_url = 'private_listener_profile'

        return render(request, 'music/account/my_account.html', {
            'user_form': user_form,
            'password_form': password_form,
            'back_url': back_url,
            'username': user.username,  # Passa il nome utente per l'URL
        })
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')


from django.http import HttpResponse

# view utilizzata per testare il servizio di invio automatico della mail
def send_test_email(request, username):
    user = get_object_or_404(User, username=username)  # Recupera l'utente in base al nome utente
    send_mail(
        'Test Email',
        'This is a test email sent from Django using SendGrid.',
        'pulsemusicinc24@gmail.com',
        [user.email],  # Invia l'email all'email associata all'utente
        fail_silently=False,
    )
    return HttpResponse('Test email sent successfully!')


from django.contrib.auth.decorators import login_required

# cambiare email dell'account
@login_required
def start_email_change(request, username):
    try:
        if request.method == 'POST':
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                # Generate token and uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                confirmation_url = request.build_absolute_uri(
                    reverse('confirm_email_change', kwargs={'uidb64': uid, 'token': token})
                ).rstrip('"')  # Rimuove eventuali virgolette doppie alla fine del link

                # Verifica il link stampando l'URL
                print("Confirmation URL:", confirmation_url)

                # Render email content from template
                context = {
                    'user': user,
                    'protocol': 'https' if request.is_secure() else 'http',
                    'domain': request.get_host(),
                    'uid': uid,
                    'token': token,
                }
                email_body = render_to_string('music/account/confirm_email_change.html', context)

                print(email_body)

                # Send the email
                send_mail(
                    'Confirm your email change',
                    email_body,
                    'pulsemusicinc24@gmail.com',
                    [user.email],
                    fail_silently=False,
                )
                return redirect('my_account', username=request.user.username)
            else:
                messages.error(request, 'Password is incorrect.')
        return render(request, 'music/account/start_email_change.html')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')


from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth.decorators import login_required

# conferma per cambiare email utente
def confirm_email_change(request, uidb64, token):
    try:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_email = request.POST.get('new_email')
                if new_email:
                    user.email = new_email
                    user.save()
                    messages.success(request, 'Your email address has been successfully updated!')
                    return redirect('my_account', username=user.username)
                else:
                    messages.error(request, 'Please enter a valid email address.')
            return render(request, 'music/account/edit_email.html', {'user': user})
        else:
            return redirect('home')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')


from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
import logging

# Configura il logger
logger = logging.getLogger(__name__)

User = get_user_model()

# richiesta di eliminazione account
@login_required
def request_account_deletion(request):
    try:
        if request.method == 'POST':
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                # Genera token e uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                confirmation_url = request.build_absolute_uri(
                    reverse('confirm_account_deletion', kwargs={'uidb64': uid, 'token': token})
                ).rstrip('"')  # Rimuove eventuali virgolette doppie alla fine del link

                # Debug: verifica il link stampando l'URL
                print("Confirmation URL:", confirmation_url)

                # Contenuto email
                context = {
                    'user': user,
                    'confirmation_url': confirmation_url,
                }
                email_body = render_to_string('music/account/confirm_account_deletion_email.html', context)

                # Invia l'email
                send_mail(
                    'Confirm Account Deletion',
                    email_body,
                    'pulsemusicinc24@gmail.com',
                    [user.email],
                    fail_silently=False,
                )

                return redirect('home')
            else:
                messages.error(request, 'Password is incorrect.')
        return render(request, 'music/account/request_account_deletion.html')
    except Exception as e:
        logger.error(f"An error occurred during account deletion request: {e}")
        return redirect('home')

# conferma per eliinazione account dopo aver ricevuto la mail
@login_required
def confirm_account_deletion(request, uidb64, token):
    try:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if request.method == 'POST':
                # Elimina l'account utente
                user.delete()
                messages.success(request, 'Your account has been successfully deleted.')
                return redirect('home')
            return render(request, 'music/account/confirm_account_deletion.html', {'user': user})
        else:
            return redirect('home')
    except Exception as e:
        logger.error(f"An error occurred during account deletion confirmation: {e}")
        return redirect('home')


def restore_profile(request):
    return render(request, 'music/restoring/restore_profile.html')


from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

# recupero della password dopo aver richiesto aiuto al sistema
def recover_password(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                # Generato token id
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # url di conferma
                confirmation_url = request.build_absolute_uri(
                    reverse('confirm_password_change', kwargs={'uidb64': uid, 'token': token})
                )

                # contenuto render email
                context = {
                    'user': user,
                    'confirmation_url': confirmation_url,
                }
                email_body = render_to_string('music/restoring/confirm_password_change.html', context)

                # Send the email
                send_mail(
                    'Reset your password',
                    email_body,
                    'pulsemusicinc24@gmail.com',
                    [user.email],
                    fail_silently=False,
                )
                return redirect('home')  # ridiretto alla home
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
                return redirect('recover_password')  # Redirect to password recovery page
        return render(request, 'music/restoring/recover_password.html')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')


from django.contrib.auth.forms import SetPasswordForm

# conferma per cambio password
def confirm_password_change(request, uidb64, token):
    try:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Your password has been updated successfully.')
                    return redirect('login')
            else:
                form = SetPasswordForm(user)
            return render(request, 'music/restoring/set_new_password.html', {'form': form})
        else:
            messages.error(request, 'The password reset link is invalid or has expired.')
            return redirect('recover_password')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')


from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

# recupero username dopo la richiesta di aiuto
def recover_username(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                # Generate token and uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Construct confirmation URL
                confirmation_url = request.build_absolute_uri(
                    reverse('confirm_username_change', kwargs={'uidb64': uid, 'token': token})
                )

                # Render email content from template
                context = {
                    'user': user,
                    'confirmation_url': confirmation_url,
                }
                email_body = render_to_string('music/restoring/confirm_username_change.html', context)

                # Send the email
                send_mail(
                    'Reset your username',
                    email_body,
                    'pulsemusicinc24@gmail.com',
                    [user.email],
                    fail_silently=False,
                )
                return redirect('home')  # Redirect to home or another page
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
                return redirect('recover_username')  # Redirect to username recovery page
        return render(request, 'music/restoring/recover_username.html')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')

# conferma per cambio username
def confirm_username_change(request, uidb64, token):
    try:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_username = request.POST.get('new_username')
                if new_username:
                    user.username = new_username
                    user.save()
                    messages.success(request, 'Your username has been updated successfully.')
                    return redirect('login')
            return render(request, 'music/restoring/set_new_username.html', {'user': user})
        else:
            messages.error(request, 'The username reset link is invalid or has expired.')
            return redirect('recover_username')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')
