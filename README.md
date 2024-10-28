# Pulse: progetto di Tecnologie Web a tema musicale
# leggere tutto il file!

**Pulse** è un'applicazione web progettata in Python tramite il framework Django per la gestione, condivisione e fruizione di contenuti musicali.

## Prerequisiti

Assicurati di avere i seguenti strumenti installati sul tuo sistema:

- **Python 3.11 o superiore**: [Download Python](https://www.python.org/downloads/)
- **pip**: Il gestore di pacchetti per Python.
- **pipenv**: Strumento per la gestione degli ambienti virtuali Python e delle dipendenze del progetto.

Il resto degli strumenti e delle librerie necessari sono specificati nel file `requirements.txt`, che verrà utilizzato per completare l'ambiente virtuale nei passaggi seguenti.

## Installazione e avvio

1. **Navigare nella cartella principale del progetto dopo averla decompressa**.

    ```bash
    cd PulseProject
    ```

2. **Installare le dipendenze utilizzando pipenv**.

    ```bash
    pipenv install -r requirements.txt
    ```

3. **Entrare nell'ambiente virtuale creato tramite pipenv**.

    ```bash
    pipenv shell
    ```

4. **Eseguire le migrazioni per configurare il database**.

    ```bash
    python manage.py migrate
    ```

5. **Avviare il server di sviluppo di Django per utilizzare l'applicazione**.

    ```bash
    python manage.py runserver
    ```

6. **Avviare anche il seguente comando in un secondo terminale per la gestione dello stock. Potrebbe avviarsi un timer, attendere e poi fare le prove di acquisto. Il timer si avvierà ogni volta che si tenta un acquisto, se non andrà a buon fine il sistema può ripristinare lo stock alla fine del timer in questione**. 

    ```bash
    python manage.py qcluster
    ```

## Importante!

Alcune funzionalità, come il sistema di raccomandazione, funzionano solo interagendo con i file mp3, che vengono solitamente caricati dagli artisti all'interno degli album. Se desideri utilizzare brani già presenti nel database, puoi scaricare i file mp3 di prova dal seguente link:

[Scarica i file mp3 di prova](https://drive.google.com/drive/folders/1lDVPq_2KA-m43Ws3Bj8YufvGxI_cfr2M?usp=drive_link)

Dopo aver scaricato i file, è sufficiente inserire le cartelle con i nomi degli artist nella cartella `/media/brani_mp3/` del progetto, mantenendo la struttura originale delle cartelle. In questo modo, il sistema sarà in grado di trovare i file e riprodurli. In alternativa, è possibile creare un nuovo profilo artista e caricare della nuova musica.
Il sistema di raccomandazione aggiorna le statistiche relative ai gusti musicali dell'ascoltatore dopo ogni riproduzione effettiva di un brano, purché l'ascolto duri almeno 30 secondi consecutivi. Questi dati sono visibili nella sezione "My Profile/My Listenings" sotto forma di grafico.
Consiglio di utilizzare il profilo Pink Floyd per fare i vari test, infatti ha già album e merchandise caricati.




## Per completare un acquisto di merchandise

L'applicazione ti reindirizzerà a una pagina PayPal per finalizzare l'acquisto. Per testare questa funzionalità, puoi utilizzare le seguenti credenziali di esempio:

- **Email**: `sb-pxnr332332973@personal.example.com`
- **Password**: `6U(X=mq5`

### Configurazione PayPal e API
Se hai ottenuto questo progetto tramite GitHub, dovrai configurare le tue credenziali PayPal Sandbox per abilitare gli acquisti simulati. Senza questa configurazione, la funzionalità di acquisto di merchandise non sarà utilizzabile. Tuttavia, tutte le altre funzionalità dell'app rimarranno disponibili.

### Come inserire le tue API di PayPal
1. Ottieni il **client ID** e il **client secret** dal tuo account [PayPal Developer](https://developer.paypal.com/).
2. Apri il file `mysite/settings.py` e trova la sezione dedicata alla configurazione di PayPal.
3. Inserisci le tue credenziali PayPal nei campi indicati:

    ```python
    # Configura PayPal per simulare acquisti
    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox per i test, live per la produzione
        "client_id": "",  # inserisci qui il tuo client ID
        "client_secret": ""  # inserisci qui il tuo client secret
    })
    ```

**Nota**: Assicurati che il campo `"mode"` sia impostato su `"sandbox"` per i test. Quando l'applicazione sarà pronta per l'uso in produzione, aggiorna questo valore su `"live"`.

---

Con queste impostazioni, sarai in grado di testare e completare gli acquisti di merchandise tramite PayPal Sandbox.





## Test

E' possibile effettuarli tramite il comando 

    ```bash
    python manage.py test
    ```

e riguardano la fase di controllo durante gli acquisti di merchandise, coprendo tutti i casi di errore dal pre al post PayPal. 

## Uso dell'applicazione

Il database contiene già un numero significativo di utenti, sia artisti che ascoltatori, e altre entità relative all'utilizzo dell'applicazione, visualizzabili nella pagina di amministrazione (le credenziali di accesso sono username: `admin` e password: `admin`).

È possibile iscriversi come nuovo utente e scegliere se essere un creatore o un fruitore di contenuti. L'intero processo di iscrizione è completamente guidato e ben documentato per risolvere eventuali dubbi. L'applicazione è progettata per essere intuitiva e facile da navigare.

