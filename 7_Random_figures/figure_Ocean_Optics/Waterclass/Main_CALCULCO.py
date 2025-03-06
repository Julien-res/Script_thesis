# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 14:49:11 2024

@author: Julien Masson

"""

WPATH='/mnt/c/Travail/Script/Chl-CONNECT/'   
import pandas as pd
import os
os.chdir(WPATH)
import common.meta as meta
import numpy as np
import xarray as xr
import glob
from common.Chl_CONNECT import Chl_CONNECT
from osgeo import gdal
# =============================================================================
# Variables
# =============================================================================

# INPUT = 
# WIPE_INPUT = 
PATH = "/mnt/d/TEST/"
PATH_POLYM=['/mnt/d/DATA/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer10m.nc',
            '/mnt/d/DATA/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer20m.nc',
            '/mnt/d/DATA/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer60m.nc']

MUDATA = os.path.join(WPATH,'MDB_1990_08_28_2023_07_17_modis_l2gen.csv')
BANDS = meta.SENSOR_BANDS['MSI-SOLID']
RRS = {}
RRS_MC = {}
# =============================================================================
# Function
# =============================================================================

def zerooone(x):
    '''Return 1 if x>0 else 0'''
    if x>0:
        r=1
    else:
        r=0
    return r

def polymer_zero(x):
    '''Replace values meaning no data to None'''
    if x>999999:
        r=None
    else:
        r=x
    return r

# =============================================================================
# Open data
# =============================================================================
data={}
convert=['lat','lon','Rrs443','Rrs490','Rrs560','Rrs665','Rrs705']

for i in PATH_POLYM:
    print (i)
    ds = gdal.Open('/mnt/d/DATA/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer60m.nc',gdal.GA_ReadOnly)
    DATA=[]
    for o in [0,1,7,8,9,10,11]: #0=lat,1=lon,7=Rw443,...
        band_ds = gdal.Open(ds.GetSubDatasets()[o][0], gdal.GA_ReadOnly)
        dw = band_ds.ReadAsArray()
        if o in [7,8,9,10,11]:
            dw = dw/np.pi #Convert Rw to Rrs
            dw=np.vectorize(polymer_zero)(dw)
            dw = dw.flatten() #.T
            DATA.append(dw)
#         data[convert[TIC]] = dw
#         TIC += 1
# df = pd.DataFrame(data)
# =============================================================================
# Load Rrs
# =============================================================================
# bands = [412, 443, 490, 560, 665, 705, 740, 783]
# Construct input

Rrs_mc_vis_nir = np.array(DATA).T

# =============================================================================
# Load Rrs
# =============================================================================
Chl_NN_mc = Chl_CONNECT(Rrs_mc_vis_nir,sensor='MSI')
Class = Chl_NN_mc.Class
