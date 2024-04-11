# -*- coding: utf-8 -*-
"""
Created on Thu Apr 09 09:00:04 2024
@author: Julien Masson
"""
import re
import numpy as np
import xarray as xr
import rioxarray
import matplotlib.pyplot as plt
import pyproj
import retrieve_filename
import rasterio
from rasterio.enums import Resampling
#import geopandas as gpd
#import geodatasets
# import pandas as pd
# dico={'latitude':'y','longitude':'x'}
# ds=ds.rename(dico)
# ds=ds.set_coords('x')
# ds=ds.set_coords('y')
# ds=ds.rio.write_crs("EPSG:4326")
def zerooone(x):
    '''Return 1 if x>0 else 0'''
    if x>0:
        r=1
    else:
        r=0
    return r

# Definition des vars  ===========================
P = pyproj.Proj(proj='utm', zone=48, ellps='WGS84', preserve_units=True)
LOCAL_PROJ=32648
PATH = "/mnt/d/TEST/"
PATH_WIPE = '/mnt/d/TEST/Test_WiPE/2017/NEW/'
TILE = 'T48PUV'
KEEP = 'Rw443'

# Ouvrir le fichier .nc  ===========================
#xds = rxr.open_rasterio(path,masked=True)
list_img = retrieve_filename.POLYMER(TILE,PATH)
list_WiPE = retrieve_filename.WiPE(TILE,PATH_WIPE)
DROP = ['bitmask','Rnir','Rgli','logchl','bbs','Rw443','Rw490','Rw560'
      ,'Rw665','Rw705','Rw740','Rw783','Rw842','Rw865','Rw1610','logfb']
DROP.remove(KEEP)

ITER = 1
for image in list_img:
    with xr.open_dataset(image,decode_coords="all",drop_variables=DROP) as ds: #Open POLYMER img
        AA = P(ds.longitude.data,ds.latitude.data) # Reproject to UTM
        da = xr.DataArray(
            data = np.vectorize(zerooone)(ds[KEEP].data),
            dims = ["x","y"],
            coords = dict(
                    x = (["x"], np.unique(np.round(AA[0]))),
                    y = (["y"], np.unique(np.round(AA[1])))
            )
        )
    del ds
    match=re.findall(r'\d+',image)
    wipe_var=next((s for s in list_WiPE if match[3] in s),None)
    try :
        with rasterio.open(wipe_var) as dw: # Open WiPE img and resample it to 20m resolution
            WData = dw.read(
                    out_shape=(
                        dw.count,
                        int(dw.height * 0.5),
                        int(dw.width * 0.5)
                    ),
                    resampling=Resampling.bilinear
                )
    except ImportError:
        print("There's no WiPE Mask for a specific POLYMER Data. Is everything processed?")
    WData=WData[0].astype(int) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it
    if ITER==1:
        resultp=da
        resultw=WData
        difference=WData-da
    else:
        resultp=resultp+da
        resultw=resultw+WData
        difference=difference+(WData-da)
    ITER=ITER+1
#open corresponding WiPE
#Reinterpolation de WiPE
#Comparaison pixel


# plots?  ===========================
fig, ax = plt.subplots()

heatmap=ax.imshow(resultp,cmap='ocean',vmin=0)
cbar=plt.colorbar(heatmap)
