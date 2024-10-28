from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from music.models import ListenerProfile, ArtistProfile, Merchandise, TempOrderData
from music.forms import PurchaseForm
from unittest.mock import patch, MagicMock

class BuyMerchandiseViewTests(TestCase):

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
            stock_quantity=5  # quantità nell stock iniziale
        )
        self.url = reverse('buy_merchandise', args=[self.artist.username, self.merch.id])

    def test_buy_merchandise_without_login(self):
        """
        Verifica che un utente non autenticato venga reindirizzato alla pagina di login.
        """
        response = self.client.get(self.url)

        # Verifica che la risposta sia un redirect verso la pagina di login
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_buy_merchandise_get(self):
        """
        Verifica che una richiesta GET carichi correttamente il form e il template.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music/merchandise/buy_merchandise.html')
        self.assertIsInstance(response.context['form'], PurchaseForm)

    @patch('paypalrestsdk.Payment')
    def test_buy_merchandise_post_valid(self, MockPayment):
        """
        Verifica che una richiesta POST valida gestisca correttamente il pagamento e aggiorni lo stock.
        """
        # Set up the mock for the payment
        mock_payment = MagicMock()
        mock_payment.create.return_value = True
        mock_payment.id = 'PAYID-12345'
        mock_payment.links = [type('obj', (object,), {'rel': 'approval_url', 'href': 'http://paypal.com/approve'})]
        MockPayment.return_value = mock_payment

        # Log in user
        self.client.login(username='testuser', password='12345')

        # Form da compilare
        form_data = {
            'quantity': 1,
            'shipping_address': 'via test',
            'shipping_city': 'Citta test',
            'shipping_zip': '12345',
            'shipping_phone': '+1234567890',
        }

        # inviare post request con data valida
        response = self.client.post(self.url, form_data)

        # verificare di essere reindirizzati verso approval url di paypal
        self.assertEqual(response.status_code, 302)
        self.assertIn('http://paypal.com/approve', response['Location'])

        # refresh del merch e controllo stock
        self.merch.refresh_from_db()
        self.assertEqual(self.merch.stock_quantity, 4, "The stock should be reduced by 1.")

    @patch('paypalrestsdk.Payment.create')
    def test_buy_merchandise_post_invalid_stock(self, mock_payment_create):
        """
        Verifica che una richiesta POST con quantità maggiore dello stock disponibile
        venga gestita correttamente con un messaggio di errore e nessuna modifica allo stock.
        """
        # processo di creazione del mock di pagamento per simulare un fallimento
        mock_payment_create.return_value = False

        # Log in the user
        self.client.login(username='testuser', password='12345')

        # form con inserimento di una quantità maggiore nello stock rispetto alla disponibile
        form_data = {
            'quantity': 10,  # Requested quantity is greater than available stock (5)
            'shipping_address': '123 Main St',
            'shipping_city': 'Test City',
            'shipping_zip': '12345',
            'shipping_phone': '+1234567890',
        }

        # inviare richiesta post con stock invalido
        response = self.client.post(self.url, form_data)

        # verificare la risposta con stato 200 e rirendering del form
        self.assertEqual(response.status_code, 200)

        # controllo messaggio di errore
        self.assertContains(response, "Sorry, we only have 5 of Test Merch available.")

        #verificare che la quantità di stock non è cambiata da 5
        self.merch.refresh_from_db()
        self.assertEqual(self.merch.stock_quantity, 5, "Stock quantity should remain unchanged when request exceeds available stock.")

    def test_buy_merchandise_post_negative_quantity(self):
        """
Verifica che venga gestita una richiesta POST con una quantità negativa
        correttamente con un reindirizzamento e nessuna modifica allo stock.
        """
        # Log in the user
        self.client.login(username='testuser', password='12345')

        # form da compilare con quantità negativa
        form_data_negative = {
            'quantity': -3,
            'shipping_address': '123 Main St',
            'shipping_city': 'Test City',
            'shipping_zip': '12345',
            'shipping_phone': '+1234567890',
        }

        # inviare post request con quantità negativa
        response_negative = self.client.post(self.url, form_data_negative)

        # Verifica che il codice di stato della risposta sia 200 (il modulo viene nuovamente visualizzato con errori)
        self.assertEqual(response_negative.status_code, 200)

        # Verificare che venga visualizzato il messaggio di errore per la quantità negativa
        self.assertFormError(response_negative, 'form', 'quantity', 'Invalid quantity. Please enter a positive number.')

        # verifica che lo stock non è cambiato
        self.merch.refresh_from_db()
        self.assertEqual(self.merch.stock_quantity, 5, "Stock quantity should remain unchanged for negative quantity.")

    def test_buy_merchandise_post_invalid_phone_and_zip(self):
        """
Verifica che una richiesta POST con un numero di telefono e un codice postale non validi
        viene gestito correttamente con messaggi di errore del modulo e nessuna modifica allo stock.
        """
        # Log in the user
        self.client.login(username='testuser', password='12345')

        # Dati del modulo da inviare con un numero di telefono e un codice postale non validi
        form_data_invalid = {
            'quantity': 1,
            'shipping_address': '123 Main St',
            'shipping_city': 'Test City',
            'shipping_zip': '1234', # CAP non valido (meno di 5 cifre)
            'shipping_phone': 'invalid_phone',  # formato numero invalido
        }

        # Invia una richiesta POST con numero di telefono e codice postale non validi
        response_invalid = self.client.post(self.url, form_data_invalid)

        # Verifica che il codice di stato della risposta sia 200 (il modulo viene nuovamente visualizzato con errori)
        self.assertEqual(response_invalid.status_code, 200)

        # Controlla che venga visualizzato il messaggio di errore relativo al numero di telefono non valido
        self.assertFormError(response_invalid, 'form', 'shipping_phone', 'Enter a valid phone number.')

        # Controlla che venga visualizzato il messaggio di errore per codice postale non valido
        self.assertFormError(response_invalid, 'form', 'shipping_zip', 'Enter a valid ZIP code.')

        # Verificare che la quantità di stock non sia cambiata
        self.merch.refresh_from_db()
        self.assertEqual(self.merch.stock_quantity, 5,
                         "Stock quantity should remain unchanged for invalid phone number and ZIP code.")




