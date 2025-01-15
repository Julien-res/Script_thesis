import sys
import argparse

from rayleigh_correction import apply_rayleigh_correction
from applyWiPE import applyWiPE
os.chdir('/home/julien/')
import rasterio
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.plot import reshape_as_raster, reshape_as_image
from rasterio.transform import from_origin
from glob import glob

parser = argparse.ArgumentParser(description="Appliquer une correction de Rayleigh à une image Sentinel-2")
parser.add_argument("output", help="Chemin vers le fichier de sortie corrigé", default="stdout")
requiredNamed = parser.add_argument_group('Arguments requis')
requiredNamed.add_argument("input", help="Chemin vers le fichier Sentinel-2 (SAFE)", required=True)
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

# Point d'entrée du script
if __name__ == "__main__":
    if args.output=='stdout'
        os.mkdir('WiPE_Workspace')
        Output=os.curdir+'/WiPE_Workspace'
    else:
        Output=args.output

    corrected_bands=apply_rayleigh_correction(args.input,10)
    # # Charger les bandes
    # bands, profile = load_bands(band_filepaths)
    LIEN A FAIRE ENTRE CORRECTED BANDS(DICTIONNAIRE) ET BANDS (LIST)
    mask_image = applyWiPE(bands)

    # Enregistrer l'image composite
    save_composite(Output, mask_image, profile)
    print(f"Image composite enregistrée à {Output}")

