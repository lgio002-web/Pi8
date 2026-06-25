"""Factory dell'applicazione Flask per ASD Pi8 Running."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Effettua il login per accedere a questa pagina.'
login_manager.login_message_category = 'warning'


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Assicura che le directory necessarie esistano
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Inizializza le estensioni
    db.init_app(app)
    login_manager.init_app(app)

    # Registra i filtri Jinja2 personalizzati
    from app.utils.formatters import format_euro, format_data_it
    app.jinja_env.filters['euro'] = format_euro
    app.jinja_env.filters['data_it'] = format_data_it

    # Funzioni globali Jinja2
    from datetime import date as _date
    app.jinja_env.globals['now'] = lambda: _date.today()

    # Registra i blueprint
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.gare import gare_bp
    from app.routes.admin import admin_bp
    from app.routes.atleta import atleta_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(gare_bp, url_prefix='/gare')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(atleta_bp, url_prefix='/atleta')

    # User loader per Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    return app
