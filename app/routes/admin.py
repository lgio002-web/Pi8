"""Rotte per il pannello Admin."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Gara, Iscrizione, RichiestaIscrizione
from app.utils.formatters import parse_data_it

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decoratore per limitare l'accesso agli admin."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accesso riservato agli amministratori.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Dashboard admin con panoramica generale."""
    totale_atleti = User.query.filter(User.ruolo == 'atleta').count()
    atleti_attivi = User.query.filter(User.ruolo == 'atleta', User.attivo == True).count()
    totale_gare = Gara.query.count()
    richieste_pendenti = RichiestaIscrizione.query.filter_by(stato='in_attesa').count()

    return render_template('admin/dashboard.html',
                           totale_atleti=totale_atleti,
                           atleti_attivi=atleti_attivi,
                           totale_gare=totale_gare,
                           richieste_pendenti=richieste_pendenti)


@admin_bp.route('/atleti')
@login_required
@admin_required
def atleti():
    """Lista di tutti gli atleti."""
    atleti_list = User.query.filter(User.ruolo == 'atleta').order_by(User.cognome).all()
    return render_template('admin/atleti.html', atleti=atleti_list)


@admin_bp.route('/atleti/nuovo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuovo_atleta():
    """Crea un nuovo atleta manualmente."""
    if request.method == 'POST':
        tessera = request.form.get('tessera', '').strip().upper()
        if not tessera:
            flash('Il numero tessera è obbligatorio.', 'error')
            return render_template('admin/atleta_form.html', atleta=None)

        if User.query.filter_by(tessera=tessera).first():
            flash('Tessera già esistente.', 'error')
            return render_template('admin/atleta_form.html', atleta=None)

        nuovo = User(
            tessera=tessera,
            nome=request.form.get('nome', '').strip().upper(),
            cognome=request.form.get('cognome', '').strip().upper(),
            data_nascita=parse_data_it(request.form.get('data_nascita', '')),
            categoria=request.form.get('categoria', '').strip(),
            luogo_nascita=request.form.get('luogo_nascita', '').strip().upper(),
            data_tesseramento=parse_data_it(request.form.get('data_tesseramento', '')),
            taglia_maglia=request.form.get('taglia_maglia', '').strip(),
            data_scadenza_certificato=parse_data_it(request.form.get('data_scadenza_certificato', '')),
            ruolo='atleta',
            attivo=False
        )
        db.session.add(nuovo)
        db.session.commit()
        flash(f'Atleta {nuovo.cognome} {nuovo.nome} creato con tessera {tessera}.', 'success')
        return redirect(url_for('admin.atleti'))

    return render_template('admin/atleta_form.html', atleta=None)


@admin_bp.route('/atleti/<tessera>/modifica', methods=['GET', 'POST'])
@login_required
@admin_required
def modifica_atleta(tessera):
    """Modifica i dati di un atleta."""
    atleta = User.query.get_or_404(tessera)

    if request.method == 'POST':
        atleta.nome = request.form.get('nome', '').strip().upper()
        atleta.cognome = request.form.get('cognome', '').strip().upper()
        atleta.data_nascita = parse_data_it(request.form.get('data_nascita', ''))
        atleta.categoria = request.form.get('categoria', '').strip()
        atleta.luogo_nascita = request.form.get('luogo_nascita', '').strip().upper()
        atleta.data_tesseramento = parse_data_it(request.form.get('data_tesseramento', ''))
        atleta.taglia_maglia = request.form.get('taglia_maglia', '').strip()
        atleta.data_scadenza_certificato = parse_data_it(request.form.get('data_scadenza_certificato', ''))

        db.session.commit()
        flash(f'Atleta {atleta.cognome} {atleta.nome} aggiornato.', 'success')
        return redirect(url_for('admin.atleti'))

    return render_template('admin/atleta_form.html', atleta=atleta)


@admin_bp.route('/atleti/<tessera>/elimina', methods=['POST'])
@login_required
@admin_required
def elimina_atleta(tessera):
    """Elimina un atleta."""
    atleta = User.query.get_or_404(tessera)
    nome_completo = f"{atleta.cognome} {atleta.nome}"
    db.session.delete(atleta)
    db.session.commit()
    flash(f'Atleta {nome_completo} eliminato.', 'success')
    return redirect(url_for('admin.atleti'))


@admin_bp.route('/atleti/<tessera>/reset-attivazione', methods=['POST'])
@login_required
@admin_required
def reset_attivazione(tessera):
    """Resetta l'attivazione di un atleta: rimuove password e stato attivo.
    L'atleta dovrà rifare il primo accesso."""
    atleta = User.query.get_or_404(tessera)
    atleta.password_hash = None
    atleta.attivo = False
    db.session.commit()
    flash(f'Attivazione di {atleta.cognome} {atleta.nome} resettata. Potrà rifare il primo accesso.', 'success')
    return redirect(url_for('admin.atleti'))


@admin_bp.route('/richieste')
@login_required
@admin_required
def richieste():
    """Lista delle richieste di iscrizione pendenti."""
    richieste_list = RichiestaIscrizione.query.order_by(RichiestaIscrizione.data_richiesta.desc()).all()
    return render_template('admin/richieste.html', richieste=richieste_list)


@admin_bp.route('/richieste/<int:richiesta_id>/approva', methods=['POST'])
@login_required
@admin_required
def approva_richiesta(richiesta_id):
    """Approva una richiesta di iscrizione e crea l'utente."""
    richiesta = RichiestaIscrizione.query.get_or_404(richiesta_id)

    if richiesta.stato != 'in_attesa':
        flash('Questa richiesta è già stata gestita.', 'warning')
        return redirect(url_for('admin.richieste'))

    # Genera un numero tessera progressivo
    ultimo = User.query.filter(User.tessera.like('PI8%')).order_by(User.tessera.desc()).first()
    if ultimo:
        try:
            num = int(ultimo.tessera.replace('PI8', '')) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    nuova_tessera = f"PI8{num:04d}"

    # Crea il nuovo utente
    nuovo_utente = User(
        tessera=nuova_tessera,
        nome=richiesta.nome,
        cognome=richiesta.cognome,
        data_nascita=richiesta.data_nascita,
        luogo_nascita=richiesta.luogo_nascita,
        email=richiesta.email,
        taglia_maglia=richiesta.taglia_maglia,
        ruolo='atleta',
        attivo=False
    )
    db.session.add(nuovo_utente)

    richiesta.stato = 'approvata'
    db.session.commit()

    flash(f'Richiesta approvata. Nuova tessera: {nuova_tessera}', 'success')
    return redirect(url_for('admin.richieste'))


@admin_bp.route('/richieste/<int:richiesta_id>/rifiuta', methods=['POST'])
@login_required
@admin_required
def rifiuta_richiesta(richiesta_id):
    """Rifiuta una richiesta di iscrizione."""
    richiesta = RichiestaIscrizione.query.get_or_404(richiesta_id)

    if richiesta.stato != 'in_attesa':
        flash('Questa richiesta è già stata gestita.', 'warning')
        return redirect(url_for('admin.richieste'))

    richiesta.stato = 'rifiutata'
    db.session.commit()

    flash('Richiesta rifiutata.', 'success')
    return redirect(url_for('admin.richieste'))
