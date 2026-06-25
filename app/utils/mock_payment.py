"""Mock del servizio di pagamento.
In produzione, questo modulo verrà sostituito con un gateway reale (Stripe, PayPal, ecc.).
Per il prototipo, ogni pagamento viene registrato automaticamente con esito positivo.
"""
from datetime import datetime

MOCK_LOG_FILE = 'mock_pagamenti.txt'


def processa_pagamento(atleta_tessera, gara_nome, importo, metodo):
    """
    Simula il processamento di un pagamento.
    Ritorna sempre esito positivo per il prototipo.
    
    Args:
        atleta_tessera: Numero tessera dell'atleta
        gara_nome: Nome della gara
        importo: Importo in Euro
        metodo: Metodo di pagamento (paypal, carta, bonifico)
    
    Returns:
        dict con esito del pagamento
    """
    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    log_entry = (
        f"\n[MOCK PAGAMENTO] {timestamp}\n"
        f"  Atleta: {atleta_tessera}\n"
        f"  Gara: {gara_nome}\n"
        f"  Importo: {importo}€\n"
        f"  Metodo: {metodo}\n"
        f"  Esito: OK ✓\n"
    )

    # Log su console
    print(log_entry)

    # Log su file
    with open(MOCK_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

    return {
        'esito': 'OK',
        'transazione_id': f"MOCK-{atleta_tessera}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'metodo': metodo,
        'importo': importo,
        'timestamp': timestamp
    }
