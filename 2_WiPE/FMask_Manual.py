import os
from fmask import landsatmask
from osgeo import gdal

# Chemin vers les bandes Sentinel-2
bands_dir = "/chemin/vers/les/bandes/"
output_dir = "/chemin/vers/le/résultat/"

# Identifier les bandes nécessaires (Sentinel-2 utilise les bandes B02, B03, B04 pour Fmask)
bands = {
    "blue": os.path.join(bands_dir, "B02.jp2"),
    "green": os.path.join(bands_dir, "B03.jp2"),
    "red": os.path.join(bands_dir, "B04.jp2"),
    "nir": os.path.join(bands_dir, "B08.jp2"),
    "cirrus": os.path.join(bands_dir, "B10.jp2"),
}

# Vérification des fichiers nécessaires
for band, path in bands.items():
    if not os.path.exists(path):
        raise FileNotFoundError(f"Band {band} not found at {path}")

# Appliquer Fmask
output_mask_path = os.path.join(output_dir, "fmask_output.tif")
landsatmask.main(
    [
        "--blue", bands["blue"],
        "--green", bands["green"],
        "--red", bands["red"],
        "--nir", bands["nir"],
        "--cirrus", bands["cirrus"],
        "--output", output_mask_path,
    ]
)

# Charger et afficher la couche eau depuis le masque
ds = gdal.Open(output_mask_path)
fmask_array = ds.GetRasterBand(1).ReadAsArray()

# Les valeurs 1 dans le masque correspondent à l'eau
water_mask = (fmask_array == 1)

print("Masque d'eau généré avec succès.")


import os
from fmask.cmdline import sentinel2Stacked


safe_dir = '/mnt/c/Travail/HDF_water_detect'
OUT='/mnt/c/Travail/HDF_water_detect/Output'
LIST=['S2A_MSIL1C_20240919T105731_N0511_R094_T31UCR_20240919T144023.SAFE','S2A_MSIL1C_20240919T105731_N0511_R094_T31UDR_20240919T144023.SAFE','S2A_MSIL1C_20240919T105731_N0511_R094_T31UDS_20240919T144023.SAFE','S2B_MSIL1C_20241024T110039_N0511_R094_T31UCS_20241024T125901.SAFE']

out_img_file = 'img'
for i in LIST:
    sentinel2Stacked.mainRoutine(['--safedir', safe_dir+'/'+i, '-o', OUT+'/'+i+out_img_file])

print('Completed running Fmask on SAFE file')