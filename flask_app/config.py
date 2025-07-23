import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

print("SUPABASE_DB_URL =", os.getenv("SUPABASE_DB_URL"))


url = urlparse(os.getenv("SUPABASE_DB_URL"))

DB_CONFIG = {
    "host": url.hostname,
    "dbname": url.path[1:],
    "user": url.username,
    "password": url.password,
    "port": url.port,
    "sslmode": "require",
    "connect_timeout": 30
}
# Configuration pour la connexion à la base de données Supabase
# Assurez-vous que les variables d'environnement sont définies dans votre système ou dans un fichier .env
# Exemple de variables d'environnement :
# export SUPABASE_DB_URL="postgresql://username:password@host:port/dbname"
# export SUPABASE_PASSWORD="your_password_here"
# Vous pouvez utiliser dotenv pour charger ces variables depuis un fichier .env si nécessaire