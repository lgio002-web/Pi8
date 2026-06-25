"""Utilità per la formattazione di date e valuta in locale italiano."""
from datetime import date, datetime


def format_euro(value):
    """
    Formatta un valore numerico in Euro secondo lo standard italiano.
    Esempi: 1€, 1,50€, 10€, 1.000€, 10.050,50€
    """
    if value is None:
        return "0€"

    value = float(value)

    # Separa parte intera e decimale
    if value == int(value):
        # Numero intero: nessun decimale
        formatted = f"{int(value):,}".replace(",", ".")
    else:
        # Numero con decimali
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return f"{formatted}€"


def format_data_it(value):
    """
    Formatta una data nel formato italiano gg-mm-aaaa.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return value
    if isinstance(value, (date, datetime)):
        return value.strftime('%d-%m-%Y')
    return str(value)


def parse_data_it(date_string):
    """
    Converte una stringa gg-mm-aaaa in un oggetto date.
    Supporta anche il formato yyyy-mm-dd (input HTML5).
    """
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%d-%m-%Y').date()
    except ValueError:
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            return None
