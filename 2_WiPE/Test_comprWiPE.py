import sys
import argparse
import os
os.chdir('/mnt/c/Travail/Script/Script_Thesis/2_WiPE/WiPE_personal/Python_Dev/') # inutile 
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
# %%
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

def save_compositeJP2(output_path, composite, profile, output_name):
    """Save the mask while preserving georeferencing."""
    profile.update(dtype='uint16', count=1)
    with rasterio.open(os.path.join(output_path, output_name + '.jp2'), 'w', **profile) as dst:
        dst.write(composite.astype('uint16'), 1)
def save_compositeTIFF(output_path, composite, profile, output_name):
    """Save the mask while preserving georeferencing."""
    profile.update(dtype='uint16', count=1, driver='GTiff')
    with rasterio.open(os.path.join(output_path, output_name + '.tif'), 'w', **profile) as dst:
        dst.write(composite.astype('uint16'), 1)
def save_compositeTIFFCPR(output_path, composite, profile, output_name):
    """Save the mask while preserving georeferencing."""
    profile.update(
        dtype='uint16',
        count=1,
        driver='GTiff',
        compress='lzw',  # Use LZW compression
        tiled=True,  # Enable tiling
        blockxsize=256,  # Set tile width
        blockysize=256  # Set tile height
    )
    with rasterio.open(os.path.join(output_path, output_name + '.tif'), 'w', **profile) as dst:
        dst.write(composite.astype('uint16'), 1)

bands = ["B2", "B3", "B4", "B7", "B10", "B11", "B12"]
corrected_bands=np.zeros((7,10980,10980))
# %%
for band in bands:
    corrected_bands[bands.index(band)]=apply_rayleigh_correction(input_path="/mnt/c/Travail/Script/S2A_MSIL1C_20231216T032131_N0510_R118_T48PXQ_20231216T050649.SAFE",target_res=10,band=band,resolution_method="other")
    Mask = applyWiPE(corrected_bands)
    np.unique(Mask)
    # %%
profile=load_band(filepath="/mnt/c/Travail/Script/S2A_MSIL1C_20231216T032131_N0510_R118_T48PXQ_20231216T050649.SAFE",resolution=10)
save_compositeJP2(output_path="/mnt/c/Travail/TEST", composite=Mask, profile=profile, output_name="TESTJP2")
profile=load_band(filepath="/mnt/c/Travail/Script/S2A_MSIL1C_20231216T032131_N0510_R118_T48PXQ_20231216T050649.SAFE",resolution=10)
save_compositeTIFF(output_path="/mnt/c/Travail/TEST", composite=Mask, profile=profile, output_name="TEST")
profile=load_band(filepath="/mnt/c/Travail/Script/S2A_MSIL1C_20231216T032131_N0510_R118_T48PXQ_20231216T050649.SAFE",resolution=10)
save_compositeTIFFCPR(output_path="/mnt/c/Travail/TEST", composite=Mask, profile=profile, output_name="TEST_no_compress")