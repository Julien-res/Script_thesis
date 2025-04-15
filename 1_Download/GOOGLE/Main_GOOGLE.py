#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Téléchargement de produits Sentinel-2 L1C depuis Google Cloud Storage
Auteur : Julien Masson (adapté pour GCS)
"""

import os
import calendar
import argparse
import gcsfs
import mgrs
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta
import csv

# Initialisation de GCS et MGRS
fs = None
m = mgrs.MGRS()

# Dictionnaire pour éviter les doublons de téléchargement
downloaded_keys = set()
download_log = []

def parse_arguments():
    parser = argparse.ArgumentParser(description="Téléchargement de Sentinel-2 depuis GCS")
    requiredNamed = parser.add_argument_group('Arguments requis')
    requiredNamed.add_argument("-y", "--year", type=int, dest='year', help="Année de l'image", required=True)
    requiredNamed.add_argument("-t", "--tile", type=str, dest='tile', help="Tuile(s) à télécharger (e.g. 31TFJ)", nargs='+', required=True)
    requiredNamed.add_argument("-c", "--credential", type=str, dest='cred', help="Chemin vers le fichier de credentials GCS", required=True)
    requiredNamed.add_argument("-d", "--downloaded_csv", type=str, dest='downloaded_csv', help="Chemin vers le fichier CSV des téléchargements existants", required=True)
    parser.add_argument("-o", "--output", type=str, dest='output', help="Chemin de sortie pour les fichiers téléchargés", default=None)
    parser.add_argument("-m", "--month", type=int, dest='month', help="Mois de l'image")
    return parser.parse_args()

def setup_download_path(output):
    if output is None:
        workspace = 'gcs_workspace'
        if not os.path.isdir(workspace):
            os.mkdir(workspace)
        return os.path.join(os.getcwd(), workspace)
    return output

def get_date_range(year, month):
    if month:
        if month < 1 or month > 12:
            raise ValueError("Le mois doit être entre 1 et 12.")
        month_str = f"{month:02d}"
        start = f"{year}-{month_str}-01"
        end = f"{year}-{month_str}-{calendar.monthrange(year, month)[1]}"
    else:
        start = f"{year}-01-01"
        end = f"{year}-12-31"
    return pd.to_datetime(start).date(), pd.to_datetime(end).date()

def load_downloaded_files(csv_path):
    """
    Charge les fichiers déjà téléchargés depuis un fichier CSV contenant des chemins complets.
    Retourne un ensemble de tuples (date, tuile).
    """
    downloaded = set()
    try:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            # Extraire le chemin complet
            full_path = row[0]  # Supposons que le chemin est dans la première colonne
            safe_name = os.path.basename(full_path)  # Extraire uniquement le nom du fichier
            date, tile = extract_date_tile_from_safe_name(safe_name)
            if date and tile:
                downloaded.add((date, tile))
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV {csv_path} : {e}")
    return downloaded

def is_already_downloaded(safe_name, downloaded_files):
    """
    Vérifie si un fichier SAFE a déjà été téléchargé en comparant la date et la tuile.
    """
    date, tile = extract_date_tile_from_safe_name(safe_name)
    return (date, tile) in downloaded_files

def list_safe_products(zone, band, square, start_date, end_date, downloaded_files):
    """
    Recherche des produits Sentinel-2 dans un répertoire MGRS donné,
    en vérifiant les dates dans les noms de fichiers et en excluant les fichiers déjà téléchargés.
    """
    products = []
    base_path = f"gcp-public-data-sentinel-2/tiles/{zone}/{band}/{square}/"

    try:
        # Lister tous les fichiers dans le répertoire de la tuile
        files = fs.ls(base_path)
        for f in files:
            if f.endswith(".SAFE"):
                # Extraire la date et la tuile du nom du fichier
                safe_name = f.split("/")[-1]
                date_str, _ = extract_date_tile_from_safe_name(safe_name)
                if date_str and start_date <= date_str <= end_date:
                    if not is_already_downloaded(safe_name, downloaded_files):
                        products.append(f)
                    else:
                        print(f"[SKIP] Déjà téléchargé : {safe_name}")
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

if __name__ == "__main__":
    print('Lancement...')
    args = parse_arguments()

    # Initialiser le système de fichiers GCS
    fs = gcsfs.GCSFileSystem(token=args.cred)

    # Charger les fichiers déjà téléchargés
    downloaded_files = load_downloaded_files(args.downloaded_csv)

    # Configurer le chemin de sortie
    localp = setup_download_path(args.output)
    print(f"Répertoire de sortie : {localp}")

    # Obtenir la plage de dates
    start_date, end_date = get_date_range(args.year, args.month)
    print(f"Plage de dates : {start_date} à {end_date}")

    # Initialiser les téléchargements
    for tile in args.tile:
        print(f"Traitement de la tuile {tile}")
        zone, band, square = tile[:2], tile[2], tile[3:]

        # Rechercher les produits dans GCS
        products = list_safe_products(zone, band, square, start_date, end_date, downloaded_files)

        if not products:
            print(f"Aucun produit trouvé pour la tuile {tile} entre {start_date} et {end_date}")
            continue

        # Télécharger les produits
        for product_path in products:
            download_safe_product(product_path, localp)

    # Sauvegarder le log des téléchargements
    log_file = os.path.join(localp, "download_log.csv")
    with open(log_file, "w", newline="") as csvfile:
        fieldnames = ["date", "tile", "safe_name", "local_path"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in download_log:
            writer.writerow(entry)

    print("\nTéléchargements terminés.")
    print(f"Log écrit dans : {log_file}")