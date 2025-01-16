import sys
import argparse
import os
os.chdir('/mnt/c/Travail/Script/Script_Thesis/2_WiPE/WiPE_personal/Python_Dev/') # inutile 
sys.path.insert(1, '/home/julien/') # Afin de pouvoir charger esa_snappy, il faut charger son fichier source
from rayleigh_correction import apply_rayleigh_correction
from applyWiPE import applyWiPE
# from launch_acolite import launch_acolite
os.chdir('/home/julien/')
import rasterio
import numpy as np
from rasterio.merge import merge
from rasterio.plot import reshape_as_raster, reshape_as_image
from rasterio.transform import from_origin
from glob import glob
# os.chdir('/mnt/c/Travail/Script/acolite')
# import acolite as ac
# from netCDF4 import Dataset
import concurrent.futures
import time


parser = argparse.ArgumentParser(description="Appliquer une correction de Rayleigh à une image Sentinel-2")
parser.add_argument(
    "-o", "--output", 
    dest="output", 
    help="Chemin vers le fichier de sortie corrigé (par défaut: stdout)", 
    default="stdout"
)
parser.add_argument(
    "-r", "--resolution", 
    dest="resolution", 
    type=int, 
    help="Résolution de sortie souhaitée (par défaut: 20)", 
    default=20
)
requiredNamed = parser.add_argument_group('Arguments requis')
requiredNamed.add_argument(
    "-i", "--input", 
    dest="input", 
    help="Chemin vers le fichier Sentinel-2 (SAFE)", 
    required=True
)
args = parser.parse_args()

TEST="/mnt/c/Travail/Script/S2A_MSIL1C_20231216T032131_N0510_R118_T48PXQ_20231216T050649.SAFE"

def load_bands(filepaths):
    """Charge les bandes Sentinel-2 depuis les fichiers spécifiés."""
    band_filepaths = [
    glob(os.path.join(filepaths,'GRANULE/**/IMG_DATA/*B01.jp2'))[0] ,  # Bande 2
    glob(os.path.join(filepaths,'GRANULE/**/IMG_DATA/*B03.jp2'))[0],  # Bande 3
    glob(os.path.join(filepaths,'GRANULE/**/IMG_DATA/*B04.jp2'))[0],  # Bande 4
    glob(os.path.join(filepaths,'GRANULE/**/IMG_DATA/*B07.jp2'))[0],  # Bande 7
    glob(os.path.join(filepaths,'GRANULE/**/IMG_DATA/*B10.jp2'))[0], # Bande 10
    glob(os.path.join(filepaths,'GRANULE/**/IMG_DATA/*B11.jp2'))[0], # Bande 11
    glob(os.path.join(filepaths,'GRANULE/**/IMG_DATA/*B12.jp2'))[0]  # Bande 12
    ]
    bands = []
    profile = None
    iter=0
    for filepath in band_filepaths:
        with rasterio.open(filepath) as src:
            if iter==0:
                iter=1
                if profile is None:
                    profile = src.profile
            bands.append(src.read(1))

    return np.array(bands), profile

def save_composite(output_path, composite, profile):
    """Enregistre le mask tout en conservant le géoréférencement."""
    profile.update(
        dtype='uint16',
        count=1
    )

    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(composite.astype('uint16'), 1)

# Fonction pour exécuter en parallèle

def process_in_parallel(func, input_path, resolution, bands, max_workers=7):
    """
    Exécute une fonction sur plusieurs bandes en parallèle.

    :param func: Fonction à exécuter.
    :param bands: Liste des bandes à traiter.
    :param input_path: Chemin vers le dossier contenant les données.
    :param resolution: Résolution souhaitée.
    :param max_workers: Nombre maximal de processus parallèles.
    :return: Liste des résultats.
    """
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Prépare les arguments pour chaque bande
        futures = {
            executor.submit(func, input_path, resolution, band): band for band in bands
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Erreur lors du traitement : {e}")
    return results

# Point d'entrée du script
if __name__ == "__main__":
    start_time=time.time()
    if args.output=='stdout':
        os.mkdir('WiPE_Workspace')
        Output=os.curdir+'/WiPE_Workspace'
    else:
        Output=args.output

    bands = ["B2","B3","B4","B7","B10","B11","B12"]  # Filtre les fichiers
    corrected_bands = process_in_parallel(func=apply_rayleigh_correction, input_path=args.input,
                                            resolution=args.resolution, bands=bands,  
                                            max_workers=24)
        
    print("--- %s seconds ---" % (time.time() - start_time))
    # settings = {"inputfile":args.input,
    # "output":args.output,
    # "s2_target_res":args.resolution,
    # "atmospheric_correction":True,
    # "l2w_parameters":["rhorc_492","rhorc_560","rhorc_665","rhorc_783","rhorc_945","rhorc_1373","rhorc_1614"],
    # "rgb_rhot":False,
    # "rgb_rhos":False,
    # "l2w_mask":False,
    # "reproject_outputs":"L2W",
    # "l1r_delete_netcdf":True,
    # "l2t_delete_netcdf":True
    # }
    # ac.acolite.acolite_run(settings, inputfile=inputfile_list, output=output)
    # dataset = Dataset(output, mode="r")
    # launch_acolite(inputfile=agrs.input,output=arsg.output,settings=settings_path)
    # # Charger les bandes
    # bands, profile = load_bands(band_filepaths)

    # LIEN A FAIRE ENTRE CORRECTED BANDS(DICTIONNAIRE) ET BANDS (LIST)
    # mask_image = applyWiPE(bands)

    # # Enregistrer l'image composite
    # save_composite(Output, mask_image, profile)
    # print(f"Image composite enregistrée à {Output}")

