from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from music.models import ListenerProfile, ArtistProfile, Merchandise, TempOrderData


class BuyMerchandiseConcurrencyTests(TestCase):

    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        self.user1 = User.objects.create_user(username='testuser1', password='12345')
        self.user2 = User.objects.create_user(username='testuser2', password='12345')
        self.listener_profile1 = ListenerProfile.objects.create(user=self.user1)
        self.listener_profile2 = ListenerProfile.objects.create(user=self.user2)
        self.artist = User.objects.create_user(username='testartist', password='12345')
        self.artist_profile = ArtistProfile.objects.create(user=self.artist)
        self.merch = Merchandise.objects.create(
            name='Test Merch',
            artist=self.artist_profile,
            price=10.0,
            stock_quantity=5  # Stock iniziale
        )
        self.url = reverse('buy_merchandise', args=[self.artist.username, self.merch.id])

    @patch('paypalrestsdk.Payment')
    def test_concurrent_purchases(self, MockPayment):
        """
        Verifica la gestione della concorrenza quando due utenti tentano di acquistare quasi contemporaneamente.
        """
        # Configura il mock per il pagamento
        mock_payment = MagicMock()
        mock_payment.create.return_value = True
        mock_payment.id = 'PAYID-12345'
        mock_payment.links = [type('obj', (object,), {'rel': 'approval_url', 'href': 'http://paypal.com/approve'})]
        MockPayment.return_value = mock_payment

        self.client1.login(username='testuser1', password='12345')
        self.client2.login(username='testuser2', password='12345')

        form_data = {
            'quantity': 5,  # Entrambi provano a comprare tutto lo stock disponibile
            'shipping_address': '123 Main St',
            'shipping_city': 'Test City',
            'shipping_zip': '12345',
            'shipping_phone': '+1234567890',
        }

        # Primo utente tenta l'acquisto
        response1 = self.client1.post(self.url, form_data)

        # Ricarica l'oggetto Merchandise per simulare il tentativo del secondo utente subito dopo il primo
        self.merch.refresh_from_db()

        # Secondo utente tenta l'acquisto
        response2 = self.client2.post(self.url, form_data)

        # Verifica che il primo utente sia stato reindirizzato correttamente all'approvazione di PayPal
        self.assertEqual(response1.status_code, 302)
        self.assertIn('http://paypal.com/approve', response1['Location'])

        # Verifica che il secondo utente riceva un messaggio di errore per stock insufficiente
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, "Sorry, we only have 0 of Test Merch available.")

        # Verifica che solo un ordine sia stato creato
        successful_orders = TempOrderData.objects.filter(merch=self.merch, is_order_completed=False).count()
        self.assertEqual(successful_orders, 1, "Solo un ordine temporaneo dovrebbe essere completato con successo.")

        # Verifica che lo stock sia esaurito
        self.merch.refresh_from_db()
        self.assertEqual(self.merch.stock_quantity, 0, "Lo stock dovrebbe essere esaurito dopo il primo acquisto.")

