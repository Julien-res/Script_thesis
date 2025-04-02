import os
import re
from osgeo import gdal
import xarray as xr
import numpy as np
from datetime import datetime
from tqdm import tqdm

# Répertoires
input_dir = "/mnt/d/DATA/SPM_Polymer_Han/"
output_dir = "/mnt/d/DATA/SPM_Polymer_Han/NetCDF/"

# Expression régulière pour extraire le nom de cellule et la date
pattern = re.compile(r"processed_(?P<cell>\d{2}[A-Za-z]{3})_(?P<date>\d{8})\.tif")

# Dictionnaire pour regrouper les fichiers par nom de cellule
cell_files = {}

# Parcourir les fichiers dans le répertoire
for filename in os.listdir(input_dir):
    match = pattern.match(filename)
    if match:
        cell = match.group("cell")
        date = match.group("date")
        if cell not in cell_files:
            cell_files[cell] = []
        cell_files[cell].append((filename, date))

# Fonction pour convertir une liste de fichiers .tif en un fichier NetCDF
def convert_to_netcdf(cell, files):
    datasets = []
    times = []
    
    # Ajouter une barre de progression pour les fichiers
    for filename, date in tqdm(files, desc=f"Traitement de la cellule {cell}", unit="fichier"):
        filepath = os.path.join(input_dir, filename)
        src_ds = gdal.Open(filepath)
        
        data = src_ds.GetRasterBand(1).ReadAsArray()
        x_size = src_ds.RasterXSize
        y_size = src_ds.RasterYSize
        x_coords = np.arange(x_size)
        y_coords = np.arange(y_size)
        
        times.append(datetime.strptime(date, "%Y%m%d"))
        datasets.append(xr.DataArray(
            data,
            dims=("y", "x"),
            coords={
                "y": y_coords,
                "x": x_coords,
            },
            name="data"
        ))
    
    # Empiler les données le long de la dimension temporelle
    combined = xr.concat(datasets, dim="time")
    combined["time"] = times
    
    # Sauvegarder en NetCDF
    output_path = os.path.join(output_dir, f"{cell}.nc")
    combined.to_netcdf(output_path)
    print(f"Fichier NetCDF créé : {output_path}")

# Créer le répertoire de sortie s'il n'existe pas
os.makedirs(output_dir, exist_ok=True)

# Convertir les fichiers pour chaque cellule
for cell, files in cell_files.items():
    convert_to_netcdf(cell, files)
