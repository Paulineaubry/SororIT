import requests
import pandas as pd
import base64
import dotenv
import os

# Charge les variables d'environnement depuis le fichier .env
dotenv.load_dotenv()

# Renseigne ici tes clés
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

# Récupère un token d'accès Spotify
def get_token(client_id, client_secret):
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    return response.json().get("access_token")

# Fonction simple de filtrage thématique
def detect_theme(text):
    text = text.lower()
    if any(word in text for word in ['cyber', 'hacking', 'sécurité']):
        return 'cybersécurité'
    elif any(word in text for word in ['game', 'jeu vidéo', 'gaming']):
        return 'gaming'
    elif any(word in text for word in ['start-up', 'entrepreneu', 'vc', 'invest']):
        return 'entrepreneuriat'
    elif any(word in text for word in ['ia', 'intelligence artificielle']):
        return 'IA'
    elif any(word in text for word in ['data', 'analyse', 'machine learning']):
        return 'data'
    else:
        return 'tech'

# Fonction pour convertir une URL Spotify en URL embed
def convert_to_embed_url(url):
    if "open.spotify.com" in url:
        return url.replace("open.spotify.com", "open.spotify.com/embed")
    return url

# Récupère les épisodes d’un podcast avec la date de publication
def get_episodes(show_id, access_token):
    episodes = []
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://api.spotify.com/v1/shows/{show_id}/episodes?market=FR&limit=50"
    while url:
        r = requests.get(url, headers=headers)
        data = r.json()
        for ep in data.get("items", []):
            episodes.append({
                "podcast_id": show_id,
                "episode_titre": ep["name"],
                "url": convert_to_embed_url(ep["external_urls"]["spotify"]),
                "description": ep.get("description", ""),
                "theme": detect_theme(ep["description"] + " " + ep["name"]),
                "release_date": ep.get("release_date", "")  # Ajout de la date de publication
            })
        url = data.get("next")
    return episodes

# IDs des podcasts
SHOWS = {
    "TechLipstick": "7JyjjDJ6benEc2LFRoW3Yy",
    "Femmes de la Tech": "6swTuYvHHQpFboNe2GhSva",
    "Cybersécurité Podcast": "33T2CyRIdoxUzola76tkuT",  # Classé en cybersécurité
    "Gaming Podcast": "5FD27omsigPxUXHZQZcXgw"  # Classé en gaming
}

# Filtrer les épisodes pour exclure ceux contenant "extrait"
def filter_episodes(episodes):
    return [ep for ep in episodes if "extrait".lower() not in ep["episode_titre"].lower()]

# Mise à jour dans main pour appliquer le filtre
def main():
    token = get_token(CLIENT_ID, CLIENT_SECRET)
    all_episodes = []
    for name, show_id in SHOWS.items():
        episodes = get_episodes(show_id, token)
        episodes = filter_episodes(episodes)  # Appliquer le filtre
        for ep in episodes:
            ep["podcast_titre"] = name
        all_episodes.extend(episodes)
    
    df = pd.DataFrame(all_episodes)
    df.to_csv("episodes_podcasts.csv", index=False)
    print(f"{len(df)} épisodes exportés dans episodes_podcasts.csv")

if __name__ == "__main__":
    main()
