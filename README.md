# ASD Pi8 Running - Portale Web

Portale web per la gestione della società sportiva ASD Pi8 Running.

## Tecnologie
- **Backend:** Python 3.10+ / Flask
- **Database:** SQLite (via SQLAlchemy)
- **Frontend:** Tailwind CSS (CDN) + Jinja2 templates
- **Auth:** Flask-Login con RBAC (Admin/Atleta)

## Struttura Progetto

```
Pi8/
├── app/
│   ├── __init__.py          # Factory dell'app Flask
│   ├── models.py            # Modelli SQLAlchemy
│   ├── routes/
│   │   ├── main.py          # Homepage/redirect
│   │   ├── auth.py          # Login, primo accesso, logout
│   │   ├── gare.py          # CRUD gare, iscrizioni
│   │   ├── admin.py         # Dashboard admin, gestione atleti
│   │   └── atleta.py        # Profilo atleta, nuova iscrizione
│   ├── templates/           # Template HTML Jinja2
│   ├── static/uploads/      # Foto profilo uploadate
│   └── utils/
│       ├── formatters.py    # Formattazione date/valuta italiana
│       ├── mock_email.py    # Mock invio email
│       └── mock_payment.py  # Mock pagamenti
├── data/
│   └── atleti_sample.csv    # CSV atleti di esempio
├── instance/                # Database SQLite (auto-creato)
├── config.py                # Configurazione
├── init_db.py               # Inizializzazione database
├── seed_db.py               # Popolamento dati di test
├── run.py                   # Entry point server
└── requirements.txt         # Dipendenze Python
```

## Setup Rapido

```bash
# 1. Crea un virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. Installa le dipendenze
pip install -r requirements.txt

# 3. Inizializza il database
python init_db.py

# 4. Popola con dati di test
python seed_db.py

# 5. Avvia il server
python run.py
```

Apri il browser su: **http://127.0.0.1:5000**

## Credenziali di Test

### Admin
- Username: `pi8admin`
- Password: `69Presidente69`

### Atleta (Primo Accesso)
1. Vai su "Primo accesso"
2. Inserisci: Tessera `LE065320`, Cognome `Rossi`, Data Nascita `1985-03-15`
3. Inserisci una email
4. La password provvisoria sarà: `LE065320Password`

## Funzionalità

- **Admin:** Dashboard, gestione gare (CRUD), gestione atleti, approvazione nuove iscrizioni
- **Atleta:** Profilo, iscrizione/cancellazione gare, cambio password, upload foto
- **Gare:** Iscrizione con pagamento mock, vincolo data ultima iscrizione, lista iscritti
- **Notifiche:** Mock email loggate su console e file `mock_emails.txt`
- **Pagamenti:** Mock con esito sempre positivo, log su `mock_pagamenti.txt`

## Formato Dati
- **Date:** `gg-mm-aaaa` (visualizzazione), datepicker HTML5 (input)
- **Valuta:** Standard italiano con € a destra (es. `10,50€`, `1.000€`)
