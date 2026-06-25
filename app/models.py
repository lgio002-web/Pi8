"""Modelli del database per ASD Pi8 Running."""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """Modello Utente/Atleta con campi anagrafica FIDAL."""
    __tablename__ = 'users'

    tessera = db.Column(db.String(20), primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    data_nascita = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(30), nullable=True)
    luogo_nascita = db.Column(db.String(100), nullable=True)
    data_tesseramento = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    taglia_maglia = db.Column(db.String(5), nullable=True)
    foto_profilo = db.Column(db.String(256), nullable=True)
    ruolo = db.Column(db.String(10), default='atleta')  # 'admin' o 'atleta'
    attivo = db.Column(db.Boolean, default=False)  # Diventa True dopo primo accesso

    # Campi FIDAL aggiuntivi
    agonista = db.Column(db.String(20), nullable=True)  # AGONISTA / NON AGONISTA
    codice_fiscale = db.Column(db.String(16), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    cellulare = db.Column(db.String(20), nullable=True)
    fax = db.Column(db.String(20), nullable=True)
    indirizzo = db.Column(db.String(200), nullable=True)
    cap = db.Column(db.String(5), nullable=True)
    provincia = db.Column(db.String(50), nullable=True)
    citta = db.Column(db.String(100), nullable=True)
    iban = db.Column(db.String(34), nullable=True)
    professione = db.Column(db.String(100), nullable=True)
    titolo_studio = db.Column(db.String(50), nullable=True)
    scuola = db.Column(db.String(100), nullable=True)
    doppia_cittadinanza = db.Column(db.Boolean, default=False)
    nazione_gara = db.Column(db.String(50), default='ITALIA')
    straniero = db.Column(db.Boolean, default=False)
    cittadinanza = db.Column(db.String(50), nullable=True)
    data_scadenza_certificato = db.Column(db.Date, nullable=True)
    tipo_movimento = db.Column(db.String(50), nullable=True)  # Rinnovo Tesserato, Nuovo Tesseramento
    causale_sospensione = db.Column(db.String(100), nullable=True)

    # Relazione con iscrizioni
    iscrizioni = db.relationship('Iscrizione', backref='atleta', lazy=True)

    def get_id(self):
        return self.tessera

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.ruolo == 'admin'


class Gara(db.Model):
    """Modello Gara."""
    __tablename__ = 'gare'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_gara = db.Column(db.Date, nullable=False)
    nome_gara = db.Column(db.String(200), nullable=False)
    distanza = db.Column(db.String(50), nullable=False)  # 5km, 10km, Mezza Maratona, Maratona, Altro
    distanza_altro = db.Column(db.String(100), nullable=True)  # Campo libero se distanza == 'Altro'
    costo = db.Column(db.Float, default=0.0)
    data_ultima_iscrizione = db.Column(db.Date, nullable=False)
    note = db.Column(db.Text, nullable=True)
    creata_il = db.Column(db.DateTime, default=datetime.utcnow)

    # Relazione con iscrizioni
    iscrizioni = db.relationship('Iscrizione', backref='gara', lazy=True, cascade='all, delete-orphan')

    @property
    def iscrizioni_aperte(self):
        """Verifica se le iscrizioni sono ancora aperte."""
        return datetime.now().date() <= self.data_ultima_iscrizione

    @property
    def distanza_display(self):
        """Restituisce la distanza formattata per la visualizzazione."""
        if self.distanza == 'Altro' and self.distanza_altro:
            return self.distanza_altro
        return self.distanza


class Iscrizione(db.Model):
    """Modello Iscrizione (tabella di join tra User e Gara)."""
    __tablename__ = 'iscrizioni'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gara_id = db.Column(db.Integer, db.ForeignKey('gare.id'), nullable=False)
    atleta_tessera = db.Column(db.String(20), db.ForeignKey('users.tessera'), nullable=False)
    data_iscrizione = db.Column(db.DateTime, default=datetime.utcnow)
    stato_pagamento = db.Column(db.String(20), default='non_richiesto')  # non_richiesto, pagato
    metodo_pagamento = db.Column(db.String(30), nullable=True)  # paypal, carta, bonifico

    # Vincolo di unicità: un atleta può iscriversi una sola volta per gara
    __table_args__ = (
        db.UniqueConstraint('gara_id', 'atleta_tessera', name='uq_gara_atleta'),
    )


class RichiestaIscrizione(db.Model):
    """Modello per le nuove richieste di iscrizione alla società (anagrafica FIDAL)."""
    __tablename__ = 'richieste_iscrizione'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Dati Anagrafici
    nome = db.Column(db.String(50), nullable=False)
    cognome = db.Column(db.String(50), nullable=False)
    data_nascita = db.Column(db.Date, nullable=False)
    luogo_nascita = db.Column(db.String(100), nullable=False)
    codice_fiscale = db.Column(db.String(16), nullable=False)
    # Contatti e Residenza
    telefono = db.Column(db.String(20), nullable=True)
    cellulare = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    fax = db.Column(db.String(20), nullable=True)
    indirizzo = db.Column(db.String(200), nullable=False)
    cap = db.Column(db.String(5), nullable=False)
    provincia = db.Column(db.String(50), nullable=False)
    citta = db.Column(db.String(100), nullable=False)
    # Dati FIDAL
    agonista = db.Column(db.String(20), default='AGONISTA')
    iban = db.Column(db.String(34), nullable=True)
    professione = db.Column(db.String(100), nullable=True)
    titolo_studio = db.Column(db.String(50), nullable=True)
    scuola = db.Column(db.String(100), nullable=True)
    doppia_cittadinanza = db.Column(db.Boolean, default=False)
    nazione_gara = db.Column(db.String(50), default='ITALIA')
    straniero = db.Column(db.Boolean, default=False)
    cittadinanza = db.Column(db.String(50), nullable=True)
    data_scadenza_certificato = db.Column(db.Date, nullable=True)
    tipo_movimento = db.Column(db.String(50), default='Nuovo Tesseramento')
    taglia_maglia = db.Column(db.String(5), nullable=True)
    note = db.Column(db.Text, nullable=True)
    # Stato richiesta
    data_richiesta = db.Column(db.DateTime, default=datetime.utcnow)
    stato = db.Column(db.String(20), default='in_attesa')  # in_attesa, approvata, rifiutata
