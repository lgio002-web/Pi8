"""Rotte per l'autenticazione (login, primo accesso, logout)."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils.mock_email import invia_password_provvisoria
from app.utils.formatters import parse_data_it

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login per Admin e Atleti registrati.
    
    L'atleta usa come username il numero tessera e come password il numero tessera.
    Al primo login effettivo l'atleta viene marcato come attivo.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Check Admin
        if username.lower() == 'pi8admin':
            admin = User.query.filter_by(tessera='ADMIN').first()
            if admin and admin.check_password(password):
                login_user(admin)
                flash('Benvenuto, Amministratore!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Credenziali non valide.', 'error')
                return render_template('login.html')

        # Login atleta con tessera (username = tessera)
        user = User.query.filter_by(tessera=username.upper()).first()

        # Fallback: prova anche ricerca per email (retrocompatibilità)
        if not user:
            user = User.query.filter_by(email=username).first()

        if user and user.password_hash and user.check_password(password):
            # Al primo login effettivo, segna come attivo
            if not user.attivo:
                user.attivo = True
                db.session.commit()
                flash(f'Benvenuto {user.nome}! Il tuo account è ora attivo.', 'success')
            else:
                flash(f'Benvenuto, {user.nome}!', 'success')
            login_user(user)
            return redirect(url_for('gare.lista'))
        elif user and not user.password_hash:
            flash('Devi prima completare l\'attivazione. Vai su "Primo accesso".', 'warning')
        else:
            flash('Username o password non corretti.', 'error')

    return render_template('login.html')


@auth_bp.route('/primo-accesso', methods=['GET', 'POST'])
def primo_accesso():
    """Primo accesso: verifica tessera + cognome + data nascita.
    
    Dopo la verifica imposta username=tessera, password=tessera.
    L'atleta NON è ancora attivo — lo diventa solo al primo login.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        tessera = request.form.get('tessera', '').strip().upper()
        cognome = request.form.get('cognome', '').strip()
        data_nascita_str = request.form.get('data_nascita', '').strip()

        data_nascita = parse_data_it(data_nascita_str)
        if not data_nascita:
            flash('Formato data non valido.', 'error')
            return render_template('primo_accesso.html')

        user = User.query.filter_by(tessera=tessera).first()

        if user and user.cognome.lower() == cognome.lower() and user.data_nascita == data_nascita:
            # Verifica se ha già una password impostata E è attivo (ha già fatto login)
            if user.attivo:
                flash('Il tuo account è già attivo. Accedi con username (tessera) e password (tessera).', 'info')
                return redirect(url_for('auth.login'))

            # Imposta le credenziali: username = tessera, password = tessera
            user.set_password(tessera)
            user.attivo = False  # Rimane non attivo finché non fa login
            db.session.commit()

            flash(
                f'Verifica completata! Le tue credenziali sono: '
                f'Username: {tessera} — Password: {tessera}. '
                f'Accedi per attivare il tuo account.',
                'success'
            )
            return redirect(url_for('auth.login'))
        else:
            flash('Dati non corrispondenti. Verifica tessera, cognome e data di nascita.', 'error')

    return render_template('primo_accesso.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('auth.login'))
