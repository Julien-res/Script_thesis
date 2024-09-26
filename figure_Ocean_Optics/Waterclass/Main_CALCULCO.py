# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 14:49:11 2024

@author: Julien Masson

"""
WORKDIR='/mnt/c/Travail/Script/Chl-CONNECT'
# WORKDIR='/mnt/c/Users/Julien/Documents/Chl-CONNECT/'   
import pandas as pd
import os
import sys
os.chdir(WORKDIR)
import common.meta as meta
import numpy as np
import numpy.ma as ma
import xarray as xr
from glob import glob
from common.Chl_CONNECT import Chl_CONNECT
from osgeo import gdal
import optparse
from pathlib import Path
import rasterio
from rasterio.enums import Resampling
# =============================================================================
# Variables
# =============================================================================

# INPUT = 
# WIPE_INPUT = 

# PATH = "/mnt/c/Users/Julien/Documents/WiPE_degrade_test/"
# INPUT='/mnt/c/Users/Julien/Documents/WiPE_degrade_test/'
# WIPE_INPUT = '/mnt/c/Users/Julien/Documents/WiPE_degrade_test/'
PATH='/mnt/d/DATA/WiPE_degrade_test'
INPUT='/mnt/d/DATA/WiPE_degrade_test'
WIPE_INPUT='/mnt/d/DATA/WiPE_degrade_test'

TILENAME='T48PWS'

def zerooone(x):
    if x==0:
        r=False
    else:
        r=True
    return r

def polymer_zero(x):
    '''Replace values meaning no data to None'''
    if x>999999:
        r=None
    else:
        r=x
    return r

def list_files(directory_path,pattern):
    files_list = [str(file) for file in Path(directory_path).rglob(pattern)]
    return files_list

class OptionParser (optparse.OptionParser):
    def check_required(self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)

if len(sys.argv) == 1:
    TILENAME = open(os.path.join(WORKDIR,"List_tiles.txt"), "r")
else:
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)

    parser.add_option("-t", "--tile", dest="tile", action="store", type="string",
                    help="Entry (str): Tiles to treat"
                    ,default=None)
    (options, args) = parser.parse_args()

PATH_POLYM=['/mnt/c/Users/Julien/Documents/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer10m.nc',
            '/mnt/c/Users/Julien/Documents/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer20m.nc',
            '/mnt/c/Users/Julien/Documents/WiPE_degrade_test/L1C_T48PWS_A029573_20210219T033017_polymer60m.nc']

BANDS = meta.SENSOR_BANDS['MSI-SOLID']
RRS = {}
RRS_MC = {}

# =============================================================================
# Open data
# =============================================================================
for name in TILENAME:
    WDATA={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    WDATAPERC={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    monthdic={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    monthdicW={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    occurence={}
    name=name.rstrip()
    TILE='*'+name+'*_polymer20m.nc'
    for path in list_files(INPUT,TILE):
        monthdic[Path(path).name[23:25]].append(path)
        print (Path(path).name)
        TILEWIPE = '*' + name + '_' + Path(path).name[19:27] + '*water.TIF'
        WPE = list_files(WIPE_INPUT,TILEWIPE)
        if len(WPE[0]) != 0:
            monthdicW[Path(WPE[0]).name[15:17]].append(WPE[0])
            print (Path(WPE[0]).name)
        else:
            print('Missing WiPE mask, skipping data...')
            del monthdic[Path(path).name[23:25]][-1]
    data={}
    convert=['lat','lon','Rrs443','Rrs490','Rrs560','Rrs665','Rrs705']
    for a in monthdic :
        t=0
        for i in monthdic[a] :
            print (i)
            ds=gdal.Open(i,gdal.GA_ReadOnly)
            with rasterio.open(monthdicW[a][t]) as dsw: # Open WiPE img and resample it to 20m
                dww = dsw.read(
                out_shape=(
                    dsw.count,
                    int(dsw.height*0.5),
                    int(dsw.width*0.5)
                    ),
                    resampling=Resampling.nearest
                )
            dww=np.squeeze(dww.astype(int)) #Convert np.uint8 (0 to 255) to np.int64 and remove dim 1
            dww=np.vectorize(zerooone)(dww)
            DATA = []
            for o in [7,8,9,10,11]: #0=lat,1=lon,7=Rw443,...
                band_ds = gdal.Open(ds.GetSubDatasets()[o][0], gdal.GA_ReadOnly) #Polymer open
                dw = band_ds.ReadAsArray()
                dw = dw/np.pi #Convert Rw to Rrs
                dw = np.where(dww,dw,9999999) #Apply WiPE mask
                dw = np.vectorize(polymer_zero)(dw)
                dw = dw.flatten() #.T
                DATA.append(dw)
            Rrs_mc_vis_nir = np.array(DATA).T
            # Classification
            Class = Chl_CONNECT(Rrs_mc_vis_nir,sensor='MSI').Class
            Class = np.reshape(Class, (-1, 5490))
            t += 1

    


    
    
