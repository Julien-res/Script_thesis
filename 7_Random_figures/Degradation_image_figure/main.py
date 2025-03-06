# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 14:47:04 2024
@author: Julien Masson

Plot figure to show the impact of a lowering resolution on WiPE, colored image and POLYMER
"""
import os
import numpy as np
import xarray as xr
import rioxarray
import rasterio
import matplotlib.pyplot as plt
from rasterio.enums import Resampling
import pyproj
# Definition des vars  ===========================
os.chdir('/mnt/c/Travail/Script/Script_thesis/2_WiPE/Degradation_image_figure')
P = pyproj.Proj(proj='utm', zone=48, ellps='WGS84', preserve_units=True)
LOCAL_PROJ=32648
PATH = "/mnt/d/TEST/"
PATH_WIPE = '/mnt/d/DATA/WiPE_degrade_test/S2A_T48PWS_20210219T031751_water.TIF'
PATH_IMG = '/mnt/d/DATA/WiPE_degrade_test/S2A_MSIL1C_20210219T031751_N0209_R118_T48PWS_20210219T060828.SAFE/GRANULE/L1C_T48PWS_A029573_20210219T033017/IMG_DATA/T48PWS_20210219T031751_TCI.jp2'
PATH_POLYM=['/mnt/d/DATA/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer10m.nc',
            '/mnt/d/DATA/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer20m.nc',
            '/mnt/d/DATA/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer60m.nc']
KEEP = 'Rw443'
DROP = ['bitmask','Rnir','Rgli','logchl','bbs','Rw443','Rw490','Rw560'
      ,'Rw665','Rw705','Rw740','Rw783','Rw842','Rw865','Rw1610','logfb']
DROP.remove(KEEP)

def zerooone(x):
    '''Return 1 if x>0 else 0'''
    if x>0:
        r=1
    else:
        r=0
    return r

# Importation des données IMG  ===========================
RDATA=[]
for i in [1,0.5,10/60]:
    with rasterio.open(PATH_IMG) as dw: # Open WiPE img and resample it to 20m and 60m resolution
        IMG = dw.read(
        out_shape=(
            dw.count,
            int(dw.height*i),
            int(dw.width*i)
                ),
                resampling=Resampling.nearest
            )
    RDATA.append(IMG)
# Importation des données WiPE  ===========================
WDATA=[]
for i in [1,0.5,10/60]:
    with rasterio.open(PATH_WIPE) as dw: # Open WiPE img and resample it to 20m and 60m resolution
        WDAT = dw.read(
        out_shape=(
            dw.count,
            int(dw.height*i),
            int(dw.width*i)
            ),
            resampling=Resampling.nearest
        )
    WDATA.append(WDAT.astype(int)) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it

# Importation des données Polymer  ========================
PDATA=[]
for i in PATH_POLYM:
    with xr.open_dataset(i,decode_coords="all",drop_variables=DROP) as ds:
        AA = P(ds.longitude.data,ds.latitude.data) # Reproject to UTM
        Coordx=np.unique(np.round(AA[0]))
        Coordy=np.unique(np.round(AA[1]))
        da = xr.DataArray(
            data = np.vectorize(zerooone)(ds[KEEP].data),
            dims = ["x","y"],
            coords = dict(
                    x = (["x"], Coordx),
                    y = (["y"], Coordy)
            )
        )
    PDATA.append(da)

# Plots figures ==========================================
fig, axs = plt.subplots(3, 3, figsize=(20, 20))
plt.title('Degradation with loss of resolution')
tit=['10m','20m','60m']
a=0
for i in RDATA:
    axs[0,a].imshow(i.transpose(1,2,0),cmap='Greys')
    if a==0:
        axs[0,a].tick_params(
            axis='x',
            which='both',
            bottom=False,
            top=False,
            labelbottom=False)
        start, end = axs[0,a].get_ylim()
        start=int(start)
        end=int(end)
        axs[0,a].set_yticks(np.linspace(start=start,stop=end,num=3))
        axs[0,a].set_yticklabels(np.linspace(start=Coordy[0],stop=Coordy[-1],num=3)
                            ,minor=False,rotation=30)
        axs[0,a].title.set_text('RGB image'+'\n'+tit[a])
    else:
        axs[0,a].tick_params(
            axis='both',
            which='both',
            bottom=False,
            top=False,
            left=False,
            labelbottom=False,
            labelleft=False)
        axs[0,a].title.set_text(tit[a])
    
    a=a+1
a=0
for i in WDATA:
    axs[1,a].imshow(i[0],cmap='Greys')
    if a==0:
        axs[1,a].tick_params(
            axis='x',
            which='both',
            bottom=False,
            top=False,
            labelbottom=False)
        start, end = axs[1,a].get_ylim()
        start=int(start)
        end=int(end)
        axs[1,a].set_yticks(np.linspace(start=start,stop=end,num=3))
        axs[1,a].set_yticklabels(np.linspace(start=Coordy[0],stop=Coordy[-1],num=3)
                            ,minor=False,rotation=30)
        axs[1,a].title.set_text('WiPE mask'+'\n'+tit[a])
    else:
        axs[1,a].tick_params(
            axis='both',
            which='both',
            bottom=False,
            top=False,
            left=False,
            labelbottom=False,
            labelleft=False)
        axs[1,a].title.set_text(tit[a])
    a=a+1
a=0
for i in PDATA:
    axs[2,a].imshow(i,cmap='Greys')
    if a!=0:
        axs[2,a].tick_params(
            axis='y',
            which='both',
            bottom=False,
            top=False,
            left=False,
            labelbottom=False,
            labelleft=False)
        start, end = axs[2,a].get_xlim()
        start=int(start)
        end=int(end)
        axs[2,a].set_xticks(np.linspace(start=start,stop=end,num=3))
        axs[2,a].set_xticklabels(np.linspace(start=Coordx[0],stop=Coordx[-1],num=3)
                            ,minor=False,rotation=30)
        axs[2,a].title.set_text(tit[a])
    else:
        start, end = axs[2,a].get_xlim()
        start=int(start)
        end=int(end)
        axs[2,a].set_xticks(np.linspace(start=start,stop=end,num=3))
        axs[2,a].set_xticklabels(np.linspace(start=Coordx[0],stop=Coordx[-1],num=3)
                            ,minor=False,rotation=30)
        start, end = axs[2,a].get_ylim()
        start=int(start)
        end=int(end)
        axs[2,a].set_yticks(np.linspace(start=start,stop=end,num=3))
        axs[2,a].set_yticklabels(np.linspace(start=Coordy[0],stop=Coordy[-1],num=3)
                            ,minor=False,rotation=30)
        axs[2,a].title.set_text('Polymer mask'+'\n'+tit[a])
    a=a+1

plt.tight_layout()
plt.subplots_adjust(wspace=0.1, hspace=0.1)
plt.savefig(fname=os.path.join(os.getcwd(),'Difference.png'),format='png',dpi=1000)
