from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from music.models import ListenerProfile, ArtistProfile, Merchandise

class PayPalCancelViewTests(TestCase):

    def setUp(self):

        self.client = Client()# Imposta il client di prova e i dati iniziali
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.listener_profile = ListenerProfile.objects.create(user=self.user)
        self.artist = User.objects.create_user(username='testartist', password='12345')
        self.artist_profile = ArtistProfile.objects.create(user=self.artist)
        self.merch = Merchandise.objects.create(
            name='Test Merch',
            artist=self.artist_profile,
            price=10.0,
            stock_quantity=5  # stock quantità iniziale
        )
        self.url = reverse('paypal_cancel')
        self.payment_id = 'PAYID-12345'

    def test_paypal_cancel_redirect_and_message(self):
        """
        Verifica che la view paypal_cancel gestisca correttamente l'annullamento del pagamento
        mostrando un messaggio di avviso e reindirizzando l'utente.
        """
        # Log in dell 'user
        self.client.login(username='testuser', password='12345')

        # Simula l'annullamento del pagamento impostando i dati della sessione
        session = self.client.session
        session['payment_id'] = self.payment_id
        session['merch_id'] = self.merch.id
        session['quantity'] = 1
        session.save()

        # Effettua una richiesta GET alla vista di cancellazione
        response = self.client.get(self.url)

        # Verifica che l'utente venga reindirizzato alla pagina appropriata
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('public_listener_artists', args=[self.user.username]))

        # Verifica che il messaggio di avviso sia stato inviato correttamente
        messages_list = list(response.wsgi_request._messages)
        self.assertTrue(any("You have canceled your payment." in str(message) for message in messages_list))

    def test_paypal_cancel_does_not_modify_stock(self):
        """
        Verifica che lo stock della merce rimanga invariato quando il pagamento viene annullato.
        """
        # Log in the user
        self.client.login(username='testuser', password='12345')

        # Simula l'annullamento del pagamento impostando i dati della sessione
        session = self.client.session
        session['payment_id'] = self.payment_id
        session['merch_id'] = self.merch.id
        session['quantity'] = 1
        session.save()

        # Effettua una richiesta GET alla vista di cancellazione
        self.client.get(self.url)

        # Verifica che lo stock della merce non sia stato modificato
        self.merch.refresh_from_db()
        self.assertEqual(self.merch.stock_quantity, 5, "Stock quantity should remain unchanged after payment cancellation.")
