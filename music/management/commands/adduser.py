

from django.contrib.auth.models import User
from music.models import ListenerProfile  # Assicurati che il modello ListenerProfile sia importato correttamente

# Lista di nomi per gli utenti ascoltatori
names = ["Luca", "Marco", "Giulia", "Francesca", "Alessandro", "Giorgia", "Matteo", "Simone", "Valentina", "Fabio"]

for name in names:
    # Crea l'utente
    user = User.objects.create_user(
        username=name.lower(),
        email=f"{name.lower()}@mail.com",
        password=f"{name}190701"
    )

    # Crea il profilo di ascoltatore
    listener_profile = ListenerProfile.objects.create(
        user=user,
        name=name,  # Usando il nome dell'utente
        bio="Sono un ascoltatore",
        listening_mode='seeker'  # Modalità di ascolto predefinita
        # Nessuna foto viene specificata, quindi il campo rimane vuoto
    )

    print(f"Creato utente e profilo ascoltatore per: {name}")

print("Operazione completata.")
