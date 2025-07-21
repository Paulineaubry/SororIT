import psycopg2
from flask_app.config import DB_CONFIG

def get_connection():
    # Force IPv4 by adding 'options' to the connection configuration
    DB_CONFIG['options'] = '-c inet_protocols=ipv4'
    return psycopg2.connect(**DB_CONFIG)
