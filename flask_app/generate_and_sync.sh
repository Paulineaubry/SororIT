#!/bin/bash
# Script pour générer les CSV et les synchroniser avec Supabase

# Répertoire de base du projet
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."

# Assurez-vous que le dossier logs existe
mkdir -p "$PROJECT_DIR/logs"

# Générer les CSV
echo "Génération des fichiers CSV..."
python "$PROJECT_DIR/scripts/episodes.py"

# Si des scripts pour générer d'autres CSV existent, ajoutez-les ici
# python "$PROJECT_DIR/scripts/fetch_youtube_latest.py"

# Synchroniser avec Supabase
echo "Synchronisation avec Supabase..."
python "$PROJECT_DIR/flask_app/sync_to_supabase.py"

echo "Opération terminée!"
