# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 09:00:04 2024
@author: Julien Masson

Plot figure to show the impact of season, and location on detected water
"""
import os
import numpy as np
import xarray as xr
import rioxarray
import rasterio
from glob import glob
import matplotlib.pyplot as plt
import matplotlib.colormaps as cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from rasterio.enums import Resampling
import pyproj
from pathlib import Path
from osgeo import gdal
plt.style.use('dark_background')
###########################################################################

INPUT ='/mnt/d/DATA/WiPE/WiPE_Data_TEST/DATA'
OUTPUT='/mnt/d/DATA/WiPE/WiPE_Data_TEST/OUTPUT'
os.chdir(OUTPUT)
##================================================================================
WDATA={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
monthdic={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
Tile='*T48PUV*water.TIF'
for path in Path(INPUT).rglob(Tile):
    monthdic[path.name[15:17]].append(str(path))
    print (path.name)
for a in monthdic :
    for i in monthdic[a] :
        with gdal.Open(i) as ds: # Open WiPE img and resample it to 20m and 60m resolution
            width = ds.RasterXSize
            height = ds.RasterYSize
            gt = ds.GetGeoTransform()
            minx = gt[0]
            miny = gt[3] + width*gt[4] + height*gt[5] 
            maxx = gt[0] + width*gt[1] + height*gt[2]
            maxy = gt[3] 
            dw=ds.GetRasterBand(1)
            dw=dw.ReadAsArray()
        if type(WDATA[a])!=type(np.empty(0)) :
            WDATA[a]=dw.astype(int) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it
        else:
            WDATA[a]=WDATA[a]+dw.astype(int) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it

WDATA2={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
monthdic2={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
Tile='*T48PVV*water.TIF'
for path in Path(INPUT).rglob(Tile):
    monthdic2[path.name[15:17]].append(str(path))
    print (path.name)
for a in monthdic2 :
    for i in monthdic2[a] :
        with gdal.Open(i) as ds: # Open WiPE img and resample it to 20m and 60m resolution
            width = ds.RasterXSize
            height = ds.RasterYSize
            gt = ds.GetGeoTransform()
            minx2 = gt[0]
            miny2 = gt[3] + width*gt[4] + height*gt[5] 
            maxx2 = gt[0] + width*gt[1] + height*gt[2]
            maxy2 = gt[3] 
            dw=ds.GetRasterBand(1)
            dw=dw.ReadAsArray()
        if type(WDATA2[a])!=type(np.empty(0)) :
            WDATA2[a]=dw.astype(int) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it
        else:
            WDATA2[a]=WDATA2[a]+dw.astype(int) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it
for i in WDATA:
    if not WDATA[i] or not WDATA2[i]:
        print "Error: One image as no data for one month.\n" 
        sys.exit(1)
    else:
        WDATA[i]=np.concatenate((WDATA[i],WDATA2[i]),axis=1)
        
##================================================================================

WET=[]
WETNUM=0
DRY=[]
DRYNUM=0
for i in WDATA:
    if type(WDATA[i]) == type(np.empty(0)):
        if i in ('01','02','03','04','11','12'):
            if not WET :
                WET=WDATA[i]
                WETNUM=1
            else :
                WET=WET + WDATA[i]
                WETNUM=WETNUM+1
        elif not DRY  :
            DRY = WDATA[i]
            DRYNUM=1
        else :
            DRY = DRY + WDATA[i]
            DRYNUM=DRYNUM+1
    else:
        print("One whole month as no data=> Climatology won't work well")
##======================

##======================
for i in WDATA:
    if type(WDATA[i])==type(np.empty(0)):
        fig, axs = plt.subplots(figsize=(40, 20))
        axs.imshow(WDATA[i],cmap=newcmp)
        axs.tick_params(
            axis='both',
            which='both',
            bottom=True,
            top=False,
            labelbottom=True,
            labelsize=10)
        start, end = axs.get_ylim()
        start=int(start)
        end=int(end)
        axs.set_yticks(np.linspace(start=start,stop=end,num=3))
        axs.set_yticklabels(np.linspace(start=miny,stop=maxy,num=3)
                            ,minor=False,rotation=30)
        axs.set_xticks(np.linspace(start=start,stop=end,num=3))
        axs.set_xticklabels(np.linspace(start=maxx2,stop=minx,num=3)
                            ,minor=False,rotation=30)
        fig.colorbar(im,ax=axs,fraction=0.046, pad=0.04)
        plt.tight_layout()
        plt.subplots_adjust(wspace=0.1, hspace=0.1)
        plt.savefig(fname=os.path.join(os.getcwd(),'Water_presence'+i+'.png'),format='png',dpi=1000)

##======================
colorm = cm.get_cmap('cool', WETNUM+1)
newcolors = colorm(np.linspace(0, 1, WETNUM+1))
newcolors[:1, :] = np.array([0/256, 0/256, 0/256, 1])
newcmp = ListedColormap(newcolors)

fig, axs = plt.subplots(figsize=(40, 20))
axs.imshow(WET,cmap=newcmp)
axs.tick_params(
    axis='both',
    which='both',
    bottom=True,
    top=False,
    labelbottom=True,
    labelsize=10)
start, end = axs.get_ylim()
start=int(start)
end=int(end)
axs.set_yticks(np.linspace(start=start,stop=end,num=3))
axs.set_yticklabels(np.linspace(start=miny,stop=maxy,num=3)
                    ,minor=False,rotation=30)
axs.set_xticks(np.linspace(start=start,stop=end,num=3))
axs.set_xticklabels(np.linspace(start=maxx2,stop=minx,num=3)
                    ,minor=False,rotation=30)
fig.colorbar(im,ax=axs,fraction=0.046, pad=0.04)
plt.tight_layout()
plt.subplots_adjust(wspace=0.1, hspace=0.1)
plt.savefig(fname=os.path.join(os.getcwd(),'WET.png'),format='png',dpi=1000)

##======================
colorm = cm.get_cmap('cool', DRYNUM+1)
newcolors = colorm(np.linspace(0, 1, DRYNUM+1))
newcolors[:0, :] = np.array([0/256, 0/256, 0/256, 1])
newcmp = ListedColormap(newcolors)

fig, axs = plt.subplots(figsize=(40, 20))
im=axs.imshow(WET,cmap=newcmp)
axs.tick_params(
    axis='both',
    which='both',
    bottom=True,
    top=False,
    labelbottom=True,
    labelsize=20)
start, end = axs.get_ylim()
start=int(start)
end=int(end)
axs.set_yticks(np.linspace(start=start,stop=end,num=3))
axs.set_yticklabels(np.linspace(start=miny,stop=maxy,num=3)
                    ,minor=False,rotation=30)
axs.set_xticks(np.linspace(start=start,stop=end,num=3))
axs.set_xticklabels(np.linspace(start=maxx2,stop=minx,num=3)
                    ,minor=False,rotation=30)
cbar=fig.colorbar(im,ax=axs,fraction=0.046, pad=0.04)
cbar.ax.tick_params(labelsize=20) 
plt.tight_layout()
plt.subplots_adjust(wspace=0.1, hspace=0.1)
plt.savefig(fname=os.path.join(os.getcwd(),'DRY.png'),format='png',dpi=1000)