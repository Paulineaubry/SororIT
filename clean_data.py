
"""
clean_data.py - Script pour nettoyer et fusionner les données (associations + écoles)

- Peut être importé dans Flask (via clean_data(mode="fast"|"full")).
- Peut être exécuté directement (python clean_data.py) pour générer les fichiers JSON.
- Cherche automatiquement les fichiers dans ./data et sauvegarde dans ./output.
"""

import pandas as pd
import json
import os
from geopy.geocoders import Nominatim
from time import sleep

DATA_DIR = "./data"
OUTPUT_DIR = "./output"

ASSOS_FILE = os.path.join(DATA_DIR, "assos_geocoded.json")
ECOLES_FILE = os.path.join(DATA_DIR, "ecolesV5_enriched.xlsx")

def normalize_text(text: str) -> str:
    """Nettoie le texte : supprime espaces, accents, met en Title Case."""
    if not isinstance(text, str):
        return text
    text = text.strip()
    return text.title()

def load_and_clean_assos() -> pd.DataFrame:
    """Charge et nettoie les données associations."""
    with open(ASSOS_FILE, "r", encoding="utf-8") as f:
        assos = pd.json_normalize(json.load(f))

    for col in ["NOM", "ADRESSE", "REGION"]:
        if col in assos.columns:
            assos[col] = assos[col].apply(normalize_text)

    assos = assos.drop_duplicates(subset=["NOM", "REGION"], keep="first")
    if "LAT" not in assos.columns:
        assos["LAT"] = None
    if "LON" not in assos.columns:
        assos["LON"] = None
    return assos.reset_index(drop=True)

def load_and_clean_ecoles() -> pd.DataFrame:
    """Charge et nettoie les données écoles."""
    ecoles = pd.read_excel(ECOLES_FILE)

    # Normaliser noms de colonnes (en majuscules, sans accents)
    ecoles.columns = (
        ecoles.columns.str.upper()
        .str.replace("É", "E")
        .str.replace("È", "E")
        .str.replace(" ", "_")
    )
    for col in ["ECOLES", "LOCALISATION", "REGION"]:
        if col in ecoles.columns:
            ecoles[col] = ecoles[col].apply(normalize_text)
    ecoles = ecoles.drop_duplicates(subset=["ECOLES", "REGION"], keep="first")
    return ecoles.reset_index(drop=True)

def geocode_missing_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Complète les coordonnées manquantes via Nominatim."""
    geolocator = Nominatim(user_agent="geo_enrichment_sororit")
    def geocode(row):
        if pd.notnull(row.get("LAT")) and pd.notnull(row.get("LON")):
            return row["LAT"], row["LON"]
        query = f"{row.get('ADRESSE', '')}, {row.get('REGION', '')}, France"
        try:
            loc = geolocator.geocode(query, timeout=10)
            if loc:
                sleep(1)
                return loc.latitude, loc.longitude
        except Exception:
            return None, None
        return None, None
    df[["LAT", "LON"]] = df.apply(lambda r: pd.Series(geocode(r)), axis=1)
    return df

def clean_data(mode="fast"):
    """Nettoie et fusionne les données, génère les fichiers JSON."""
    assos = load_and_clean_assos()
    ecoles = load_and_clean_ecoles()
    if mode == "full":
        assos = geocode_missing_coords(assos)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    assos.to_json(os.path.join(OUTPUT_DIR, "assos_cleaned.json"), orient="records", indent=2, force_ascii=False)
    ecoles.to_json(os.path.join(OUTPUT_DIR, "ecoles_cleaned.json"), orient="records", indent=2, force_ascii=False)
    pd.concat([assos, ecoles], ignore_index=True).to_json(
        os.path.join(OUTPUT_DIR, "all_cleaned.json"), orient="records", indent=2, force_ascii=False
    )
    print(f"Fichiers nettoyés exportés dans {OUTPUT_DIR}")

if __name__ == "__main__":
    # Mode par défaut = rapide (pas de géocodage)
    clean_data(mode="fast")
