"""
Based on Ngoc et al. (2019)
https://www.sciencedirect.com/science/article/pii/S0034425719300276
Code by : Julien Masson - LOG UMR CNRS 8187 (01/2025)
Require a working SNAP installation (SNAP 11.01 or higher) to compute Rayleigh correction
"""
import sys
import argparse
import os
path = os.curdir
# Default path to SNAPPY is ~/esa_snappy but modify if required 
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

# Save mask without compression => Should be useless
def save_composite(output_path, composite, profile, output_name,compression):
    """Save the mask while preserving georeferencing."""
    if compression == 'n':
        profile.update(dtype='uint16', count=1, driver='GTiff')
    else:
        profile.update(
            dtype='uint16',
            count=1,
            driver='GTiff',
            compress='lzw',  # Use LZW compression
            tiled=True,  # Enable tiling
            blockxsize=256,  # Set tile width
            blockysize=256  # Set tile
        )
    with rasterio.open(os.path.join(output_path, output_name + '.tif'), 'w', **profile) as dst:
        dst.write(composite.astype('uint16'), 1)

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
    parser.add_argument(
        "-c", "--compression",
        dest="compression",
        type=str,
        help="Wether or not to compress the output image(s) (default: y)",
        default="y"
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
    for band in bands:
        corrected_bands[bands.index(band)] = apply_rayleigh_correction(
        input_path=args.input,
        target_res=args.resolution,
        band=band,
        resolution_method=args.method
        )
    Mask = applyWiPE(corrected_bands)
    profile = load_band(filepath=args.input, resolution=args.resolution)
    save_composite(output_path=Output, composite=Mask, profile=profile, output_name=args.name, compression=args.compression)
    print(f"Water mask image saved at {os.path.join(Output, args.name) + '.jp2'}")
    print(f"--- {time.time() - start_time} seconds ---")
    print(f"--- or {(time.time() - start_time)/60} minutes ---")
    print('Clearing __pycache__')
    files = glob(os.path.join(path, '__pycache__/*'))
    for f in files:
        os.remove(f)