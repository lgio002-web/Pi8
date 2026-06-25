"""Rotte principali (homepage, pagine pubbliche)."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage - redirect in base allo stato di login."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('gare.lista'))
    return redirect(url_for('auth.login'))
