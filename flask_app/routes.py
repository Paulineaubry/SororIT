from flask import Blueprint, jsonify, render_template, request
from flask_app.db import get_connection
import re
import pandas as pd
import logging
import subprocess
import os

routes = Blueprint("routes", __name__)

# Configuration des logs
logging.basicConfig(level=logging.INFO)


@routes.route("/api/resources", methods=["GET"])
def get_resources():
    conn = get_connection()
    cur = conn.cursor()
    
    # Obtenir toutes les ressources podcasts
    cur.execute("""
        SELECT podcast_id, episode_titre, url, theme, release_date, podcast_titre, 'podcast' as type, description
        FROM public.podcasts 
        ORDER BY episode_titre
    """)
    podcast_rows = cur.fetchall()
    
    # Obtenir toutes les ressources YouTube
    cur.execute("""
        SELECT '' as podcast_id, titre as episode_titre, url, theme, '' as release_date, 
               concat(type, ' - ', titre) as podcast_titre, 'youtube' as type, description
        FROM public.youtube_channels 
        ORDER BY titre
    """)
    youtube_rows = cur.fetchall()
    
    # Fermeture du curseur et de la connexion
    cur.close()
    conn.close()

    # Combiner les résultats
    all_rows = podcast_rows + youtube_rows
    
    results = [
        {
            "podcast_id": row[0],
            "episode_titre": row[1],
            "url": row[2],
            "theme": row[3],
            "release_date": row[4],
            "podcast_titre": row[5],
            "type": row[6],
            "description": row[7]
        }
        for row in all_rows
    ]
    return jsonify(results)


@routes.route("/", methods=["GET"])
def index():
    """
    Redirection vers la page Good Morning TechWoman pour une expérience utilisateur simplifiée.
    """
    # Pour l'instant, redirigeons directement vers Good Morning TechWoman
    # Cette route pourra être modifiée par votre collègue plus tard
    
    return render_template(
        "index.html", 
        redirect_url="/good-morning-techwoman",
        page_title="SororIT - Good Morning TechWoman"
    )

@routes.route("/audios", methods=["GET"])
def get_audios_by_theme():
    import pandas as pd

    theme = request.args.get("theme")

    try:
        # Tentative de connexion à Supabase
        conn = get_connection()
        cur = conn.cursor()

        # Récupération des podcasts de la table podcasts
        if theme:
            cur.execute("""
                SELECT episode_titre, theme, url
                FROM podcasts
                WHERE theme = %s
                ORDER BY episode_titre
            """, (theme,))
        else:
            cur.execute("""
                SELECT episode_titre, theme, url
                FROM podcasts
                ORDER BY episode_titre
            """)

        rows = cur.fetchall()

        # Récupération des thèmes uniques de la table podcasts
        cur.execute("SELECT DISTINCT theme FROM podcasts ORDER BY theme")
        themes = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        audios = []
        for row in rows:
            embed_url = row[2]
            if "spotify.com" in row[2]:
                embed_url = row[2].replace("open.spotify.com/episode", "open.spotify.com/embed/episode")
                
            logging.info(f"URL originale: {row[2]}")
            logging.info(f"URL embed: {embed_url}")
            
            audios.append({
                "episode_titre": row[0],
                "theme": row[1],
                "url": row[2],
                "embed_url": embed_url
            })

    except Exception as e:
        logging.error(f"Erreur lors de la récupération des audios depuis Supabase : {e}")
        # Fallback : lecture depuis le fichier CSV
        csv_path = "../data/episodes_podcasts.csv"
        try:
            data = pd.read_csv(csv_path)
        except Exception as csv_error:
            return f"Erreur lors de la lecture du fichier CSV : {csv_error}", 500

        if theme:
            filtered_data = data[data['theme'] == theme]
        else:
            filtered_data = data

        audios = []
        for _, row in filtered_data.iterrows():
            embed_url = row['url']
            if "spotify.com" in row['url']:
                embed_url = row['url'].replace("open.spotify.com/episode", "open.spotify.com/embed/episode")
            
            logging.info(f"CSV - URL originale: {row['url']}")
            logging.info(f"CSV - URL embed: {embed_url}")
            
            audios.append({
                "episode_titre": row['episode_titre'],
                "theme": row['theme'],
                "url": row['url'],
                "embed_url": embed_url
            })
        themes = data['theme'].unique()

    # Avant de retourner le template, vérifions les données
    logging.info(f"Nombre d'audios: {len(audios)}")
    if audios:
        logging.info(f"Premier audio: {audios[0]}")
    
    return render_template("audios.html", audios=audios, selected_theme=theme, themes=themes)

@routes.route("/test_csv", methods=["GET"])
def test_csv():
    import pandas as pd

    # Chemin vers le fichier CSV
    csv_path = "../data/episodes_podcasts.csv"

    # Lire le fichier CSV
    try:
        data = pd.read_csv(csv_path)
    except Exception as e:
        return f"Erreur lors de la lecture du fichier CSV : {e}", 500

    # Filtrer les données par thème si un thème est spécifié
    theme = request.args.get("theme")
    if theme:
        filtered_data = data[data['theme'] == theme]
    else:
        filtered_data = data

    # Convertir les données filtrées en liste de dictionnaires avec URLs embed
    episodes = []
    for _, row in filtered_data.iterrows():
        episodes.append({
            "title": row['episode_titre'],  # Correction du nom de colonne
            "theme": row['theme'],
            "url": row['url'],
            "embed_url": row['url']
        })

    return render_template("audios.html", audios=episodes, themes=data['theme'].unique(), selected_theme=theme)

@routes.route("/good-morning-techwoman", methods=["GET"])
def good_morning_techwoman():
    """
    Route unique pour la fonctionnalité "Good Morning TechWoman".
    Affiche les ressources audio (podcasts) et vidéo (YouTube) filtrées par thème.
    """
    theme = request.args.get("theme")
    resource_type = request.args.get("resource_type")  # Pour filtrer par type de ressource (podcast/youtube)
    
    try:
        # Tentative de connexion à Supabase
        conn = get_connection()
        cur = conn.cursor()

        # Récupération des thèmes pour le filtre (combinaison des thèmes des deux tables)
        cur.execute("SELECT DISTINCT theme FROM podcasts UNION SELECT DISTINCT theme FROM youtube_channels ORDER BY theme")
        themes = [row[0] for row in cur.fetchall()]
        
        # Initialisation de la liste des ressources
        resources = []
        
        # Récupération des podcasts si aucun type n'est spécifié ou si le type est 'podcast'
        if not resource_type or resource_type == 'podcast':
            if theme:
                cur.execute("""
                    SELECT episode_titre as titre, theme, url, podcast_id, release_date, podcast_titre, description
                    FROM podcasts
                    WHERE theme = %s
                    ORDER BY episode_titre
                """, (theme,))
            else:
                cur.execute("""
                    SELECT episode_titre as titre, theme, url, podcast_id, release_date, podcast_titre, description
                    FROM podcasts
                    ORDER BY episode_titre
                """)
                
            podcast_rows = cur.fetchall()
            
            # Traitement des podcasts
            for row in podcast_rows:
                embed_url = row[2]  # url
                if "spotify.com" in row[2]:
                    embed_url = row[2].replace("open.spotify.com/episode", "open.spotify.com/embed/episode")
                
                logging.info(f"Podcast URL originale: {row[2]}")
                logging.info(f"Podcast URL embed: {embed_url}")
                
                resources.append({
                    "titre": row[0],
                    "theme": row[1],
                    "url": row[2],
                    "embed_url": embed_url,
                    "resource_type": "podcast",
                    "podcast_id": row[3],
                    "release_date": row[4],
                    "podcast_titre": row[5],
                    "description": row[6]
                })
        
        # Récupération des vidéos YouTube si aucun type n'est spécifié ou si le type est 'youtube'
        if not resource_type or resource_type == 'youtube':
            if theme:
                cur.execute("""
                    SELECT titre, theme, url, type, description, last_video_embed_url
                    FROM youtube_channels
                    WHERE theme = %s
                    ORDER BY titre
                """, (theme,))
            else:
                cur.execute("""
                    SELECT titre, theme, url, type, description, last_video_embed_url
                    FROM youtube_channels
                    ORDER BY titre
                """)
                
            youtube_rows = cur.fetchall()
            
            # Traitement des vidéos YouTube
            for row in youtube_rows:
                embed_url = row[5] if row[5] else row[2]  # Utiliser last_video_embed_url si disponible, sinon url
                
                logging.info(f"YouTube URL originale: {row[2]}")
                logging.info(f"YouTube URL embed: {embed_url}")
                
                resources.append({
                    "titre": row[0],
                    "theme": row[1],
                    "url": row[2],
                    "embed_url": embed_url,
                    "resource_type": "youtube",
                    "podcast_id": "",
                    "release_date": "",
                    "podcast_titre": f"{row[3]} - {row[0]}",  # type - titre
                    "description": row[4]
                })
        
        cur.close()
        conn.close()

    except Exception as e:
        logging.error(f"Erreur lors de la récupération des ressources depuis Supabase : {e}")
        
        # Fallback : lecture depuis les fichiers CSV
        resources = []
        all_themes = set()
        
        # 1. Lecture des podcasts
        try:
            podcasts_path = "data/episodes_podcasts.csv"
            podcasts_data = pd.read_csv(podcasts_path)
            
            # Ajout des thèmes à l'ensemble
            all_themes.update(podcasts_data['theme'].unique())
            
            # Filtrage par thème si nécessaire
            if theme:
                filtered_podcasts = podcasts_data[podcasts_data['theme'] == theme]
            else:
                filtered_podcasts = podcasts_data
                
            # Traitement des podcasts pour l'affichage
            for _, row in filtered_podcasts.iterrows():
                embed_url = row['url']
                if "spotify.com" in row['url']:
                    embed_url = row['url'].replace("open.spotify.com/episode", "open.spotify.com/embed/episode")
                
                resources.append({
                    "titre": row['episode_titre'],
                    "theme": row['theme'],
                    "url": row['url'],
                    "embed_url": embed_url,
                    "resource_type": "podcast",
                    "release_date": row.get('release_date', ''),
                    "podcast_titre": row.get('podcast_titre', '')
                })
                
        except Exception as podcast_error:
            logging.error(f"Erreur lors de la lecture du fichier podcasts : {podcast_error}")
            
        # 2. Lecture des vidéos YouTube
        try:
            youtube_path = "data/youtube_channels_with_videos.csv"
            youtube_data = pd.read_csv(youtube_path)
            
            # Ajout des thèmes à l'ensemble
            all_themes.update(youtube_data['theme'].unique())
            
            # Filtrage par thème si nécessaire
            if theme:
                filtered_youtube = youtube_data[youtube_data['theme'].str.contains(theme, case=False, na=False)]
            else:
                filtered_youtube = youtube_data
                
            # Traitement des vidéos YouTube pour l'affichage
            for _, row in filtered_youtube.iterrows():
                resources.append({
                    "titre": row['titre'],
                    "theme": row['theme'],
                    "url": row['url'],
                    "embed_url": row['last_video_embed_url'],
                    "resource_type": "youtube",
                    "description": row.get('description', '')
                })
                
        except Exception as youtube_error:
            logging.error(f"Erreur lors de la lecture du fichier YouTube : {youtube_error}")
            
        # Conversion de l'ensemble des thèmes en liste
        themes = sorted(list(all_themes))
            
        # Si aucun fichier n'a pu être lu
        if not resources:
            return "Erreur lors de la lecture des fichiers de ressources", 500
            
        # Filtrage par type de ressource si nécessaire
        if resource_type:
            resources = [res for res in resources if res['resource_type'] == resource_type]
    
    return render_template(
        "good_morning_techwoman.html",
        resources=resources,
        themes=themes,
        selected_theme=theme,
        selected_resource_type=resource_type,
        page_title="Good Morning TechWoman - Ressources Audio et Vidéo"
    )

@routes.route("/sync_to_supabase", methods=["GET"])
def sync_to_supabase():
    """
    Route pour synchroniser les fichiers CSV avec Supabase.
    Cette route exécute le script de synchronisation et affiche le résultat.
    """
    try:
        # Import et utilisation directe du script de synchronisation dans flask_app
        from flask_app.sync_to_supabase import main as sync_main
        
        # Exécution du script en Python directement
        import io
        import contextlib
        
        # Capturer la sortie pour l'afficher dans le template
        f = io.StringIO()
        with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            sync_result = sync_main()
            
        result_output = f.getvalue()
        
        # Log du résultat
        logging.info(f"Synchronisation avec Supabase exécutée avec succès: {result_output}")
        
        # Retourner un message de succès
        return render_template(
            "sync_result.html", 
            success=sync_result, 
            message="Synchronisation avec Supabase effectuée avec succès!" if sync_result else "Des problèmes sont survenus lors de la synchronisation.",
            output=result_output
        )
    except Exception as e:
        # Log de l'erreur
        logging.error(f"Erreur lors de la synchronisation avec Supabase: {str(e)}")
        
        # Retourner un message d'erreur
        return render_template(
            "sync_result.html", 
            success=False, 
            message="Erreur lors de la synchronisation avec Supabase.",
            output=str(e)
        )




