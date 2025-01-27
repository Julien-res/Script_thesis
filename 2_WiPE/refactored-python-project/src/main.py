# FILE: /refactored-python-project/refactored-python-project/src/main.py

import os
import time
import argparse
import numpy as np
from rayleigh_correction import RayleighCorrection
from apply_wipe import WiPE
from utils.file_operations import save_composite, load_band, clear_cache

def main():
    parser = argparse.ArgumentParser(description="Process satellite images with Rayleigh correction and WiPE.")
    parser.add_argument('--input', required=True, help='Input path to the Sentinel-2 file (SAFE format)')
    parser.add_argument('--output', default='stdout', help='Output directory or "stdout" for console output')
    parser.add_argument('--resolution', type=int, choices=[10, 20, 60], default=20, help='Desired resolution for the bands')
    parser.add_argument('--method', default='Sampling', help='Resampling method for Rayleigh correction')
    parser.add_argument('--name', default='water_mask', help='Output name for the water mask image')
    args = parser.parse_args()

    start_time = time.time()

    if args.output == 'stdout':
        os.makedirs('WiPE_Workspace', exist_ok=True)
        output_path = os.path.join(os.curdir, 'WiPE_Workspace')
    else:
        output_path = args.output

    bands = ["B2", "B3", "B4", "B7", "B10", "B11", "B12"]
    rayleigh_correction = RayleighCorrection(input_path=args.input, target_res=args.resolution, method=args.method)
    corrected_bands = rayleigh_correction.apply_correction(bands)

    wipe = WiPE()
    mask = wipe.apply(corrected_bands)

    profile = load_band(filepath=args.input, resolution=args.resolution)
    save_composite(output_path=output_path, composite=mask, profile=profile, output_name=args.name)

    print(f"Water mask image saved at {os.path.join(output_path, args.name) + '.jp2'}")
    print(f"--- {time.time() - start_time} seconds ---")
    print(f"--- or {(time.time() - start_time) / 60} minutes ---")
    
    clear_cache()

if __name__ == "__main__":
    main()