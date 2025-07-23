import psycopg2
from flask_app.config import DB_CONFIG
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_connection():
    try:
        # Force IPv4 by adding 'options' to the connection configuration
        DB_CONFIG['options'] = '-c inet_protocols=ipv4'
        conn = psycopg2.connect(**DB_CONFIG)
        logging.debug("Connexion réussie à la base de données.")
        return conn
    except Exception as e:
        logging.error(f"Erreur de connexion à la base de données : {e}")
        raise
