#!/usr/bin/env python
"""
Script pour synchroniser les fichiers CSV locaux avec la table resources_techwoman dans Supabase.
Ce script:
1. Lit les fichiers CSV de podcasts et de vidéos You        cursor.close()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la vérification/création des tables: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return False Se connecte à la base de données Supabase
3. Met à jour la table resources_techwoman avec les données des CSV
"""

import os
import sys
import pandas as pd
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Charger les variables d'environnement depuis le fichier .env dans le dossier flask_app
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
print(f"Chargement du fichier .env depuis: {dotenv_path}")

# Créer le logger avant de l'utiliser
logger = logging.getLogger(__name__)

# Import des modules flask_app avec gestion des erreurs
# Définir une variable pour stocker la fonction get_connection et DB_CONFIG
get_connection = None
DB_CONFIG = None

# Ajouter le répertoire parent au chemin de recherche Python
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    logger.info(f"Ajout de {parent_dir} au chemin de recherche Python")

# Ajouter le répertoire courant au chemin de recherche Python
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logger.info(f"Ajout de {current_dir} au chemin de recherche Python")

try:
    # Tenter d'importer db depuis le même répertoire
    import db
    get_connection = db.get_connection
    logger.info("Module db importé avec succès (import direct)")
    
    import config
    DB_CONFIG = config.DB_CONFIG
    logger.info("Module config importé avec succès (import direct)")
except ImportError:
    try:
        # Tenter d'importer depuis flask_app
        from flask_app import db, config
        get_connection = db.get_connection
        DB_CONFIG = config.DB_CONFIG
        logger.info("Modules importés avec succès (import depuis flask_app)")
    except ImportError:
        # Dernier recours: définir get_connection manuellement
        logger.warning("Échec des imports des modules db et config, utilisation du fallback")
        try:
            # Importation manuelle des dépendances nécessaires
            import psycopg2
            from dotenv import load_dotenv
            from urllib.parse import urlparse
            import os
            
            # Charger les variables d'environnement
            load_dotenv(dotenv_path)
            
            # Configurer DB_CONFIG manuellement
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
            
            # Définir la fonction get_connection manuellement
            def get_connection():
                try:
                    # Force IPv4 by adding 'options' to the connection configuration
                    conn_config = DB_CONFIG.copy()
                    conn_config['options'] = '-c inet_protocols=ipv4'
                    conn = psycopg2.connect(**conn_config)
                    logger.debug("Connexion réussie à la base de données (fallback).")
                    return conn
                except Exception as e:
                    logger.error(f"Erreur de connexion à la base de données (fallback): {e}")
                    raise
                    
            logger.info("Fonction get_connection et DB_CONFIG définies manuellement avec succès")
        except Exception as e:
            logger.critical(f"Impossible de configurer le fallback: {e}")
            raise

# S'assurer que le dossier logs existe
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(logs_dir, 'sync_supabase.log'))
    ]
)

# Chemins des fichiers CSV (un niveau au-dessus du dossier flask_app)
PODCASTS_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/episodes_podcasts.csv'))
YOUTUBE_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/youtube_channels_with_videos.csv'))

def read_csv_files():
    """Lit les fichiers CSV de podcasts et de vidéos YouTube et les prépare pour l'insertion."""
    podcasts_data = []
    youtube_data = []
    
    # Lecture des podcasts
    try:
        podcasts_df = pd.read_csv(PODCASTS_CSV_PATH)
        logger.info(f"Fichier de podcasts lu avec succès: {len(podcasts_df)} entrées.")
        
        for _, row in podcasts_df.iterrows():
            # Utiliser la valeur 'type' du CSV si elle existe, sinon définir à 'podcast'
            entry_type = row.get("type", "podcast") if "type" in row else "podcast"
            
            podcasts_data.append({
                "podcast_id": row.get("podcast_id", ""),
                "episode_titre": row["episode_titre"],
                "url": row["url"],
                "theme": row["theme"],
                "release_date": row.get("release_date", ""),
                "podcast_titre": row.get("podcast_titre", ""),
                "type": entry_type,
                "description": row.get("description", "")
            })
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier de podcasts: {e}")
    
    # Lecture des vidéos YouTube
    try:
        youtube_df = pd.read_csv(YOUTUBE_CSV_PATH)
        logger.info(f"Fichier YouTube lu avec succès: {len(youtube_df)} entrées.")
        
        # Vérifier si la colonne 'last_video_embed_url' existe
        has_embed_url = "last_video_embed_url" in youtube_df.columns
        if not has_embed_url:
            logger.warning("La colonne 'last_video_embed_url' n'existe pas dans le fichier YouTube CSV")
        
        for _, row in youtube_df.iterrows():
            youtube_entry = {
                "podcast_id": "",  # Pas applicable pour les vidéos YouTube
                "episode_titre": row["titre"],
                "url": row["url"],
                "theme": row["theme"],
                "release_date": "",  # Pas toujours disponible pour les vidéos
                "podcast_titre": row["type"] + " - " + row["titre"],
                "type": "youtube",
                "description": row.get("description", "")
            }
            
            # Ajout de la colonne last_video_embed_url si elle existe dans le fichier CSV
            if has_embed_url:
                youtube_entry["last_video_embed_url"] = row["last_video_embed_url"]
            
            youtube_data.append(youtube_entry)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier YouTube: {e}")
    
    # Combinaison des données
    all_data = podcasts_data + youtube_data
    logger.info(f"Total d'entrées à synchroniser: {len(all_data)}")
    
    return all_data

def ensure_podcasts_table_exists(conn):
    """Vérifie si la table podcasts existe, la crée si nécessaire, et s'assure que toutes les colonnes nécessaires existent."""
    try:
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'podcasts'
        );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        # Si la table n'existe pas, la créer
        if not table_exists:
            logger.info("La table podcasts n'existe pas, création en cours...")
            cursor.execute("""
            CREATE TABLE public.podcasts (
                id SERIAL PRIMARY KEY,
                podcast_id TEXT,
                episode_titre TEXT,
                url TEXT,
                theme TEXT,
                release_date TEXT,
                podcast_titre TEXT,
                description TEXT
            );
            """)
            conn.commit()
            logger.info("Table podcasts créée avec succès.")
        else:
            logger.info("La table podcasts existe déjà.")
            
            # Vérifier si toutes les colonnes nécessaires existent
            required_columns = ["podcast_id", "episode_titre", "url", "theme", "release_date", "podcast_titre", "description"]
            for col in required_columns:
                cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'podcasts'
                    AND column_name = %s
                );
                """, (col,))
                
                column_exists = cursor.fetchone()[0]
                
                if not column_exists:
                    logger.info(f"La colonne '{col}' n'existe pas dans la table podcasts, ajout en cours...")
                    cursor.execute(f"""
                    ALTER TABLE public.podcasts
                    ADD COLUMN {col} TEXT;
                    """)
                    conn.commit()
                    logger.info(f"Colonne '{col}' ajoutée avec succès à la table podcasts.")
        
        cursor.close()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la vérification/création de la table podcasts: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return False

def ensure_youtube_table_exists(conn):
    """Vérifie si la table youtube_channels existe, la crée si nécessaire, et s'assure que toutes les colonnes nécessaires existent."""
    try:
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'youtube_channels'
        );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        # Si la table n'existe pas, la créer
        if not table_exists:
            logger.info("La table youtube_channels n'existe pas, création en cours...")
            cursor.execute("""
            CREATE TABLE public.youtube_channels (
                id SERIAL PRIMARY KEY,
                titre TEXT,
                url TEXT,
                theme TEXT,
                type TEXT,
                description TEXT,
                last_video_embed_url TEXT
            );
            """)
            conn.commit()
            logger.info("Table youtube_channels créée avec succès.")
        else:
            logger.info("La table youtube_channels existe déjà.")
            
            # Vérifier si toutes les colonnes nécessaires existent
            required_columns = ["titre", "url", "theme", "type", "description", "last_video_embed_url"]
            for col in required_columns:
                cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'youtube_channels'
                    AND column_name = %s
                );
                """, (col,))
                
                column_exists = cursor.fetchone()[0]
                
                if not column_exists:
                    logger.info(f"La colonne '{col}' n'existe pas dans la table youtube_channels, ajout en cours...")
                    cursor.execute(f"""
                    ALTER TABLE public.youtube_channels
                    ADD COLUMN {col} TEXT;
                    """)
                    conn.commit()
                    logger.info(f"Colonne '{col}' ajoutée avec succès à la table youtube_channels.")
        
        cursor.close()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la vérification/création de la table youtube_channels: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return False

def ensure_tables_exist(conn):
    """Vérifie si les tables podcasts et youtube_channels existent, les crée si nécessaire."""
    try:
        podcasts_ok = ensure_podcasts_table_exists(conn)
        youtube_ok = ensure_youtube_table_exists(conn)
        
        return podcasts_ok and youtube_ok
    except Exception as e:
        logger.error(f"Erreur lors de la vérification/création des tables: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return False

def create_connection_fallback():
    """Crée une connexion à la base de données en utilisant directement DB_CONFIG."""
    try:
        if not DB_CONFIG:
            raise Exception("DB_CONFIG n'est pas défini")
        
        # Force IPv4 by adding 'options' to the connection configuration
        db_config = DB_CONFIG.copy()
        db_config['options'] = '-c inet_protocols=ipv4'
        conn = psycopg2.connect(**db_config)
        logger.debug("Connexion réussie à la base de données (fallback).")
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données (fallback) : {e}")
        raise

def sync_to_supabase(data):
    """Synchronise les données avec les tables podcasts et youtube_channels dans Supabase."""
    if not data:
        logger.error("Aucune donnée à synchroniser.")
        return False
    
    # Séparer les données par type
    podcasts_data = [item for item in data if item["type"] == "podcast"]
    youtube_data = [item for item in data if item["type"] == "youtube"]
    
    logger.info(f"Données séparées: {len(podcasts_data)} podcasts et {len(youtube_data)} vidéos YouTube")
    
    try:
        # Utilisation de la fonction get_connection du module db ou fallback si non disponible
        if get_connection:
            conn = get_connection()
            logger.info("Utilisation de la fonction get_connection importée")
        else:
            logger.warning("Fonction get_connection non disponible, utilisation du fallback")
            conn = create_connection_fallback()
        
        # S'assurer que les tables existent
        if not ensure_tables_exist(conn):
            logger.error("Impossible de s'assurer que les tables existent. Annulation de la synchronisation.")
            return False
        
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Traitement des podcasts
        if podcasts_data:
            # Créer une table temporaire pour les podcasts
            cursor.execute("""
            CREATE TEMP TABLE temp_podcasts (
                podcast_id TEXT,
                episode_titre TEXT,
                url TEXT,
                theme TEXT,
                release_date TEXT,
                podcast_titre TEXT,
                description TEXT
            ) ON COMMIT DROP;
            """)
            
            # Insérer les données dans la table temporaire
            podcast_insert_data = []
            for item in podcasts_data:
                podcast_insert_data.append((
                    item["podcast_id"],
                    item["episode_titre"],
                    item["url"],
                    item["theme"],
                    item["release_date"],
                    item["podcast_titre"],
                    item["description"]
                ))
            
            execute_values(cursor, """
                INSERT INTO temp_podcasts 
                (podcast_id, episode_titre, url, theme, release_date, podcast_titre, description) 
                VALUES %s
                """, podcast_insert_data)
            
            # Sauvegarder l'état actuel de la table dans une sauvegarde horodatée
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS podcasts_backup_{timestamp} AS 
            SELECT * FROM public.podcasts;
            """)
            logger.info(f"Sauvegarde effectuée dans podcasts_backup_{timestamp}")
            
            # Supprimer les entrées actuelles
            cursor.execute("DELETE FROM public.podcasts;")
            
            # Insérer les nouvelles données depuis la table temporaire
            cursor.execute("""
            INSERT INTO public.podcasts
            (podcast_id, episode_titre, url, theme, release_date, podcast_titre, description)
            SELECT 
                podcast_id, 
                episode_titre, 
                url, 
                theme, 
                release_date, 
                podcast_titre, 
                description
            FROM temp_podcasts;
            """)
            
            # Statistiques de synchronisation des podcasts
            cursor.execute("SELECT COUNT(*) FROM public.podcasts")
            podcasts_count = cursor.fetchone()[0]
            logger.info(f"Synchronisation des podcasts terminée avec succès. Nombre d'entrées: {podcasts_count}")
        
        # Traitement des vidéos YouTube
        if youtube_data:
            # Créer une table temporaire pour les vidéos YouTube
            cursor.execute("""
            CREATE TEMP TABLE temp_youtube (
                titre TEXT,
                url TEXT,
                theme TEXT,
                type TEXT,
                description TEXT,
                last_video_embed_url TEXT
            ) ON COMMIT DROP;
            """)
            
            # Insérer les données dans la table temporaire
            youtube_insert_data = []
            for item in youtube_data:
                # Vérifier si last_video_embed_url est présent dans l'item
                last_video_embed_url = item.get("last_video_embed_url", "")
                
                youtube_insert_data.append((
                    item["episode_titre"],  # Le titre de l'épisode devient le titre de la vidéo
                    item["url"],
                    item["theme"],
                    item["podcast_titre"].split(" - ")[0],  # On récupère le type depuis podcast_titre
                    item["description"],
                    last_video_embed_url
                ))
            
            execute_values(cursor, """
                INSERT INTO temp_youtube 
                (titre, url, theme, type, description, last_video_embed_url) 
                VALUES %s
                """, youtube_insert_data)
            
            # Sauvegarder l'état actuel de la table dans une sauvegarde horodatée
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS youtube_channels_backup_{timestamp} AS 
            SELECT * FROM public.youtube_channels;
            """)
            logger.info(f"Sauvegarde effectuée dans youtube_channels_backup_{timestamp}")
            
            # Supprimer les entrées actuelles
            cursor.execute("DELETE FROM public.youtube_channels;")
            
            # Insérer les nouvelles données depuis la table temporaire
            cursor.execute("""
            INSERT INTO public.youtube_channels
            (titre, url, theme, type, description, last_video_embed_url)
            SELECT 
                titre, 
                url, 
                theme, 
                type, 
                description,
                last_video_embed_url
            FROM temp_youtube;
            """)
            
            # Statistiques de synchronisation des vidéos YouTube
            cursor.execute("SELECT COUNT(*) FROM public.youtube_channels")
            youtube_count = cursor.fetchone()[0]
            logger.info(f"Synchronisation des vidéos YouTube terminée avec succès. Nombre d'entrées: {youtube_count}")
        
        # Valider les modifications
        conn.commit()
        logger.info(f"Synchronisation totale terminée avec succès.")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation avec Supabase: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False

def main():
    """Fonction principale d'exécution du script."""
    logger.info("Démarrage de la synchronisation avec Supabase...")
    
    try:
        # Lecture des fichiers CSV
        data = read_csv_files()
        
        # Synchronisation avec Supabase
        if sync_to_supabase(data):
            logger.info("Synchronisation avec Supabase terminée avec succès.")
            return True
        else:
            logger.error("La synchronisation avec Supabase a échoué.")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du script: {e}")
        return False

if __name__ == "__main__":
    main()
