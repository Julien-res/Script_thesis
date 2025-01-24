"""
Based on Ngoc et al. (2019)
Code by : Julien Masson - LOG UMR CNRS 8187 (23/01/2025)
Require a working SNAP installation (SNAP 11.01 or higher)
"""
import sys
"""
Based on Ngoc et al. (2019)
Code by: Julien Masson - LOG UMR CNRS 8187 (23/01/2025)
Requires a working SNAP installation (SNAP 11.01 or higher)
"""
import sys
import argparse
import os
path = os.curdir
sys.path.insert(1, os.path.expanduser('~'))  # To load esa_snappy, its source file must be loaded
from rayleigh_correction import apply_rayleigh_correction
from applyWiPE import applyWiPE
os.chdir(os.path.expanduser('~'))
import rasterio
import numpy as np
from rasterio.merge import merge
from rasterio.plot import reshape_as_raster, reshape_as_image
from rasterio.transform import from_origin
from glob import glob
import time

# TEST="/mnt/c/Travail/Script/S2A_MSIL1C_20231216T032131_N0510_R118_T48PXQ_20231216T050649.SAFE"
# TEST2="/mnt/c/Travail/Script/S2A_MSIL1C_20241128T110411_N0511_R094_T31UDS_20241128T130346.SAFE"

def load_band(filepath, resolution):
    """Load a specific Sentinel-2 band based on resolution to output the correct profile"""
    resolution_to_band = {
        10: "B03",  # Band 3
        20: "B11",  # Band 11
        60: "B10",  # Band 10
    }
    if resolution not in resolution_to_band:
        raise ValueError(f"Invalid resolution: {resolution}. Accepted values: 10, 20, 60.")
    band_code = resolution_to_band[resolution]
    band_filepath = glob(os.path.join(filepath, f'GRANULE/**/IMG_DATA/*{band_code}.jp2'))
    if not band_filepath:
        raise FileNotFoundError(f"No file found for band {band_code} at resolution {resolution}.")
    band_filepath = band_filepath[0]
    with rasterio.open(band_filepath) as src:
        band = src.read(1)
        profile = src.profile

    return profile

def save_composite(output_path, composite, profile, output_name):
    """Save the mask while preserving georeferencing."""
    profile.update(dtype='uint16', count=1)
    with rasterio.open(os.path.join(output_path, output_name + '.jp2'), 'w', **profile) as dst:
        dst.write(composite.astype('uint16'), 1)

# Function to execute in parallel

# def process_in_parallel(func, input_path, resolution, bands, resolution_method="Sampling", max_workers=2):
#     """
#     Execute a function on multiple bands in parallel.

#     :param func: Function to execute.
#     :param bands: List of bands to process.
#     :param input_path: Path to the folder containing data.
#     :param resolution: Desired resolution.
#     :param max_workers: Maximum number of parallel processes.
#     :return: List of results.
#     """
#     results = []
#     with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
#         # Prepare arguments for each band
#         futures = {
#             executor.submit(func, input_path, resolution, band, resolution_method): band for band in bands
#         }
#         for future in concurrent.futures.as_completed(futures):
#             try:
#                 results.append(future.result())
#             except Exception as e:
#                 print(f"Error during processing: {e}")
#     return results

# Entry point of the script
if __name__ == "__main__":
    start_time = time.time()
    parser = argparse.ArgumentParser(description="Apply Rayleigh correction to a Sentinel-2 image")
    parser.add_argument(
        "-o", "--output",
        dest="output",
        type=str,
        help="Path to the corrected output file (default: stdout)",
        default="stdout"
    )
    parser.add_argument(
        "-r", "--resolution",
        dest="resolution",
        type=int,
        help="Desired output resolution (default: 20)",
        default=20
    )
    parser.add_argument(
        "-m", "--method",
        dest="method",
        type=str,
        help="Method for Rayleigh correction calculation (Sampling, Other)",
        default="Sampling"
    )
    requiredNamed = parser.add_argument_group('Required Arguments')
    requiredNamed.add_argument(
        "-i", "--input",
        dest="input",
        type=str,
        help="Path to the Sentinel-2 file (SAFE)",
        required=True
    )
    requiredNamed.add_argument(
        "-n", "--name",
        dest="name",
        type=str,
        help="Name of the output image",
        required=True
    )

    args = parser.parse_args()

    if args.output == 'stdout':
        os.mkdir('WiPE_Workspace')
        Output = os.path.join(os.curdir, 'WiPE_Workspace')
    else:
        Output = args.output
    bands = ["B2", "B3", "B4", "B7", "B10", "B11", "B12"]  # Filter the files
    if args.resolution == 10:
        corrected_bands = np.zeros((7, 10980, 10980))
    elif args.resolution == 20:
        corrected_bands = np.zeros((7, 5490, 5490))
    else:
        corrected_bands = np.zeros((7, 1830, 1830))
    # corrected_bands = process_in_parallel(func=apply_rayleigh_correction, input_path=args.input,
    #                                       resolution=args.resolution, bands=bands, resolution_method="Sampling",
    #                                       max_workers=2)
    for band in bands:
        corrected_bands[bands.index(band)] = apply_rayleigh_correction(
            input_path=args.input,
            target_res=args.resolution,
            band=band,
            resolution_method=args.method
        )
    Mask = applyWiPE(corrected_bands)
    profile = load_band(filepath=args.input, resolution=args.resolution)
    save_composite(output_path=Output, composite=Mask, profile=profile, output_name=args.name)
    print(f"Water mask image saved at {os.path.join(Output, args.name) + '.jp2'}")
    print(f"--- {time.time() - start_time} seconds ---")
    print(f"--- or {(time.time() - start_time)/60} minutes ---")
    print('Clearing __pycache__')
    files = glob(os.path.join(path, '__pycache__/*'))
    for f in files:
        os.remove(f)

# import os
# # os.chdir ('/mnt/c/Travail/Script/Script_Thesis/2_WiPE/WiPE_personal/Python_Dev/') # inutile 
# path=os.curdir
# sys.path.insert(1, os.path.expanduser('~')) # Afin de pouvoir charger esa_snappy, il faut charger son fichier source
# from rayleigh_correction import apply_rayleigh_correction
# from applyWiPE import applyWiPE
# # from launch_acolite import launch_acolite
# os.chdir(os.path.expanduser('~'))
# import rasterio
# import numpy as np
# from rasterio.merge import merge
# from rasterio.plot import reshape_as_raster, reshape_as_image
# from rasterio.transform import from_origin
# from glob import glob
# # os.chdir('/mnt/c/Travail/Script/acolite')
# # import acolite as ac
# # from netCDF4 import Dataset
# import time

# # TEST="/mnt/c/Travail/Script/S2A_MSIL1C_20231216T032131_N0510_R118_T48PXQ_20231216T050649.SAFE"
# # TEST2="/mnt/c/Travail/Script/S2A_MSIL1C_20241128T110411_N0511_R094_T31UDS_20241128T130346.SAFE"
# def load_band(filepath, resolution):
#     """Charge une bande Sentinel-2 spécifique en fonction de la résolution afin de pouvoir output le bon profile"""
#     resolution_to_band = {
#         10: "B03",  # Bande 3
#         20: "B11",  # Bande 11
#         60: "B10",  # Bande 10
#     }
#     if resolution not in resolution_to_band:
#         raise ValueError(f"Résolution invalide : {resolution}. Valeurs acceptées : 10, 20, 60.")
#     band_code = resolution_to_band[resolution]
#     band_filepath = glob(os.path.join(filepath, f'GRANULE/**/IMG_DATA/*{band_code}.jp2'))
#     if not band_filepath:
#         raise FileNotFoundError(f"Aucun fichier trouvé pour la bande {band_code} à la résolution {resolution}.")
#     band_filepath = band_filepath[0]
#     with rasterio.open(band_filepath) as src:
#         band = src.read(1)
#         profile = src.profile

#     return profile

# def save_composite(output_path, composite, profile, output_name):
#     """Enregistre le mask tout en conservant le géoréférencement."""
#     profile.update(dtype='uint16',count=1)
#     with rasterio.open(os.path.join(output_path,output_name+'.jp2',), 'w', **profile) as dst:
#         dst.write(composite.astype('uint16'), 1)

# # Fonction pour exécuter en parallèle

# # def process_in_parallel(func, input_path, resolution, bands, resolution_method="Sampling", max_workers=2):
# #     """
# #     Exécute une fonction sur plusieurs bandes en parallèle.

# #     :param func: Fonction à exécuter.
# #     :param bands: Liste des bandes à traiter.
# #     :param input_path: Chemin vers le dossier contenant les données.
# #     :param resolution: Résolution souhaitée.
# #     :param max_workers: Nombre maximal de processus parallèles.
# #     :return: Liste des résultats.
# #     """
# #     results = []
# #     with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
# #         # Prépare les arguments pour chaque bande
# #         futures = {
# #             executor.submit(func, input_path, resolution, band,resolution_method): band for band in bands
# #         }
# #         for future in concurrent.futures.as_completed(futures):
# #             try:
# #                 results.append(future.result())
# #             except Exception as e:
# #                 print(f"Erreur lors du traitement : {e}")
# #     return results

# # Point d'entrée du script
# if __name__ == "__main__":
#     start_time=time.time()
#     parser = argparse.ArgumentParser(description="Appliquer une correction de Rayleigh à une image Sentinel-2")
#     parser.add_argument(
#         "-o", "--output", 
#         dest="output", 
#         type=str,
#         help="Chemin vers le fichier de sortie corrigé (par défaut: stdout)", 
#         default="stdout"
#     )
#     parser.add_argument(
#         "-r", "--resolution", 
#         dest="resolution", 
#         type=int, 
#         help="Résolution de sortie souhaitée (par défaut: 20)", 
#         default=20
#     )
#     parser.add_argument(
#         "-m", "--method", 
#         dest="method", 
#         type=str, 
#         help="Methode de calcul de la correction de Rayleigh (Sampling, Other)", 
#         default="Sampling"
#     )
#     requiredNamed = parser.add_argument_group('Arguments requis')
#     requiredNamed.add_argument(
#         "-i", "--input", 
#         dest="input", 
#         type=str,
#         help="Chemin vers le fichier Sentinel-2 (SAFE)", 
#         required=True
#     )
#     requiredNamed.add_argument(
#         "-n", "--name", 
#         dest="name", 
#         type=str,
#         help="Nom de de l'image de sortie", 
#         required=True
#     )

#     args = parser.parse_args()

#     if args.output=='stdout':
#         os.mkdir('WiPE_Workspace')
#         Output=os.curdir+'/WiPE_Workspace'
#     else:
#         Output=args.output
#     bands = ["B2","B3","B4","B7","B10","B11","B12"]  # Filtre les fichiers
#     if args.resolution==10:
#         corrected_bands=np.zeros((7,10980,10980))
#     elif args.resolution==20:
#         corrected_bands=np.zeros((7,5490,5490))
#     else:
#         corrected_bands=np.zeros((7,1830,1830))
#     # corrected_bands = process_in_parallel(func=apply_rayleigh_correction, input_path=args.input,
#     #                                         resolution=args.resolution, bands=bands,resolution_method="Sampling",  
#     #                                         max_workers=2)
#     for band in bands:
#         corrected_bands[bands.index(band)]=apply_rayleigh_correction(input_path=args.input,target_res=args.resolution,band=band,resolution_method=args.method)
#     Mask=applyWiPE(corrected_bands)
#     profile=load_band(filepath=args.input, resolution=args.resolution)
#     save_composite(output_path=Output, composite=Mask, profile=profile,output_name=args.name)
#     print(f"Image masque d'eau enregistrée à {os.path.join(Output,args.name)+'.jp2'}")
#     print("--- %s seconds ---" % (time.time() - start_time))
#     print("--- or %s minutes ---" % ((time.time() - start_time)/60))
#     print('Clear __pycache__')
#     files = glob(os.path.join(path,'__pycache__/*'))
#     for f in files:
#         os.remove(f)
