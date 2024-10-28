import time

from django.db import transaction

from .models import Merchandise, TempOrderData


# ripristina lo stock se entro 40 secondi non viene completato l'acquisto+

def release_stock(merch_id, quantity, payment_id):
    """
    Funzione chiamata automaticamente dal task asincrono per ripristinare lo stock.
    """
    print(f"Task di rilascio stock iniziato per payment_id {payment_id}. Timestamp: {time.time()}")

    # Simula il tempo di attesa (30 secondi)
    for i in range(30, 0, -1):
        print(f"Tempo rimasto per payment_id {payment_id}: {i} secondi. Timestamp: {time.time()}")
        time.sleep(1)

    # A tempo scaduto, controlla se l'ordine è già stato completato
    try:
        temp_order = TempOrderData.objects.get(payment_id=payment_id)
        if temp_order.is_order_completed:
            print(
                f"L'ordine per payment_id {payment_id} è stato completato. Nessuna azione necessaria. Timestamp: {time.time()}")
            return  # Se l'ordine è completato, non fare nulla
        else:
            # Ripristina lo stock
            with transaction.atomic():
                merch = Merchandise.objects.select_for_update().get(id=merch_id)
                merch.stock_quantity += quantity
                merch.save()
                temp_order.delete()
            print(f"Stock ripristinato per payment_id {payment_id} poiché il timer è scaduto. Timestamp: {time.time()}")
    except TempOrderData.DoesNotExist:
        print(
            f"TempOrderData non trovato per payment_id {payment_id}. Probabilmente è stato già processato. Timestamp: {time.time()}")
