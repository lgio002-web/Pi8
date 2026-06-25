"""Script per inizializzare il database e creare l'utente Admin."""
import os
import sys

# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash


def init_database():
    """Crea tutte le tabelle e l'utente Admin."""
    app = create_app()

    with app.app_context():
        # Crea tutte le tabelle
        db.create_all()
        print("✓ Database creato con successo!")

        # Crea l'utente Admin se non esiste
        admin = User.query.filter_by(tessera='ADMIN').first()
        if not admin:
            from datetime import date
            admin = User(
                tessera='ADMIN',
                nome='Admin',
                cognome='Pi8',
                data_nascita=date(2000, 1, 1),
                email='pi8admin',
                ruolo='admin',
                attivo=True
            )
            admin.set_password('69Presidente69')
            db.session.add(admin)
            db.session.commit()
            print("✓ Utente Admin creato (username: pi8admin, password: 69Presidente69)")
        else:
            print("ℹ Utente Admin già presente.")

        print(f"\n📁 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("🚀 Puoi ora lanciare: python seed_db.py (per caricare dati di test)")


if __name__ == '__main__':
    init_database()
