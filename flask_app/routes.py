from flask import Blueprint, jsonify, render_template, request
from flask_app.db import get_connection
import re
import pandas as pd




routes = Blueprint("routes", __name__)

@routes.route("/api/resources", methods=["GET"])
def get_resources():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT podcast_id, episode_titre, url, theme, release_date, podcast_titre
        FROM dev_pauline.good_morning_techwoman
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
    selected_theme = request.args.get("theme")

    conn = get_connection()
    cur = conn.cursor()

    if selected_theme:
        cur.execute("""
            SELECT podcast_id, episode_titre, url, theme, release_date, podcast_titre
            FROM dev_pauline.good_morning_techwoman
            WHERE theme = %s
            ORDER BY episode_titre
        """, (selected_theme,))
    else:
        cur.execute("""
            SELECT podcast_id, episode_titre, url, theme, release_date, podcast_titre
            FROM dev_pauline.good_morning_techwoman
            ORDER BY episode_titre
        """)

    rows = cur.fetchall()

    cur.execute("SELECT DISTINCT theme FROM dev_pauline.good_morning_techwoman ORDER BY theme")
    themes = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    ressources = [
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
    return render_template("index.html", ressources=ressources, themes=themes, selected_theme=selected_theme)

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

        audios = [
            {
                "episode_titre": row[0],
                "theme": row[1],
                "url": row[2]
            }
            for row in rows
        ]

    except Exception as e:
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

        audios = filtered_data.drop(columns=['description']).to_dict(orient="records")
        themes = data['theme'].unique()

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




