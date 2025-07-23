from flask import Flask
from .db import get_connection
from .routes import routes  # Assure-toi que tu importes le bon blueprint

def create_app():
    app = Flask(__name__)

    # Test de connexion à Supabase
    conn = get_connection()
    if conn:
        conn.close()

    # Enregistrer les routes (IMPORTANT)
    app.register_blueprint(routes)

    return app
