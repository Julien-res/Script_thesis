# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 14:47:04 2024
@author: Julien Masson

Plot impact of sunglint and retrieval possibility with WiPE
"""
import os
import numpy as np
import xarray as xr
import rioxarray
import rasterio
import matplotlib.pyplot as plt
import pyproj
from rasterio.enums import Resampling
import ast
import re
# Definition des vars  ===========================
os.chdir('/mnt/c/Travail/Script/Script_thesis/2_WiPE/Degradation_image_figure')
P = pyproj.Proj(proj='utm', zone=48, ellps='WGS84', preserve_units=True)
LOCAL_PROJ=32648
PATH = "/mnt/d/TEST/"

PATH_WIPE = '/mnt/c/Travail/Script/Script_thesis/3_CA/WiPE_before_or_after/Sunglint_retrieval_test/Data/S2A_T48PUV_20170504T032541_water.TIF'
PATH_POLYM=['/mnt/c/Travail/Script/Script_thesis/3_CA/WiPE_before_or_after/Sunglint_retrieval_test/Data/L1C_T48PUV_A009739_20170504T034240_polymer10m.nc',
            '/mnt/c/Travail/Script/Script_thesis/3_CA/WiPE_before_or_after/Sunglint_retrieval_test/Data/L1C_T48PUV_A009739_20170504T034240_polymer20m.nc']
KEEP = 'bitmask'
#=============================
DROP = ['bitmask','Rnir','Rgli','logchl','bbs','Rw443','Rw490','Rw560'
      ,'Rw665','Rw705','Rw740','Rw783','Rw842','Rw865','Rw1610','logfb']
DROP.remove(KEEP)

# Importation des données WiPE  ===========================
WDATA=[]
for i in [1,0.5]:
    with rasterio.open(PATH_WIPE) as dw: # Open WiPE img and resample it to 20m and 60m resolution
        WDAT = dw.read(
        out_shape=(
            dw.count,
            int(dw.height*i),
            int(dw.width*i)
            ),
            resampling=Resampling.nearest
        )
    WDATA.append(WDAT[0].astype(int)) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it

# Importation des données Polymer  ========================
PDATA=[]
for i in PATH_POLYM:
    with xr.open_dataset(i,decode_coords="all",drop_variables=DROP) as ds:
        AA = P(ds.longitude.data,ds.latitude.data) # Reproject to UTM
        Coordx=np.unique(np.round(AA[0]))
        Coordy=np.unique(np.round(AA[1]))
        da = xr.DataArray(
            data = ds[KEEP].data,
            dims = ["x","y"],
            coords = dict(
                    x = (["x"], Coordx),
                    y = (["y"], Coordy)
            )
        )
    PDATA.append(da.astype(int))


# Creation du dic pour commprend le bitmask  ==============
dic=ds.bitmask.description
Listname=dic.split()
Listnum=re.findall(r'\d+',dic)
del Listnum[2]
del Listnum[-4]
dicti={}
itr=0
for i in Listname:
    name=i[0:i.find(':')]
    dicti[int(Listnum[itr])]=name
    itr=itr+1

# Plot  =================================================
fig, axs = plt.subplots(2,6, figsize=(12,4))
plt.title('Bitmask test')
B=0
for i in Listnum:
    if B<6:
        TEST = np.where(PDATA[0]!=int(i), -999999, PDATA[0])
        heatmap = axs[0,B].imshow(TEST,cmap='Greys')
        axs[0,B].tick_params(
            axis='both',
            which='both',
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False)
        axs[0,B].title.set_text(dicti[int(i)])
        B=B+1
    else:
        TEST = np.where(PDATA[0]!=int(i), 999999, PDATA[0])
        heatmap = axs[1,B-6].imshow(TEST,cmap='Greys')
        axs[1,B-6].tick_params(
            axis='both',
            which='both',
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False)
        axs[1,B-6].title.set_text(dicti[int(i)])
        B=B+1
plt.tight_layout()
plt.savefig(fname=os.path.join(os.getcwd(),'Bitmask.png'),format='png',dpi=1000)