---
noteId: "0bb59ad0657711f0bf31d1d5570a6cd4"
tags: []

---


# Nettoyage et Fusion des Données (Associations + Écoles)

Ce module permet de nettoyer et fusionner les données des associations et écoles pour SororIT.

## Structure
- Cherche automatiquement les fichiers dans `./data` :
  - `assos_geocoded.json`
  - `ecolesV5_enriched.xlsx`
- Produit les fichiers nettoyés dans `./output` :
  - `assos_cleaned.json`
  - `ecoles_cleaned.json`
  - `all_cleaned.json` (fusionné)

## Utilisation en Local
1. Placer les fichiers sources dans le dossier `data/`.
2. Exécuter :
   ```bash
   python clean_data.py
   ```
   Par défaut, cela tourne en mode **rapide** (sans géocodage).

3. Pour forcer le **mode complet** (avec géocodage) :
   ```python
   from clean_data import clean_data
   clean_data(mode="full")
   ```

## Intégration avec Flask
- Importer le module dans votre code Flask :
  ```python
  from clean_data import clean_data

  # Exemple : lancer le nettoyage avant de charger les données
  clean_data(mode="fast")
  ```

## Dépendances
- `pandas`
- `geopy` (pour le géocodage)
- `openpyxl` (pour lire le fichier Excel)

Installez-les avec :
```bash
pip install pandas geopy openpyxl
```
