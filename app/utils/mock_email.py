"""Mock del servizio di invio email.
In produzione, questo modulo verrà sostituito con un vero provider SMTP.
Per il prototipo, logga le email su console e su file.
"""
import os
from datetime import datetime

MOCK_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mock_emails.txt')


def invia_email(destinatario, oggetto, corpo, cc=None):
    """
    Simula l'invio di una email. Logga su console e su file di testo.
    
    Args:
        destinatario: Indirizzo email del destinatario
        oggetto: Oggetto dell'email
        corpo: Corpo del messaggio
        cc: Indirizzo in copia (opzionale)
    """
    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    cc_str = f" | CC: {cc}" if cc else ""

    log_entry = (
        f"\n{'='*60}\n"
        f"[MOCK EMAIL] {timestamp}\n"
        f"A: {destinatario}{cc_str}\n"
        f"Oggetto: {oggetto}\n"
        f"{'─'*40}\n"
        f"{corpo}\n"
        f"{'='*60}\n"
    )

    # Log su console
    print(log_entry)

    # Log su file
    with open(MOCK_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)


def invia_password_provvisoria(email, tessera):
    """Invia la password provvisoria al nuovo atleta."""
    password = f"{tessera}Password"
    invia_email(
        destinatario=email,
        oggetto="ASD Pi8 Running - La tua password provvisoria",
        corpo=(
            f"Ciao!\n\n"
            f"Ecco la tua password provvisoria per accedere al portale:\n\n"
            f"  Password: {password}\n\n"
            f"Ti consigliamo di cambiarla al primo accesso.\n\n"
            f"Buone corse!\n"
            f"ASD Pi8 Running"
        )
    )
    return password


def notifica_iscrizione_gara(atleta_email, atleta_nome, nome_gara):
    """Notifica l'iscrizione a una gara."""
    invia_email(
        destinatario=atleta_email,
        oggetto=f"Iscrizione confermata - {nome_gara}",
        corpo=(
            f"Ciao {atleta_nome}!\n\n"
            f"La tua iscrizione alla gara \"{nome_gara}\" è stata confermata.\n\n"
            f"Buon allenamento!\n"
            f"ASD Pi8 Running"
        ),
        cc="pi8.running@gmail.com"
    )


def notifica_cancellazione_gara(atleta_email, atleta_nome, nome_gara):
    """Notifica la cancellazione da una gara."""
    invia_email(
        destinatario=atleta_email,
        oggetto=f"Cancellazione iscrizione - {nome_gara}",
        corpo=(
            f"Ciao {atleta_nome}!\n\n"
            f"La tua iscrizione alla gara \"{nome_gara}\" è stata cancellata.\n\n"
            f"ASD Pi8 Running"
        ),
        cc="pi8.running@gmail.com"
    )
