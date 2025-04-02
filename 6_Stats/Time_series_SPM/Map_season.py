import os
import re
import numpy as np
import rasterio

# Définir les saisons
def get_season(date):
    month = int(date[4:6])  # Extraire le mois de la date (YYYYMMDD)
    if 5 <= month <= 10:  # Saison humide (mai à octobre)
        return "humide"
    else:  # Saison sèche (novembre à avril)
        return "seche"

# Dossier contenant les fichiers .tiff
input_folder = "/mnt/d/DATA/SPM_Polymer_Han/"
output_folder = "/mnt/d/DATA/SPM_Polymer_Han/mean_season/"
os.makedirs(output_folder, exist_ok=True)

# Regrouper les fichiers par cellule et saison
data = {}
cell_name = r"\d{2}[A-Z]{3}"  # Exemple : 48PUV
pattern = re.compile(rf"({cell_name}).*?(\d{{8}}).*\.tif$")  # Exemple : 48PUV_YYYYMMDD.tif

for file in os.listdir(input_folder):
    if file.endswith(".tif"):
        match = pattern.search(file)
        if match:
            cell = match.group(1)
            date = match.group(2)
            season = get_season(date)
            key = (cell, season)
            if key not in data:
                data[key] = []
            data[key].append(os.path.join(input_folder, file))

# Calculer les moyennes saisonnières et sauvegarder les résultats
for (cell, season), files in data.items():
    print(f"Traitement de la cellule {cell}, saison {season}...")
    sum_array = None
    count_array = None
    meta = None

    for file in files:
        with rasterio.open(file) as src:
            array = src.read(1)  # Lire la première bande
            mask = (array > 0) & np.isfinite(array)  # Masque : pixels non nuls, non NaN, non négatifs
            if sum_array is None:
                sum_array = np.zeros_like(array, dtype=np.float64)  # Initialiser la somme
                count_array = np.zeros_like(array, dtype=np.float64)  # Initialiser le compteur
            sum_array[mask] += array[mask]  # Ajouter les valeurs valides à la somme
            count_array[mask] += 1  # Incrémenter le compteur pour les pixels valides
            if meta is None:
                meta = src.meta

    # Calculer la moyenne
    total_images = len(files)  # Nombre total d'images pour la cellule et la saison en cours
    threshold = 0.05 * total_images  # Seuil de 85% des images pour cette cellule et cette saison
    mean_array = np.divide(sum_array, count_array, out=np.zeros_like(sum_array), where=(count_array > 0))

    # Remplacer les pixels avec un nombre d'images inférieur à 85% par NaN
    mean_array[count_array < threshold] = np.nan

    # Mettre à jour les métadonnées pour le fichier de sortie
    meta.update(dtype=rasterio.float32, count=1, compress='LZW')  # Ajout de la compression LZW

    # Sauvegarder l'image moyenne
    output_file = os.path.join(output_folder, f"{cell}_{season}_mean.tif")
    with rasterio.open(output_file, "w", **meta) as dst:
        dst.write(mean_array.astype(rasterio.float32), 1)

    print(f"Image moyenne sauvegardée : {output_file}")