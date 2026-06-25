"""Rotte per il profilo Atleta e la richiesta di nuova iscrizione."""
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, RichiestaIscrizione
from app.utils.formatters import parse_data_it

atleta_bp = Blueprint('atleta', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@atleta_bp.route('/profilo')
@login_required
def profilo():
    """Visualizza il profilo dell'atleta."""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    return render_template('profilo.html')


@atleta_bp.route('/profilo/modifica', methods=['GET', 'POST'])
@login_required
def modifica_profilo():
    """Modifica il profilo dell'atleta."""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        # Aggiorna campi modificabili
        current_user.email = request.form.get('email', '').strip().lower()
        current_user.taglia_maglia = request.form.get('taglia_maglia', '').strip()

        # Gestione upload foto
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename and allowed_file(foto.filename):
                filename = secure_filename(f"{current_user.tessera}_{foto.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                foto.save(filepath)
                current_user.foto_profilo = filename

        db.session.commit()
        flash('Profilo aggiornato con successo!', 'success')
        return redirect(url_for('atleta.profilo'))

    return render_template('profilo_modifica.html')


@atleta_bp.route('/profilo/cambia-password', methods=['GET', 'POST'])
@login_required
def cambia_password():
    """Cambio password per l'atleta."""
    if request.method == 'POST':
        password_attuale = request.form.get('password_attuale', '')
        nuova_password = request.form.get('nuova_password', '')
        conferma_password = request.form.get('conferma_password', '')

        if not current_user.check_password(password_attuale):
            flash('La password attuale non è corretta.', 'error')
        elif nuova_password != conferma_password:
            flash('Le nuove password non coincidono.', 'error')
        elif len(nuova_password) < 6:
            flash('La nuova password deve essere di almeno 6 caratteri.', 'error')
        else:
            current_user.set_password(nuova_password)
            db.session.commit()
            flash('Password modificata con successo!', 'success')
            return redirect(url_for('atleta.profilo'))

    return render_template('cambia_password.html')


@atleta_bp.route('/nuovo-atleta', methods=['GET', 'POST'])
def nuovo_atleta():
    """Form pubblico per nuove richieste di tesseramento alla società (anagrafica FIDAL)."""
    if request.method == 'POST':
        richiesta = RichiestaIscrizione(
            # Tipo tesseramento
            agonista=request.form.get('agonista', 'AGONISTA'),
            tipo_movimento=request.form.get('tipo_movimento', 'Nuovo Tesseramento'),
            # Anagrafica
            nome=request.form.get('nome', '').strip().upper(),
            cognome=request.form.get('cognome', '').strip().upper(),
            data_nascita=parse_data_it(request.form.get('data_nascita', '')),
            luogo_nascita=request.form.get('luogo_nascita', '').strip().upper(),
            codice_fiscale=request.form.get('codice_fiscale', '').strip().upper(),
            # Contatti
            telefono=request.form.get('telefono', '').strip(),
            cellulare=request.form.get('cellulare', '').strip(),
            email=request.form.get('email', '').strip().lower(),
            fax=request.form.get('fax', '').strip(),
            # Residenza
            indirizzo=request.form.get('indirizzo', '').strip().upper(),
            cap=request.form.get('cap', '').strip(),
            provincia=request.form.get('provincia', '').strip().upper(),
            citta=request.form.get('citta', '').strip().upper(),
            # Bancari
            iban=request.form.get('iban', '').strip().upper(),
            # Professione
            professione=request.form.get('professione', '').strip(),
            titolo_studio=request.form.get('titolo_studio', ''),
            scuola=request.form.get('scuola', '').strip(),
            # Cittadinanza
            doppia_cittadinanza=request.form.get('doppia_cittadinanza') == 'si',
            nazione_gara=request.form.get('nazione_gara', 'ITALIA').strip().upper(),
            straniero=request.form.get('straniero') == 'si',
            cittadinanza=request.form.get('cittadinanza', '').strip(),
            # Sportivo
            data_scadenza_certificato=parse_data_it(request.form.get('data_scadenza_certificato', '')),
            taglia_maglia=request.form.get('taglia_maglia', '').strip(),
            note=request.form.get('note', '').strip()
        )

        if not richiesta.nome or not richiesta.cognome or not richiesta.data_nascita:
            flash('Compila tutti i campi obbligatori.', 'error')
            return render_template('nuovo_atleta.html')

        db.session.add(richiesta)
        db.session.commit()

        flash('Richiesta di tesseramento inviata con successo! Verrai contattato dalla segreteria.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('nuovo_atleta.html')
