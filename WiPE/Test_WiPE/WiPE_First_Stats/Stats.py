# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 09:45:04 2024
@author: Julien Masson
"""
import os
import re
from datetime import datetime
import rioxarray as rxr
import pandas as pd
import numpy as np
import matplotlib as mp
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
sns.set_style("ticks")
import geopandas as gpd
from osgeo import gdal, ogr
os.chdir('/mnt/c/Travail/Script/Script_thesis/WiPE/Test_WiPE/WiPE_First_Stats')
from retrieve_filename import retrieve_filename

#=======================
Path_new='/mnt/c/Travail/TEST/Test_WiPE/2017/NEW/'
Path_old='/mnt/c/Travail/TEST/Test_WiPE/2017/OLD/'
#========================
puv_old,pvv_old,puv_new,pvv_new=retrieve_filename(Path_old,Path_new)

a=0
for i in puv_new:
    if a==0:
        ds = gdal.Open(i)
        gt = ds.GetGeoTransform()
        data = ds.ReadAsArray()
        ds = None
        ys, xs = data.shape
        ulx, xres, _, uly, _, yres = gt
        extent = [ulx, ulx+xres*xs, uly, uly+yres*ys] # Generate X and Y limits of the image
        col=range(int(extent[0]), int(extent[1]), int(xres))
        idx=range(int(extent[2]), int(extent[3]), int(yres))
    else:
        ds = gdal.Open(i)
        gt = ds.GetGeoTransform()
        data_1 = ds.ReadAsArray()
        ds = None
        data=np.add(data,data_1)
        data_1=None

    #Find the old WiPE mask matching the date of the new one
    match=re.findall(r'\d+',i)
    old_o=next((s for s in puv_old if (match[-2]+'T'+match[-1]) in s),None)

    if a==0:
        ds = gdal.Open(old_o)
        gt = ds.GetGeoTransform()
        data_o = ds.ReadAsArray()
        ds = None
        
    else:
        ds = gdal.Open(old_o)
        gt = ds.GetGeoTransform()
        data_o1 = ds.ReadAsArray()
        ds = None
        data_o=np.add(data_o,data_o1)
        data_o1=None
    a=a+1
#=======================
# Plot results


jet = cm.get_cmap('jet', 256)
newcolors = jet(np.linspace(0, 1, 256))
dark = np.array([0/256, 0/256, 0/256, 1])
newcolors[:1, :] = dark
newcmp = ListedColormap(newcolors)

sns.heatmap(data,cmap=newcmp,vmin=0,vmax=20,cbar_kws={'label': 'Percent of data retrieval'})
plt.show()

sns.heatmap(data_o,cmap=newcmp,vmin=0,vmax=20,cbar_kws={'label': 'Percent of data retrieval'})
plt.show() 

