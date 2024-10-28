
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from music.models import ListenerProfile, ArtistProfile, Merchandise, TempOrderData, Order
from django.utils import timezone
from datetime import timedelta

from music.tasks import release_stock


class PayPalReturnViewTests(TestCase):

    def setUp(self):
        # Set up iniziale
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.listener_profile = ListenerProfile.objects.create(user=self.user)
        self.artist = User.objects.create_user(username='testartist', password='12345')
        self.artist_profile = ArtistProfile.objects.create(user=self.artist)
        self.merch = Merchandise.objects.create(
            name='Test Merch',
            artist=self.artist_profile,
            price=10.0,
            stock_quantity=4  # Lo stock è già stato ridotto a 4 da buy_merchandise
        )
        self.url = reverse('paypal_return')
        self.payment_id = 'PAYID-12345'
        self.temp_order = TempOrderData.objects.create(
            user=self.user,
            payment_id=self.payment_id,
            merch=self.merch,
            quantity=1,
            reservation_expiration=timezone.now() + timedelta(seconds=40),
            is_order_completed=False
        )

    @patch('paypalrestsdk.Payment.find')
    @patch('music.views_transaction.async_task') # fingere l'attività per impedirne l'effettiva esecuzione
    def test_paypal_return_payment_success(self, mock_async_task, mock_payment_find):
        """
        Verifica che la view paypal_return gestisca correttamente un pagamento confermato.
        """
        # Simula un pagamento riuscito
        mock_payment = MagicMock()
        mock_payment.execute.return_value = True
        mock_payment.id = self.payment_id
        mock_payment_find.return_value = mock_payment

        # Login dell'utente
        self.client.login(username='testuser', password='12345')

        # Simula il ritorno da PayPal
        session = self.client.session
        session['payment_id'] = self.payment_id
        session['merch_id'] = self.merch.id
        session['quantity'] = 1
        session['total_price'] = '10.0'
        session['reservation_expiration'] = (timezone.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S.%f')
        session['shipping_address'] = '123 Main St'
        session['shipping_city'] = 'Test City'
        session['shipping_zip'] = '12345'
        session['shipping_phone'] = '+1234567890'
        session.save()

        response = self.client.get(self.url, {'PayerID': 'PAYERID123'})

        # Verifica che l'utente venga reindirizzato alla pagina di acquisti
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('my_shopping', args=[self.user.username]))

        # Verifica che l'ordine sia stato creato
        order_exists = Order.objects.filter(transaction_id=self.payment_id, payment_status='Completed').exists()
        self.assertTrue(order_exists, "L'ordine non è stato creato correttamente.")

        # Verifica che lo stock sia rimasto invariato dopo il pagamento
        self.merch.refresh_from_db()
        self.assertEqual(self.merch.stock_quantity, 4, "Lo stock non dovrebbe cambiare dopo un pagamento confermato.")






    @patch('paypalrestsdk.Payment.find')
    @patch('music.views_transaction.async_task')  # Mock the task to prevent it from actually running
    def test_paypal_return_payment_failure_and_stock_release(self, mock_async_task, mock_payment_find):
        """
        Verifica che lo stock venga ripristinato correttamente se il pagamento fallisce e il task di rilascio viene eseguito.
        """
        # Simula un pagamento fallito
        mock_payment = MagicMock()
        mock_payment.execute.return_value = False  # Simula un pagamento fallito
        mock_payment_find.return_value = mock_payment

        # Login dell'utente
        self.client.login(username='testuser', password='12345')

        # Simula il ritorno da PayPal
        session = self.client.session
        session['payment_id'] = self.payment_id
        session['merch_id'] = self.merch.id
        session['quantity'] = 1
        session['total_price'] = '10.0'
        session['reservation_expiration'] = (timezone.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S.%f')
        session['shipping_address'] = '123 Main St'
        session['shipping_city'] = 'Test City'
        session['shipping_zip'] = '12345'
        session['shipping_phone'] = '+1234567890'
        session.save()

        response = self.client.get(self.url, {'PayerID': 'PAYERID123'})

        # Verifica che l'utente venga reindirizzato alla pagina di acquisto per riprovare
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('buy_merchandise', args=[self.artist.username, self.merch.id]))

        # Esegui manualmente il task di rilascio dello stock dopo il timeout
        release_stock(self.merch.id, 1, self.payment_id)

        # Verifica che lo stock sia stato ripristinato alla quantità originale
        self.merch.refresh_from_db()
        self.assertEqual(self.merch.stock_quantity, 5,
                         "Lo stock dovrebbe essere ripristinato alla quantità originale dopo il fallimento del pagamento.")