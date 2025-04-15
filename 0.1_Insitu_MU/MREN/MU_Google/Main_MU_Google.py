#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Téléchargement de produits Sentinel-2 L1C complets depuis Google Cloud Storage
Auteur : Julien Masson + adaptation ChatGPT
"""

import os
import pandas as pd
import time
from datetime import timedelta
import mgrs
import gcsfs
import csv
from tqdm import tqdm  # Importer tqdm pour la barre de progression

### === CONFIGURATION === ###
# Dossier local de téléchargement
LOCAL = "/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/Match_up/1_RAW"
# LOCAL="/mnt/d/TEST"
# # Fichier CSV contenant les points à traiter
DATA = "/work/users/cverpoorter/VolTransMESKONG/Code/Code_S2_PEPS/Match_up/MU_pygeodes/DATA_POC_ONLY.csv"
# DATA="/mnt/c/Travail/Script/Script_thesis/0.1_Insitu_MU/MREN/MU_pygeodes/DATA_POC_ONLY.csv"
PATH = __file__.split("Main_MU_Google.py")[0]  # Chemin du script
print(f"PATH : {PATH}")
# Créer le dossier s’il n’existe pas
os.makedirs(LOCAL, exist_ok=True)

### === INITIALISATIONS === ###
# Lire le CSV
df = pd.read_csv(DATA)
df = df[df['Depth (m)'] <= 5]
df = df[df['BOOL_POC'] != 0]
df = df.dropna(subset=['Hour (UTC)'])

# Créer une colonne datetime complète
df['dateheure'] = pd.to_datetime(df['Date (UTC)']) + pd.to_timedelta(df['Hour (UTC)'])

# Initialiser accès Google Cloud
fs = gcsfs.GCSFileSystem(token=os.path.join(PATH,'pure-lantern-405110-43589b6d4cac.json'))  # accès public
m = mgrs.MGRS()

# Dictionnaire pour éviter de retélécharger des données déjà acquises
downloaded_keys = set()
download_log = []
def latlon_to_mgrs_parts(lat, lon):
    code = m.toMGRS(lat, lon, MGRSPrecision=5)
    return code[:2], code[2], code[3:5]  # zone, bande, carré

def list_safe_products(zone, band, square, date, window_days=1):
    """
    Recherche des produits Sentinel-2 dans un répertoire MGRS donné,
    en vérifiant les dates dans les noms de fichiers.
    """
    products = []
    base_path = f"gcp-public-data-sentinel-2/tiles/{zone}/{band}/{square}/"

    # Calculer la plage de dates et les convertir en datetime.date
    start_date = (date - timedelta(days=window_days)).date()
    end_date = (date + timedelta(days=window_days)).date()

    try:
        # Lister tous les fichiers dans le répertoire de la tuile
        files = fs.ls(base_path)
        for f in files:
            if f.endswith(".SAFE"):
                # Extraire la date du nom du fichier
                safe_name = f.split("/")[-1]
                date_str, _ = extract_date_tile_from_safe_name(safe_name)
                if date_str and start_date <= date_str <= end_date:
                    products.append(f)
    except FileNotFoundError:
        print(f"Aucun fichier trouvé dans {base_path}")
    return products

def extract_date_tile_from_safe_name(safe_name):
    # Exemple : S2A_MSIL1C_20230615T030541_N0509_R075_T48QWE_20230425T083256.SAFE
    parts = safe_name.split('_')
    if len(parts) >= 6:
        date_str = parts[2][:8]  # '20230615'
        mgrs_tile = parts[5][1:]  # 'T48QWE' → '48QWE'
        date = pd.to_datetime(date_str).date()
        return date, mgrs_tile
    return None, None

def download_safe_product(remote_safe_path, local_base_dir):
    safe_name = remote_safe_path.split("/")[-1]
    date, tile = extract_date_tile_from_safe_name(safe_name)
    key = (date, tile)

    if key in downloaded_keys:
        print(f"[SKIP] Déjà téléchargé : date={date}, tuile={tile}")
        return

    local_path = os.path.join(local_base_dir, safe_name)
    print(f"Création du dossier local : {local_path}")
    os.makedirs(local_path, exist_ok=True)

    try:
        print(f"Téléchargement de : {safe_name}")

        files = fs.find(remote_safe_path)
        for f in tqdm(files, desc=f"Téléchargement {safe_name}", unit="fichier"):
            rel_path = f[len(remote_safe_path):].lstrip("/")
            local_file_path = os.path.join(local_path, rel_path)
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            with fs.open(f, "rb") as remote_file, open(local_file_path, "wb") as local_file:
                local_file.write(remote_file.read())

        # Ajoute la clé pour éviter un doublon futur
        downloaded_keys.add(key)
        download_log.append({
            "date": str(date),
            "tile": tile,
            "safe_name": safe_name,
            "local_path": local_path
        })

    except Exception as e:
        print(f"Erreur lors du téléchargement de {safe_name} : {e}")


### === MODE TEST === ###
TEST_MODE = False  # Passez à False pour traiter tout le fichier CSV

if TEST_MODE:
    # Exemple de test : latitude, longitude et date
    test_lat = 41.5567650
    test_lon = -71.0559950
    test_date = pd.to_datetime("2016-02-18 12:00:00")

    zone, band, square = latlon_to_mgrs_parts(test_lat, test_lon)
    print(f"\n[TEST] Recherche de produits pour la tuile {zone}{band}{square} autour du {test_date.date()}")

    test_products = list_safe_products(zone, band, square, test_date)

    if not test_products:
        print(f"[TEST] Aucun produit trouvé pour {test_lat:.4f}, {test_lon:.4f} le {test_date.date()}")
    else:
        for product_path in test_products:
            download_safe_product(product_path, LOCAL)

    print("\n[TEST] Téléchargement terminé pour le mode test.")


### === TRAITEMENT PRINCIPAL === ###
for idx, row in df.iterrows():
    lat, lon = row['Lat'], row['Lon']
    date_obs = row['dateheure']
    zone, band, square = latlon_to_mgrs_parts(lat, lon)

    print(f"\nRecherche de produits pour la tuile {zone}{band}{square} autour du {date_obs.date()}")

    products = list_safe_products(zone, band, square, date_obs)

    if not products:
        print(f"Aucun produit trouvé pour {lat:.4f}, {lon:.4f} le {date_obs.date()}")
        continue

    for product_path in products:
        download_safe_product(product_path, LOCAL)
        print(f"Produits téléchargés : {product_path}")

# === Sauvegarde du log des téléchargements ===
log_file = os.path.join(LOCAL, "download_log.csv")

with open(log_file, "w", newline="") as csvfile:
    fieldnames = ["date", "tile", "safe_name", "local_path"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for entry in download_log:
        writer.writerow(entry)

print("\nTéléchargements terminés.")
print(f"Log écrit dans : {log_file}")
print(f"Nombre total de produits téléchargés : {len(download_log)}")
print(f"Nombre de produits ignorés car déjà présents : {len(downloaded_keys) - len(download_log)}")

