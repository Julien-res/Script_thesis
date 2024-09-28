# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 14:49:11 2024

@author: Julien Masson

"""
# WORKDIR='/mnt/c/Travail/Script/Chl-CONNECT'
# WORKDIR='/mnt/c/Users/Julien/Documents/Chl-CONNECT/'   
WORKDIR='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_WiPE/Figure_OO/Chl-CONNECT/'

import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
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
import itertools
from netCDF4 import Dataset
from operator import add
# =============================================================================
# Variables
# =============================================================================

# INPUT = 
# WIPE_INPUT = 

# PATH = "/mnt/c/Users/Julien/Documents/WiPE_degrade_test/"
# INPUT='/mnt/c/Users/Julien/Documents/WiPE_degrade_test/'
# WIPE_INPUT = '/mnt/c/Users/Julien/Documents/WiPE_degrade_test/'

# PATH='/mnt/d/DATA/WiPE_degrade_test'
# INPUT='/mnt/d/DATA/WiPE_degrade_test'
# WIPE_INPUT='/mnt/d/DATA/WiPE_degrade_test'
# TILENAME=['T48PWS']
INPUT='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_Polymer_20m/'
WIPE_INPUT='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_WiPE/RAW/'
OUTPUT='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_WiPE/Figure_OO/Class_OUT/'

def zerooone(x):
    if x==0:
        r=False
    else:
        r=True
    return r


def polymer_zero(x):
    '''Replace values meaning no data to None'''
    if x>999999:
        r=np.nan
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

if __name__=='__main__':
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
        TILEWIPE = '*' + name + '_' + Path(path).name[19:27] + '*water.TIF'
        WPE = list_files(WIPE_INPUT,TILEWIPE)
        if not WPE:
            print('Missing WiPE mask, skipping data...')
        else:
            monthdic[Path(path).name[23:25]].append(path)
            print (Path(path).name)
            monthdicW[Path(WPE[0]).name[15:17]].append(WPE[0])
            print (Path(WPE[0]).name)
    data={}
    convert=['Rw443','Rw490','Rw560','Rw665','Rw705']
    for a in monthdic : #For all month
        t=0
        print('number of elem to treat this month : '+str(len(monthdic[a])))
        for i in monthdic[a] : # For all images in those month
            print (i)
            # ds=gdal.Open(i,gdal.GA_ReadOnly)
            DATA=[]
            with Dataset(i, mode='r') as ds:
                bitmask=ds.variables['bitmask'][:].data
                for wl in convert:
                    data=ds.variables[wl][:].data/np.pi
                    DATA.append(data)
                    print(data.shape)
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
            dww=np.squeeze(dww) #Convert np.uint8 (0 to 255) to np.int64 and remove dim 1
            dww=dww.astype(bool) #Convert to mask True or False to apply
            # bitmask = gdal.Open(ds.GetSubDatasets()[2][0], gdal.GA_ReadOnly).ReadAsArray() #Polymer open
            bitmask = np.vectorize(bitmaskp)(np.flip(bitmask,axis=0)) #Convert bitmask to True or False, and flip it to correspond WiPE projection
            # bitmask = np.vectorize(bitmaskp)(bitmask) #Convert bitmask to True or False, and flip it to correspond WiPE projection
            bitmask = np.where(dww,bitmask,False) #Fusion bitmask and WiPE to save compute time
            driver = gdal.GetDriverByName("GTiff")
            outdata = driver.Create(OUTPUT+'bitmask_'+str(t)+a+'_'+name+'.tif', 5490, 5490, 1, gdal.GDT_UInt16) #UInt16
            dwt=gdal.Open(monthdicW[a][0], gdal.GA_ReadOnly)
            geot=dwt.GetGeoTransform()
            geot=(geot[0],geot[1]*2,geot[2],geot[3],geot[4],geot[5]*2)
            outdata.SetGeoTransform(geot)##sets same geotransform as input
            outdata.SetProjection(dwt.GetProjection())##sets same projection as input
            outdata.GetRasterBand(1).WriteArray(bitmask.astype(int))
            outdata.FlushCache() ##saves to disk!!
            outdata = None
            if t==0:
                occurence[a]=bitmask.astype(int)
            else:
                occurence[a]= occurence[a] + bitmask.astype(int)
            dww=None
            # for o in [7,8,9,10,11]: #0=lat,1=lon,7=Rw443,...
            #     band_ds = gdal.Open(ds.GetSubDatasets()[o][0], gdal.GA_ReadOnly) #Polymer open
            #     dw = band_ds.ReadAsArray()
            #     dw = dw/np.pi #Convert Rw to Rrs
            #     dw = np.where(bitmask,dw,np.nan) #Apply Polymer and WiPE bitmask
            #     dw = dw.flatten() #.T # create vector from array
            #     DATA.append(dw) # create the 5 vector array to process
            for b in range(0,len(DATA)):
                DATA[b] = np.where(bitmask,DATA[b],np.nan) #apply bitmask
            if np.isnan(DATA[0]).all():
                print('DATA is all nan at point 2')
                sys.exit(-1)
            dww=None
            bitmask=None
            if t == 0:
                WDATA[a] = DATA
            else:
                WDATA[a] = list( map(add, WDATA[a], DATA))
            DATA=None
            t += 1
            if np.isnan(WDATA[a][0]).all():
                print('WDATA[a] is all nan at point 3')
                sys.exit(-1)
        print ('Processing ' + a + ' month')
        # Classification
        if a in ('01','02','03','04','05','12'):
            if a == '01':
                DRY = WDATA[a]
                DRYNUM = occurence[a]
            else:
                DRY = list( map(add, WDATA[a], DRY))
                DRYNUM = DRYNUM + occurence[a]
        else:
            if a =='06':
                WET = WDATA[a]
                WETNUM = occurence[a]
            else:
                WET = list( map(add, WDATA[a], WET))
                WETNUM = WETNUM + occurence[a]
        tmp=[]
        print (len(WDATA[a]))
        for b in range(0,len(WDATA[a])):
            print (WDATA[a][b].shape)
            if not np.isnan(WDATA[a][b]).all():
                print('OK not empty')
                tmp.append(WDATA[a][b]/occurence[a])
                if np.isnan(tmp[b]).all():
                    sys.exit(-1)
                print(tmp[b])
            else:
                print('WDATA[a] '+str(b)+' all nan!')
        print (WDATA[a][b])
        WDATA[a] = Chl_CONNECT(tmp,method='logreg',sensor='MSI',logRrsClassif=False,pTransform=False).Class
        print('Output'+a)
        if type(WDATA[a]) == type(np.empty(0)):
            driver = gdal.GetDriverByName("GTiff")
            outdata = driver.Create(OUTPUT+'Waterclass_'+a+'_'+name+'.tif', 5490, 5490, 1, gdal.GDT_UInt16) #UInt16
            dwt=gdal.Open(monthdicW[a][0], gdal.GA_ReadOnly)
            geot=dwt.GetGeoTransform()
            geot=(geot[0],geot[1]*2,geot[2],geot[3],geot[4],geot[5]*2)
            outdata.SetGeoTransform(geot)##sets same geotransform as input
            outdata.SetProjection(dwt.GetProjection())##sets same projection as input
            outdata.GetRasterBand(1).WriteArray(WDATA[a])
            outdata.FlushCache() ##saves to disk!!
            outdata = None
    DRYA=[]
    WETA=[]
    for z in range(0,len(DRY)):
        DRYA.append(DRY[z]/DRYNUM)
        WETA.append(WET[z]/WETNUM)
    WDATA=None
    Class = Chl_CONNECT(WETA,sensor='MSI').Class
    print ('Processing WET')
    if type(WET)==type(np.empty(0)):
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(OUTPUT+'Waterclass_WET_'+name+'.tif', 5490, 5490, 1, gdal.GDT_UInt16) #UInt16
        dwt=gdal.Open(monthdicW[a][0], gdal.GA_ReadOnly)
        geot=dwt.GetGeoTransform()
        geot=(geot[0],geot[1]*2,geot[2],geot[3],geot[4],geot[5]*2)
        outdata.SetGeoTransform(geot)##sets same geotransform as input
        outdata.SetProjection(dwt.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(Class)
        outdata.FlushCache() ##saves to disk!!
        outdata = None

    Class = Chl_CONNECT(DRYA,sensor='MSI').Class
    print ('Processing DRY')
    if type(DRY)==type(np.empty(0)):
        [rows, cols] = dw.shape
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(OUTPUT+'Waterclass_DRY_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
        dwt=gdal.Open(monthdicW[a][0], gdal.GA_ReadOnly)
        geot=dwt.GetGeoTransform()
        geot=(geot[0],geot[1]*2,geot[2],geot[3],geot[4],geot[5]*2)
        outdata.SetGeoTransform(geot)##sets same geotransform as input
        outdata.GetRasterBand(1).WriteArray(Class)
        outdata.FlushCache() ##saves to disk!!
        outdata = None


