"""Rotte per la gestione delle Gare."""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Gara, Iscrizione
from app.utils.mock_email import notifica_iscrizione_gara, notifica_cancellazione_gara
from app.utils.mock_payment import processa_pagamento
from app.utils.formatters import parse_data_it

gare_bp = Blueprint('gare', __name__)


@gare_bp.route('/')
@login_required
def lista():
    """Lista di tutte le gare disponibili."""
    gare = Gara.query.order_by(Gara.data_gara.desc()).all()

    # Per ogni gara, verifica se l'atleta è già iscritto
    iscrizioni_atleta = {}
    if not current_user.is_admin:
        iscrizioni = Iscrizione.query.filter_by(atleta_tessera=current_user.tessera).all()
        iscrizioni_atleta = {i.gara_id: i for i in iscrizioni}

    return render_template('gare/lista.html', gare=gare, iscrizioni_atleta=iscrizioni_atleta)


@gare_bp.route('/<int:gara_id>')
@login_required
def dettaglio(gara_id):
    """Dettaglio di una gara con lista iscritti."""
    gara = Gara.query.get_or_404(gara_id)
    iscrizioni = Iscrizione.query.filter_by(gara_id=gara_id).all()

    # Verifica se l'atleta corrente è iscritto
    iscritto = None
    if not current_user.is_admin:
        iscritto = Iscrizione.query.filter_by(
            gara_id=gara_id, atleta_tessera=current_user.tessera
        ).first()

    return render_template('gare/dettaglio.html', gara=gara, iscrizioni=iscrizioni, iscritto=iscritto)


@gare_bp.route('/crea', methods=['GET', 'POST'])
@login_required
def crea():
    """Crea una nuova gara (solo Admin)."""
    if not current_user.is_admin:
        flash('Accesso non autorizzato.', 'error')
        return redirect(url_for('gare.lista'))

    if request.method == 'POST':
        nome_gara = request.form.get('nome_gara', '').strip()
        data_gara = parse_data_it(request.form.get('data_gara', ''))
        distanza = request.form.get('distanza', '')
        distanza_altro = request.form.get('distanza_altro', '').strip()
        costo = request.form.get('costo', '0').replace(',', '.').replace('€', '').strip()
        data_ultima = parse_data_it(request.form.get('data_ultima_iscrizione', ''))
        note = request.form.get('note', '').strip()

        if not nome_gara or not data_gara or not distanza or not data_ultima:
            flash('Compila tutti i campi obbligatori.', 'error')
            return render_template('gare/crea.html')

        try:
            costo_float = float(costo) if costo else 0.0
        except ValueError:
            costo_float = 0.0

        gara = Gara(
            nome_gara=nome_gara,
            data_gara=data_gara,
            distanza=distanza,
            distanza_altro=distanza_altro if distanza == 'Altro' else None,
            costo=costo_float,
            data_ultima_iscrizione=data_ultima,
            note=note
        )
        db.session.add(gara)
        db.session.commit()

        flash(f'Gara "{nome_gara}" creata con successo!', 'success')
        return redirect(url_for('gare.lista'))

    return render_template('gare/crea.html')


@gare_bp.route('/<int:gara_id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica(gara_id):
    """Modifica una gara esistente (solo Admin)."""
    if not current_user.is_admin:
        flash('Accesso non autorizzato.', 'error')
        return redirect(url_for('gare.lista'))

    gara = Gara.query.get_or_404(gara_id)

    if request.method == 'POST':
        gara.nome_gara = request.form.get('nome_gara', '').strip()
        gara.data_gara = parse_data_it(request.form.get('data_gara', ''))
        gara.distanza = request.form.get('distanza', '')
        gara.distanza_altro = request.form.get('distanza_altro', '').strip() if gara.distanza == 'Altro' else None
        costo = request.form.get('costo', '0').replace(',', '.').replace('€', '').strip()
        gara.costo = float(costo) if costo else 0.0
        gara.data_ultima_iscrizione = parse_data_it(request.form.get('data_ultima_iscrizione', ''))
        gara.note = request.form.get('note', '').strip()

        db.session.commit()
        flash('Gara aggiornata con successo!', 'success')
        return redirect(url_for('gare.dettaglio', gara_id=gara.id))

    return render_template('gare/modifica.html', gara=gara)


@gare_bp.route('/<int:gara_id>/elimina', methods=['POST'])
@login_required
def elimina(gara_id):
    """Elimina una gara (solo Admin)."""
    if not current_user.is_admin:
        flash('Accesso non autorizzato.', 'error')
        return redirect(url_for('gare.lista'))

    gara = Gara.query.get_or_404(gara_id)
    nome = gara.nome_gara
    db.session.delete(gara)
    db.session.commit()

    flash(f'Gara "{nome}" eliminata.', 'success')
    return redirect(url_for('gare.lista'))


@gare_bp.route('/<int:gara_id>/iscriviti', methods=['POST'])
@login_required
def iscriviti(gara_id):
    """Iscrizione di un atleta a una gara."""
    if current_user.is_admin:
        flash('Gli admin non possono iscriversi alle gare.', 'warning')
        return redirect(url_for('gare.dettaglio', gara_id=gara_id))

    gara = Gara.query.get_or_404(gara_id)

    # Verifica che le iscrizioni siano ancora aperte
    if not gara.iscrizioni_aperte:
        flash('Le iscrizioni per questa gara sono chiuse.', 'error')
        return redirect(url_for('gare.dettaglio', gara_id=gara_id))

    # Verifica che l'atleta non sia già iscritto
    esistente = Iscrizione.query.filter_by(
        gara_id=gara_id, atleta_tessera=current_user.tessera
    ).first()
    if esistente:
        flash('Sei già iscritto a questa gara.', 'warning')
        return redirect(url_for('gare.dettaglio', gara_id=gara_id))

    # Gestione pagamento
    metodo = request.form.get('metodo_pagamento', '')
    stato_pagamento = 'non_richiesto'

    if gara.costo > 0:
        if not metodo:
            flash('Seleziona un metodo di pagamento.', 'error')
            return redirect(url_for('gare.dettaglio', gara_id=gara_id))

        # Processa pagamento mock
        risultato = processa_pagamento(
            current_user.tessera, gara.nome_gara, gara.costo, metodo
        )
        if risultato['esito'] == 'OK':
            stato_pagamento = 'pagato'

    # Crea l'iscrizione
    iscrizione = Iscrizione(
        gara_id=gara_id,
        atleta_tessera=current_user.tessera,
        stato_pagamento=stato_pagamento,
        metodo_pagamento=metodo if metodo else None
    )
    db.session.add(iscrizione)
    db.session.commit()

    # Notifica email
    notifica_iscrizione_gara(current_user.email, current_user.nome, gara.nome_gara)

    flash(f'Iscrizione a "{gara.nome_gara}" confermata!', 'success')
    return redirect(url_for('gare.dettaglio', gara_id=gara_id))


@gare_bp.route('/<int:gara_id>/cancellati', methods=['POST'])
@login_required
def cancellati(gara_id):
    """Cancellazione di un atleta da una gara."""
    if current_user.is_admin:
        flash('Operazione non valida per admin.', 'warning')
        return redirect(url_for('gare.dettaglio', gara_id=gara_id))

    gara = Gara.query.get_or_404(gara_id)

    # Verifica che le iscrizioni siano ancora aperte (anche per la cancellazione)
    if not gara.iscrizioni_aperte:
        flash('Non è più possibile cancellare l\'iscrizione.', 'error')
        return redirect(url_for('gare.dettaglio', gara_id=gara_id))

    iscrizione = Iscrizione.query.filter_by(
        gara_id=gara_id, atleta_tessera=current_user.tessera
    ).first()

    if iscrizione:
        db.session.delete(iscrizione)
        db.session.commit()

        # Notifica email
        notifica_cancellazione_gara(current_user.email, current_user.nome, gara.nome_gara)

        flash(f'Iscrizione a "{gara.nome_gara}" cancellata.', 'success')
    else:
        flash('Non risulti iscritto a questa gara.', 'warning')

    return redirect(url_for('gare.dettaglio', gara_id=gara_id))
