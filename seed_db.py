"""Script per popolare il database con dati di test dal CSV degli atleti."""
import os
import sys
import csv
from datetime import date, datetime, timedelta

# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Gara


def seed_atleti():
    """Importa gli atleti dal file CSV ufficiale."""
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'atleti_ufficiali.csv')

    if not os.path.exists(csv_path):
        print("✗ File CSV non trovato:", csv_path)
        return

    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tessera = row['Tessera'].strip()

            # Salta se l'atleta esiste già
            if User.query.filter_by(tessera=tessera).first():
                continue

            data_nascita = datetime.strptime(row['DataNascita'].strip(), '%Y-%m-%d').date()
            data_tess_str = row['DataTess'].strip()
            data_tess = datetime.strptime(data_tess_str, '%Y-%m-%d').date() if data_tess_str else None
            causale = row['CausaleSospensione'].strip() if row['CausaleSospensione'] else None
            taglia = row['TagliaMaglia'].strip() if row['TagliaMaglia'] else None

            atleta = User(
                tessera=tessera,
                nome=row['Nome'].strip(),
                cognome=row['Cognome'].strip(),
                data_nascita=data_nascita,
                categoria=row['Categoria'].strip() if row['Categoria'] else None,
                luogo_nascita=row['LuogoNascita'].strip() if row['LuogoNascita'] else None,
                data_tesseramento=data_tess,
                taglia_maglia=taglia,
                causale_sospensione=causale,
                ruolo='atleta',
                attivo=False
            )
            db.session.add(atleta)
            count += 1

    db.session.commit()
    print(f"✓ {count} atleti importati dal CSV ufficiale.")


def seed_gare():
    """Crea alcune gare di esempio."""
    if Gara.query.count() > 0:
        print("ℹ Gare già presenti, skip.")
        return

    oggi = date.today()

    gare_esempio = [
        Gara(
            nome_gara="Corsa dei Trulli",
            data_gara=oggi + timedelta(days=30),
            distanza="10km",
            costo=15.0,
            data_ultima_iscrizione=oggi + timedelta(days=25),
            note="Percorso panoramico tra i trulli di Alberobello."
        ),
        Gara(
            nome_gara="Mezza Maratona del Salento",
            data_gara=oggi + timedelta(days=60),
            distanza="Mezza Maratona",
            costo=25.50,
            data_ultima_iscrizione=oggi + timedelta(days=50),
            note="Partenza da Lecce, arrivo a Otranto."
        ),
        Gara(
            nome_gara="5K Solidale - Corriamo Insieme",
            data_gara=oggi + timedelta(days=15),
            distanza="5km",
            costo=0,
            data_ultima_iscrizione=oggi + timedelta(days=10),
            note="Gara non competitiva di beneficenza. Partecipazione gratuita!"
        ),
        Gara(
            nome_gara="Trail del Parco Naturale",
            data_gara=oggi + timedelta(days=90),
            distanza="Altro",
            distanza_altro="18km trail",
            costo=30.0,
            data_ultima_iscrizione=oggi + timedelta(days=75),
            note="Percorso sterrato nel Parco Naturale Regionale."
        ),
        Gara(
            nome_gara="Maratona d'Inverno",
            data_gara=oggi - timedelta(days=5),  # Gara passata (iscrizioni chiuse)
            distanza="Maratona",
            costo=40.0,
            data_ultima_iscrizione=oggi - timedelta(days=10),
            note="Edizione invernale della maratona cittadina."
        ),
    ]

    for gara in gare_esempio:
        db.session.add(gara)

    db.session.commit()
    print(f"✓ {len(gare_esempio)} gare di esempio create.")


def main():
    """Esegue il seeding completo del database."""
    app = create_app()

    with app.app_context():
        print("\n🌱 Seeding del database in corso...\n")
        seed_atleti()
        seed_gare()
        print("\n✅ Seeding completato con successo!")
        print("\n📋 Riepilogo:")
        print(f"   Atleti nel DB: {User.query.filter(User.ruolo == 'atleta').count()}")
        print(f"   Gare nel DB: {Gara.query.count()}")
        print("\n🔑 Per testare il primo accesso di un atleta, usa:")
        print("   Tessera: LE065320")
        print("   Cognome: NINI")
        print("   Data Nascita: 26-04-1994")


if __name__ == '__main__':
    main()
