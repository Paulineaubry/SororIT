
# SororIT - Nettoyage et Fusion des Données (Associations & Écoles)

Ce projet contient un script `clean_data.py` qui permet de **nettoyer, enrichir et fusionner** les données des associations et écoles pour SororIT.

## Utilisation du Script

Le script peut être utilisé de deux façons :
1. **En ligne de commande** (mode rapide par défaut)
2. **Intégré dans Flask ou tout autre code Python**

### 1. Exécution Rapide (sans géocodage)
Depuis la racine du projet :
```bash
python clean_data.py
```
Cela :
- Nettoie les fichiers `data/assos_geocoded.json` et `data/ecolesV5_enriched.xlsx`
- Supprime les doublons et normalise les colonnes
- Exporte dans `output/` :
  - `assos_cleaned.json`
  - `ecoles_cleaned.json`
  - `all_cleaned.json` (fusion)

### 2. Exécution Complète (avec géocodage)
Pour enrichir les coordonnées manquantes :
```bash
python
>>> from clean_data import clean_data
>>> clean_data(mode="full")
>>> exit()
```
Cela utilise **OpenStreetMap (Nominatim)** pour compléter les coordonnées et peut prendre du temps (1-2 secondes par ligne sans coordonnées).

## Intégration dans Flask

Vous pouvez directement intégrer le script pour que les données soient nettoyées avant utilisation :
```python
from clean_data import clean_data
import json
import os

# Nettoyer les données (mode rapide ou complet)
clean_data(mode="fast")  # ou "full" pour inclure le géocodage

# Charger les données fusionnées
output_file = os.path.join("output", "all_cleaned.json")
with open(output_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Exemple : afficher le nombre d'enregistrements
print(f"Nombre total d'entrées : {len(data)}")
```

## Dépendances
Assurez-vous d’avoir installé :
```bash
pip install pandas geopy openpyxl
```

## Organisation du Projet
```
data/           # Fichiers sources (bruts)
output/         # Résultats nettoyés (JSON)
clean_data.py   # Script principal
README_CLEAN_DATA.md  # Guide spécifique pour le script
```

## Notes
- Le **mode complet** effectue des appels API pour le géocodage (limités en vitesse).
- Les données fusionnées (`all_cleaned.json`) sont prêtes à être consommées par Flask, Streamlit ou d’autres applications.
