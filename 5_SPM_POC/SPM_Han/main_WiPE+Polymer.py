import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from netCDF4 import Dataset
import os
import re
from tqdm import tqdm
# Convertir le masque d'eau en booléen


# Charger les données .nc de POLYMER
def load_polymer_data(nc_file, variable_name="Rw665"):
    with Dataset(nc_file, mode='r') as nc:
        data = nc.variables[variable_name][:]
    return data

# Charger le masque d'eau
def load_water_mask(mask_file):
    with rasterio.open(mask_file) as src:
        mask = src.read(1)
        transform = src.transform
    return mask, transform

def calculate_spm(rrs_665):
    """
    Calcule la concentration de SPM à partir des données de réflectance Rrs(665) de Sentinel-2 MSI
    selon l'algorithme semi-analytique du papier.
    
    :param rrs_665: numpy array, réflectance Rrs(665) en sr^-1
    :return: numpy array, concentration de SPM en g/m^3
    """
    pi = np.pi
    rho_w_665 = pi * rrs_665  # Calcul de la réflectance de l'eau
    
    # Initialisation du tableau de sortie
    spm = np.zeros_like(rrs_665)
    
    # Cas 1 : Faible à moyenne turbidité (SAA-L)
    low_turbidity = rrs_665 <= 0.03
    A_rho_L, C_rho_L = 396.005, 0.5
    spm[low_turbidity] = (A_rho_L * rho_w_665[low_turbidity]) / (1 - rho_w_665[low_turbidity] / C_rho_L)
    
    # Cas 2 : Eau très turbide (SAA-HR)
    high_turbidity = rrs_665 >= 0.04
    A_rho_H, C_rho_H = 1208.481, 0.3375
    rho_w_665_clipped = np.clip(rho_w_665[high_turbidity], None, C_rho_H * 0.99)  # Clip to avoid overflow
    spm[high_turbidity] = (A_rho_H * rho_w_665_clipped) / (1 - rho_w_665_clipped / C_rho_H)
    
    # Cas 3 : Transition entre faible et forte turbidité (pondération)
    transition_zone = (rrs_665 > 0.03) & (rrs_665 < 0.04)
    if np.any(transition_zone):
        if rrs_665[transition_zone] < 0.03:
            w_L = 1
            w_H = 0
        elif rrs_665[transition_zone] > 0.04:
            w_L = 0
            w_H = 1
        else:
            w_L = np.log10(0.04) - np.log10(rrs_665[transition_zone])
            w_H = np.log10(rrs_665[transition_zone]) - np.log10(0.03)
        spm_L = (A_rho_L * rho_w_665[transition_zone]) / (1 - rho_w_665[transition_zone] / C_rho_L)
        spm_H = (A_rho_H * rho_w_665[transition_zone]) / (1 - rho_w_665[transition_zone] / C_rho_H)
        spm[transition_zone] = (w_L * spm_L + w_H * spm_H) / (w_L + w_H)
    
    spm[spm < 0] = -999
    return spm

# Appliquer le masque et la fonction personnalisée de manière vectorisée
def process_data(data, mask, func):
    masked_data = np.where(mask == 1, data, np.nan)  # Appliquer le masque
    valid_pixels = ~np.isnan(masked_data)  # Identifier les pixels valides
    processed_data = np.full_like(masked_data, np.nan)  # Initialiser le tableau de sortie avec NaN
    
    # Appliquer la fonction de manière vectorisée uniquement sur les pixels valides
    processed_data[valid_pixels] = func(masked_data[valid_pixels])
    
    return processed_data
    # Sauvegarder les données en un fichier NetCDF
    def save_to_netcdf(output_file, data, dates, transform, crs="EPSG:4326"):
        """
        Sauvegarde les données dans un fichier NetCDF avec une dimension temporelle.

        :param output_file: str, chemin du fichier NetCDF de sortie
        :param data: numpy array, données à sauvegarder (3D: temps, hauteur, largeur)
        :param dates: list, liste des dates correspondant à chaque couche temporelle
        :param transform: Affine, transformation géoréférencée
        :param crs: str, système de coordonnées (par défaut EPSG:4326)
        """
        with Dataset(output_file, "w", format="NETCDF4") as nc:
            # Dimensions
            nc.createDimension("time", len(dates))
            nc.createDimension("y", data.shape[1])
            nc.createDimension("x", data.shape[2])

            # Variables
            times = nc.createVariable("time", "i4", ("time",))
            latitudes = nc.createVariable("latitude", "f4", ("y", "x"))
            longitudes = nc.createVariable("longitude", "f4", ("y", "x"))
            spm = nc.createVariable("spm", "f4", ("time", "y", "x"), zlib=True, complevel=4)

            # Attributs globaux
            nc.title = "Concentration de SPM dérivée des données POLYMER"
            nc.crs = crs
            nc.transform = str(transform)

            # Remplir les variables
            times[:] = [int(date) for date in dates]
            x_coords, y_coords = np.meshgrid(
                np.arange(data.shape[2]), np.arange(data.shape[1])
            )
            longitudes[:, :] = transform * (x_coords, y_coords)[0]
            latitudes[:, :] = transform * (x_coords, y_coords)[1]
            spm[:, :, :] = data

    # Exemple d'utilisation
    if __name__ == "__main__":
        polymer_dir = "/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_Polymer_20m"
        mask_dir = "/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_WiPE/RAW"
        output_file = "/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/SPM/SPM_Polymer_Han/processed_spm.nc"

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        polymer_files = []
        for root, _, files in os.walk(polymer_dir):
            for polymer_file in files:
                if polymer_file.endswith(".nc"):
                    polymer_files.append(os.path.join(root, polymer_file))

        all_processed_data = []
        all_dates = []

        for polymer_path in tqdm(polymer_files, desc="Traitement des fichiers POLYMER"):
            polymer_file = os.path.basename(polymer_path)

            match = re.search(r"(\d{2}[A-Z]{3}).*(\d{8})", polymer_file)
            if not match:
                continue

            tile_id, date = match.groups()

            mask_file = None
            for mask_root, _, mask_files in os.walk(mask_dir):
                for file in mask_files:
                    if tile_id in file and date in file and file.lower().endswith("_water.tif"):
                        mask_file = os.path.join(mask_root, file)
                        break
                if mask_file:
                    break

            if not mask_file:
                continue

            polymer_data = load_polymer_data(polymer_path)
            water_mask, mask_transform = load_water_mask(mask_file)
            water_mask = water_mask.astype(bool)

            target_transform = from_origin(mask_transform.c, mask_transform.f, 20, 20)
            target_shape = (polymer_data.shape[0], polymer_data.shape[1])

            water_mask_resampled = resample_mask_to_target_resolution(
                water_mask, mask_transform, target_transform, target_shape
            )

            processed_data = process_data(polymer_data, water_mask_resampled, calculate_spm)

            all_processed_data.append(processed_data)
            all_dates.append(date)

        all_processed_data = np.stack(all_processed_data)
        save_to_netcdf(output_file, all_processed_data, all_dates, target_transform)
        print(f"Résultat sauvegardé dans {output_file}")
