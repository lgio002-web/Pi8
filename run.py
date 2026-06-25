"""Entry point per avviare il server di sviluppo."""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
