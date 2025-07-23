#!/usr/bin/env python3

from googleapiclient.discovery import build
import pandas as pd
import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")


# Fonction pour récupérer l'ID de la dernière vidéo d'une chaîne
def get_latest_video_id(channel_url, api_key):
    username = channel_url.split("@")[-1]
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Récupérer le channel ID via la custom URL
    search_response = youtube.search().list(
        q=username,
        type='channel',
        part='id',
        maxResults=1
    ).execute()

    if not search_response['items']:
        return None

    channel_id = search_response['items'][0]['id']['channelId']

    # Récupérer la dernière vidéo de la chaîne
    videos = youtube.search().list(
        channelId=channel_id,
        part="id",
        order="date",
        maxResults=1
    ).execute()

    if not videos["items"]:
        return None

    return videos["items"][0]["id"]["videoId"]

# Charger le CSV existant
df = pd.read_csv("../data/youtube_channels.csv")

# Ajouter une colonne avec l'iframe de la dernière vidéo
df["last_video_embed_url"] = df["url"].apply(
    lambda u: f"https://www.youtube.com/embed/{get_latest_video_id(u, API_KEY)}"
)

# Sauvegarder
df.to_csv("../data/youtube_channels_with_videos.csv", index=False)
print("Fichier mis à jour avec la dernière vidéo.")
