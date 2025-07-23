from flask import Blueprint, jsonify, render_template, request
from flask_app.db import get_connection
import re
import pandas as pd
import logging

routes = Blueprint("routes", __name__)

# Configuration des logs
logging.basicConfig(level=logging.INFO)


@routes.route("/api/resources", methods=["GET"])
def get_resources():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT podcast_id, episode_titre, url, theme, release_date, podcast_titre
        FROM public.resources_techwoman 
        ORDER BY episode_titre
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = [
        {
            "podcast_id": row[0],
            "episode_titre": row[1],
            "url": row[2],
            "theme": row[3],
            "release_date": row[4],
            "podcast_titre": row[5]
        }
        for row in rows
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

        if theme:
            cur.execute("""
                SELECT episode_titre, theme, url
                FROM resources_techwoman
                WHERE theme = %s
                ORDER BY episode_titre
            """, (theme,))
        else:
            cur.execute("""
                SELECT episode_titre, theme, url
                FROM resources_techwoman
                ORDER BY episode_titre
            """)

        rows = cur.fetchall()

        cur.execute("SELECT DISTINCT theme FROM resources_techwoman ORDER BY theme")
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
    Affiche les ressources audio filtrées par thème.
    """
    theme = request.args.get("theme")
    
    try:
        # Tentative de connexion à Supabase
        conn = get_connection()
        cur = conn.cursor()

        # Récupération des thèmes pour le filtre
        cur.execute("SELECT DISTINCT theme FROM resources_techwoman ORDER BY theme")
        themes = [row[0] for row in cur.fetchall()]
        
        # Si un thème est sélectionné, filtrer les ressources
        if theme:
            cur.execute("""
                SELECT episode_titre, theme, url
                FROM resources_techwoman
                WHERE theme = %s
                ORDER BY episode_titre
            """, (theme,))
        else:
            cur.execute("""
                SELECT episode_titre, theme, url
                FROM resources_techwoman
                ORDER BY episode_titre
            """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Traitement des ressources pour l'affichage
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
            
            # Récupération des thèmes pour le filtre
            themes = data['theme'].unique()
            
            # Si un thème est sélectionné, filtrer les ressources
            if theme:
                filtered_data = data[data['theme'] == theme]
            else:
                filtered_data = data

            # Traitement des ressources pour l'affichage
            audios = []
            for _, row in filtered_data.iterrows():
                embed_url = row['url']
                if "spotify.com" in row['url']:
                    embed_url = row['url'].replace("open.spotify.com/episode", "open.spotify.com/embed/episode")
                
                audios.append({
                    "episode_titre": row['episode_titre'],
                    "theme": row['theme'],
                    "url": row['url'],
                    "embed_url": embed_url
                })
                
        except Exception as csv_error:
            logging.error(f"Erreur lors de la lecture du fichier CSV : {csv_error}")
            return f"Erreur lors de la lecture du fichier CSV : {csv_error}", 500
    
    return render_template(
        "good_morning_techwoman.html",
        audios=audios,
        themes=themes,
        selected_theme=theme,
        page_title="Good Morning TechWoman - Ressources Audio et Vidéo"
    )




