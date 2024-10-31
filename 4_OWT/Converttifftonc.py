import os
import sys
import numpy as np
from glob import glob
from osgeo import gdal
import optparse
from pathlib import Path
import rasterio
from rasterio.enums import Resampling
from netCDF4 import Dataset

def list_files(directory_path,pattern):
    files_list = [str(file) for file in Path(directory_path).rglob(pattern)]
    return files_list

SRCPATH='/mnt/d/DATA/S2_PEPS_OWT'
OUTPUT='/mnt/d/DATA/S2_PEPS_OWT/nc/'
for pathdt in list_files(SRCPATH,'L1C_*_polymer20m.nc.tif'):
    if not os.path.exists(OUTPUT+Path(pathdt).name[0:34]+'.nc'):
        print('Output '+ Path(pathdt).name[0:34]+'.nc')
        gdal.Translate(OUTPUT+Path(pathdt).name[0:34]+'.nc',pathdt,format='NetCDF')
    else:
        print('image already exist, skipping...')

