# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 14:49:11 2024

@author: Julien Masson

"""
# WORKDIR='/mnt/c/Travail/Script/Chl-CONNECT'
WORKDIR='/mnt/c/Users/Julien/Documents/Chl-CONNECT/'   
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

PATH = "/mnt/c/Users/Julien/Documents/WiPE_degrade_test/"
INPUT='/mnt/c/Users/Julien/Documents/WiPE_degrade_test/'
WIPE_INPUT = '/mnt/c/Users/Julien/Documents/WiPE_degrade_test/'
# PATH='/mnt/d/DATA/WiPE_degrade_test'
# INPUT='/mnt/d/DATA/WiPE_degrade_test'
# WIPE_INPUT='/mnt/d/DATA/WiPE_degrade_test'

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
        r=0
    else:
        r=x
    return r

def bitmaskp(x):
    if x in [1,2,4,8,16,32,64,128,512]:
        r=False
    else:
        r=True
    return r

def list_files(directory_path,pattern):
    files_list = [str(file) for file in Path(directory_path).rglob(pattern)]
    return files_list

# if __name__=='__main__':
#     class OptionParser (optparse.OptionParser):
#         def check_required(self, opt):
#             option = self.get_option(opt)
#             # Assumes the option's 'default' is set to None!
#             if getattr(self.values, option.dest) is None:
#                 self.error("%s option not supplied" % option)
#     if len(sys.argv) == 1:
#         TILENAME = open(os.path.join(WORKDIR,"List_tiles.txt"), "r")
#     else:
#         usage = "usage: %prog [options] "
#         parser = OptionParser(usage=usage)
#         parser.add_option("-t", "--tile", dest="tile", action="store", type="string",
#                         help="Entry (str): Tiles to treat"
#                         ,default=None)
#         (options, args) = parser.parse_args()

BANDS = meta.SENSOR_BANDS['MSI-SOLID']

# =============================================================================
# Open data
# =============================================================================

WET=[]
WETNUM=0
DRY=[]
DRYNUM=0
for name in TILENAME: # For all listed TILENAME
    WDATA={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
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
    for a in monthdic : #For all month
        t=0
        for i in monthdic[a] : # For all images in those month
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
            # Mask ==================
            dww=np.squeeze(dww.astype(int)) #Convert np.uint8 (0 to 255) to np.int64 and remove dim 1
            dww=np.vectorize(zerooone)(dww) #Convert to mask True or False to apply
            bitmask = gdal.Open(ds.GetSubDatasets()[3][0], gdal.GA_ReadOnly) #Polymer open
            bitmask = np.vectorize(bitmaskp)(bitmask)
            bitmask = np.where(dww,bitmask,0) #Fusion bitmask and WiPE to save compute time
            dww=None
            DATA = []
            for o in [7,8,9,10,11]: #0=lat,1=lon,7=Rw443,...
                band_ds = gdal.Open(ds.GetSubDatasets()[o][0], gdal.GA_ReadOnly) #Polymer open
                dw = band_ds.ReadAsArray()
                dw = dw/np.pi #Convert Rw to Rrs
                dw = np.where(bitmask,dw,0) #Apply Polymer and WiPE bitmask
                dw = dw.flatten() #.T # create vector from array
                DATA.append(dw) # create the 5 vector array to process
            dww=None
            bitmask=None
            if t == 0:
                WDATA[a] = np.array(DATA).T # convert as array and transpose
            else:
                WDATA[a] = WDATA[a] + np.array(DATA).T
            DATA=None
            t += 1
        # Classification
        if a in ('01','02','03','04','05','12'):
            if a == '01':
                DRY[a] = WDATA[a]
                DRYNUM = t
            else:
                DRY[a] = DRY[a] + WDATA[a]
                DRYNUM += t
        else:
            if a =='06':
                WET[a] = WDATA[a]
                WETNUM = t
            else:
                WET[a] = WET[a] + WDATA[a]
                WETNUM += t
        occurence[a] = t
        Class = Chl_CONNECT(WDATA[a]/t,sensor='MSI').Class
        WDATA[a] = np.reshape(Class, (-1, 5490))
        Class = None
        print ('Processing '+i+' month')
        if type(WDATA[a])==type(np.empty(0)):
            [rows, cols] = dw.shape
            driver = gdal.GetDriverByName("GTiff")
            outdata = driver.Create('Waterclass_'+a+'_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
            outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
            outdata.SetProjection(ds.GetProjection())##sets same projection as input
            outdata.GetRasterBand(1).WriteArray(WDATA[a])
            outdata.FlushCache() ##saves to disk!!
            outdata = None
    WDATA=None

    Class = Chl_CONNECT(WET/WETNUM,sensor='MSI').Class
    WET = np.reshape(Class, (-1, 5490))
    Class = None
    print ('Processing WET')
    if type(WET)==type(np.empty(0)):
        [rows, cols] = dw.shape
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create('Waterclass_WET_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
        outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(WET)
        outdata.FlushCache() ##saves to disk!!
        outdata = None

    Class = Chl_CONNECT(DRY/DRYNUM,sensor='MSI').Class
    DRY = np.reshape(Class, (-1, 5490))
    Class = None
    print ('Processing DRY')
    if type(DRY)==type(np.empty(0)):
        [rows, cols] = dw.shape
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create('Waterclass_DRY_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
        outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(DRY)
        outdata.FlushCache() ##saves to disk!!
        outdata = None


