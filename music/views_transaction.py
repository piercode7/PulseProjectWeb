# tasks.py
import datetime
import logging

import paypalrestsdk
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, DatabaseError
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import make_aware
from django_q.tasks import async_task

from .forms import PurchaseForm
from .models import TempOrderData, Notification, Merchandise, Order

logger = logging.getLogger(__name__)

# funzione per inserire i dettagli di ascquisto ed essere reindirizzati ad un pagamento simulato paypal
@login_required
def buy_merchandise(request, username, merch_id):
    try:
        merch = get_object_or_404(Merchandise, id=merch_id)

        if request.method == 'POST':
            form = PurchaseForm(request.POST)
            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                shipping_address = form.cleaned_data['shipping_address']
                shipping_city = form.cleaned_data['shipping_city']
                shipping_zip = form.cleaned_data['shipping_zip']
                shipping_phone = form.cleaned_data['shipping_phone']

                try:
                    # Blocco dello stock con transazione atomica
                    with transaction.atomic():
                        # Recupera e blocca il record del merchandise
                        merch = Merchandise.objects.select_for_update().get(id=merch_id)

                        # Controllo dello stock
                        if quantity > merch.stock_quantity:
                            messages.error(request,
                                           f"Sorry, we only have {merch.stock_quantity} of {merch.name} available.")
                            return render(request, 'music/merchandise/buy_merchandise.html',
                                          {'form': form, 'merch': merch})

                        # Riserva la quantità richiesta
                        merch.stock_quantity -= quantity
                        merch.save()

                        total_price = merch.price * quantity
                        reservation_expiration = timezone.now() + datetime.timedelta(
                            seconds=30)  # 40 secondi di timeout

                        payment = paypalrestsdk.Payment({
                            "intent": "sale",
                            "payer": {
                                "payment_method": "paypal"
                            },
                            "redirect_urls": {
                                "return_url": request.build_absolute_uri('/paypal/return/'),
                                "cancel_url": request.build_absolute_uri('/paypal/cancel/')
                            },
                            "transactions": [{
                                "item_list": {
                                    "items": [{
                                        "name": merch.name,
                                        "sku": str(merch.id),
                                        "price": str(merch.price),
                                        "currency": "USD",
                                        "quantity": quantity,
                                    }]
                                },
                                "amount": {
                                    "total": str(total_price),
                                    "currency": "USD"
                                },
                                "description": f"Purchase of {quantity} {merch.name}(s)"
                            }]
                        })

                        if payment.create():
                            # Salva i dati di transazione nella sessione
                            request.session['payment_id'] = payment.id
                            request.session['merch_id'] = merch.id
                            request.session['quantity'] = quantity
                            request.session['total_price'] = str(total_price)
                            request.session['reservation_expiration'] = reservation_expiration.strftime(
                                '%Y-%m-%d %H:%M:%S.%f')

                            # Salva le informazioni di spedizione nella sessione
                            request.session['shipping_address'] = shipping_address
                            request.session['shipping_city'] = shipping_city
                            request.session['shipping_zip'] = shipping_zip
                            request.session['shipping_phone'] = shipping_phone

                            # Creare una transazione temporanea per tracciare lo stock
                            TempOrderData.objects.create(
                                user=request.user,
                                payment_id=payment.id,
                                merch=merch,
                                quantity=quantity,
                                reservation_expiration=reservation_expiration,
                                is_order_completed=False
                            )

                            # Avvia il task asincrono di rilascio stock
                            async_task('music.tasks.release_stock', merch.id, quantity, payment.id)

                            for link in payment.links:
                                if link.rel == "approval_url":
                                    return redirect(link.href)
                        else:
                            # Pulisce i dati dalla sessione se il pagamento fallisce
                            request.session.flush()
                            merch.stock_quantity += quantity
                            merch.save()
                            messages.error(request, "There was an error processing your payment. Please try again.")
                            return redirect('buy_merchandise', username=request.user.username, merch_id=merch_id)

                except DatabaseError as e:
                    # Se c'è un problema di concorrenza, mostra un messaggio di errore
                    messages.error(request,
                                   "Another user is already attempting to buy this item. Please try again shortly.")
                    return redirect('buy_merchandise', username=request.user.username, merch_id=merch_id)

                except Exception as e:
                    # Pulisce i dati dalla sessione se si verifica un errore
                    request.session.flush()
                    messages.error(request, "There was an error. Please try again.")
                    print(f"Error occurred: {e}")
                    return redirect('buy_merchandise', username=request.user.username, merch_id=merch_id)
                else:
                    messages.error(request, "Invalid form submission. Please try again.")
                    return redirect('buy_merchandise', username=request.user.username, merch_id=merch_id)

        else:
            form = PurchaseForm()

        return render(request, 'music/merchandise/buy_merchandise.html', {'form': form, 'merch': merch})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return redirect('home')

# dopo essere tornato da paypal serve a definire se il tempo è scaduto o se ci sono stati altri problemi, in tal caso deve rilasciare lo stock
def paypal_return(request, payment_id=None, auto_called=False):
    """
    Verifica lo stato del pagamento e aggiorna lo stock se necessario.
    Se chiamato automaticamente (auto_called=True), non effettua il redirect dell'utente.
    """
    if not payment_id:
        payment_id = request.session.get('payment_id')

    merch_id = request.session.get('merch_id')
    quantity = request.session.get('quantity')
    total_price = request.session.get('total_price')
    reservation_expiration_str = request.session.get('reservation_expiration')

    # Recupera le informazioni di spedizione dalla sessione
    shipping_address = request.session.get('shipping_address')
    shipping_city = request.session.get('shipping_city')
    shipping_zip = request.session.get('shipping_zip')
    shipping_phone = request.session.get('shipping_phone')

    if not all([shipping_address, shipping_city, shipping_zip, shipping_phone]):
        messages.error(request, "Shipping information is incomplete or has expired.")
        return redirect('buy_merchandise', username=request.user.username, merch_id=merch_id)

    # Converti la stringa di scadenza della prenotazione in un oggetto datetime
    if reservation_expiration_str:
        reservation_expiration = make_aware(
            datetime.datetime.strptime(reservation_expiration_str, '%Y-%m-%d %H:%M:%S.%f'))
    else:
        messages.error(request, "Session data is incomplete or has expired.")
        return redirect('buy_merchandise', username=request.user.username, merch_id=merch_id)

    # Check if TempOrderData exists
    try:
        temp_order = TempOrderData.objects.get(payment_id=payment_id)
        if temp_order.is_order_completed:
            messages.success(request, "Your order has already been completed.")
            return redirect('my_shopping', username=request.user.username)
    except TempOrderData.DoesNotExist:
        print(
            f"No temporary order data found for payment_id {payment_id}. It may have already been processed or expired.")
        messages.error(request, "Your order has already been processed or expired.")
        return redirect('buy_merchandise', username=request.user.username, merch_id=merch_id)

    merch = get_object_or_404(Merchandise, id=merch_id)
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": request.GET.get('PayerID')}):
        with transaction.atomic():
            # Verifica se l'ordine è stato completato in tempo
            if timezone.now() > reservation_expiration:
                print(f"Stock was already released for the expired payment with ID {payment_id}.")
                messages.error(request, "Your payment session has expired. Stock has been released.")
                return redirect('buy_merchandise', username=merch.artist.user.username, merch_id=merch.id)

            # Crea l'ordine con tutte le informazioni, incluse quelle di spedizione
            order = Order.objects.create(
                buyer=request.user,
                seller=merch.artist.user,
                merchandise=merch,
                quantity=quantity,
                total_price=total_price,
                payment_method='paypal',
                transaction_id=payment.id,
                payment_status='Completed',
                shipping_address=shipping_address,
                shipping_city=shipping_city,
                shipping_zip=shipping_zip,
                shipping_phone=shipping_phone
            )
            temp_order.is_order_completed = True
            temp_order.save()

            # Creazione della notifica per l'artista dopo la creazione dell'ordine
            buyer = request.user.username
            buyer_url = reverse("public_listener_artists", args=[buyer])
            notification_message = f'<a href="{buyer_url}">{buyer}</a> purchased your merchandise "{merch.name}".'

            Notification.objects.create(
                user=merch.artist.user,  # Notifica per l'artista
                notification_type='purchase',
                message=notification_message
            )

            print(f"Payment completed for payment_id {payment_id}. Stock release cancelled.")
            messages.success(request, "Your order has been successfully created!")
            return redirect('my_shopping', username=request.user.username)
    else:
        print(f"Error confirming payment for payment_id {payment_id}.")
        messages.error(request, "There was an error confirming your payment.")
        if not auto_called:
            return redirect('buy_merchandise', username=merch.artist.user.username, merch_id=merch_id)

# in caso di problemi su paypal stesso per anticipare la chiusura
@login_required
def paypal_cancel(request, payment_id=None, auto_called=False):
    """
    Annulla l'ordine ma non tocca lo stock.
    """
    if not payment_id:
        payment_id = request.session.get('payment_id')

    merch_id = request.session.get('merch_id')
    quantity = request.session.get('quantity')

    # Aggiorna l'interfaccia utente con il messaggio di annullamento
    if not auto_called:
        messages.warning(request, "You have canceled your payment.")
        return redirect('public_listener_artists', username=request.user.username)
