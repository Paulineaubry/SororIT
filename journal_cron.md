
# Journal – Mise en place d’un script CRON pour mettre à jour les vidéos YouTube

## Structure de projet
```
SororIT/
├── data/
│   └── youtube_channels.csv               # Liste des chaînes YouTube
│   └── youtube_channels_with_videos.csv   # Résultat enrichi avec dernières vidéos
├── scripts/
│   └── fetch_youtube_latest.py            # Script Python qui interroge l'API YouTube
├── dbt-env/                               # Environnement virtuel Python
├── logs/
│   └── cron_youtube.log                   # Log généré automatiquement par le cron
```

---

## Étapes réalisées

### 1. Créer un environnement virtuel
```bash
python3 -m venv dbt-env
source dbt-env/bin/activate
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
pip install google-api-python-client
```

---

### 3. Créer le fichier CSV de chaînes YouTube
Dans `data/youtube_channels.csv`, on liste les chaînes et thématiques.

---

### 4. Écrire le script Python `scripts/fetch_youtube_latest.py`

- Lit `youtube_channels.csv`
- Utilise l’API YouTube pour obtenir la dernière vidéo
- Écrit un fichier enrichi `youtube_channels_with_videos.csv`

---

### 5. Rendre le script exécutable
```bash
chmod +x scripts/fetch_youtube_latest.py
```

---

### 6. Créer le dossier de logs
```bash
mkdir logs
```

---

### 7. Ouvrir l’éditeur de crontab
```bash
crontab -e
```

---

### 8. Ajouter cette ligne dans `crontab`
```bash
0 7 * * * /home/didou/projects/SororIT/dbt-env/bin/python3 /home/didou/projects/SororIT/scripts/fetch_youtube_latest.py >> /home/didou/projects/SororIT/logs/cron_youtube.log 2>&1
```

---

## Résultat
Tous les jours à **7h du matin**, le script :
- Contacte l’API YouTube
- Met à jour le fichier CSV
- Logue tout dans `logs/cron_youtube.log`

---

## Tester manuellement
```bash
python3 scripts/fetch_youtube_latest.py
cat logs/cron_youtube.log
```
