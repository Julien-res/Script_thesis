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

def testnan(x):
    if x==False:
        r=np.nan
    else:
        r=x
    return r

def polymernan(x):
    if x==np.inf or x==(-np.inf) or x==0:
        r=np.nan
    else:
        r=x
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
        TILENAME = [options.tile]

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
    for month in monthdic : #For all month
        t=0
        print('number of elem to treat this month : '+str(len(monthdic[month])))
        print(monthdic[month])
        i=None
        for pathdt in monthdic[month] : # For all images in those month
            print (pathdt)
            # ds=gdal.Open(pathdt,gdal.GA_ReadOnly)
            DATA=[]
            with Dataset(pathdt, mode='r') as ds:
                bitmask=ds.variables['bitmask'][:].data
                for wl in convert:
                    data=ds.variables[wl][:].data/np.pi
                    DATA.append(data)
                    print(data.shape)
            with rasterio.open(monthdicW[month][t]) as dsw: # Open WiPE img and resample it to 20m
                dww = dsw.read(
                out_shape=(
                    dsw.count,
                    int(dsw.height*0.5),
                    int(dsw.width*0.5)
                    ),
                    resampling=Resampling.nearest
                )
                print('Watermask Opened')
            # Mask ==================
            dww=np.squeeze(dww) #Convert np.uint8 (0 to 255) to np.int64 and remove dim 1
            dww=dww.astype(bool) #Convert to mask True or False to apply
            # bitmask = gdal.Open(ds.GetSubDatasets()[2][0], gdal.GA_ReadOnly).ReadAsArray() #Polymer open
            bitmask = np.vectorize(bitmaskp)(np.flip(bitmask,axis=0)) #Convert bitmask to True or False, and flip it to correspond WiPE projection
            # bitmask = np.vectorize(bitmaskp)(bitmask) #Convert bitmask to True or False, and flip it to correspond WiPE projection
            bitmask = np.where(dww,bitmask,False) #Fusion bitmask and WiPE to save compute time
            if t==0:
                occurence[month]=bitmask.astype(int)
            else:
                occurence[month]= occurence[month] + bitmask.astype(int)
            dww=None
            # for o in [7,8,9,10,11]: #0=lat,1=lon,7=Rw443,...
            #     band_ds = gdal.Open(ds.GetSubDatasets()[o][0], gdal.GA_ReadOnly) #Polymer open
            #     dw = band_ds.ReadAsArray()
            #     dw = dw/np.pi #Convert Rw to Rrs
            #     dw = np.where(bitmask,dw,np.nan) #Apply Polymer and WiPE bitmask
            #     dw = dw.flatten() #.T # create vector from array
            #     DATA.append(dw) # create the 5 vector array to process
            if np.isnan(np.vectorize(testnan)(bitmask)).all():
                print('Empty bitmask, no data')
            for b in range(0,len(DATA)):
                DATA[b] = np.where(bitmask,DATA[b],0) #apply bitmask

            if t == 0:
                WDATA[month] = DATA
            else:
                WDATA[month] = list( map(add, WDATA[month], DATA))
            dww=None
            bitmask=None
            DATA=None
            t += 1
        print (t)
        print(str(t) + ' treated out of '+ str(len(monthdic[month])))
        if t != len(monthdic[month]):
            print('ERROR, LESS MONTH TREATED THAN EXPECTED, CHECK CODE')
            sys.exit(-1)
        
        print ('Processing ' + month + ' month')
        # Classification
        if month in ('01','02','03','04','05','12'):
            if month == '01':
                DRY = WDATA[month]
                DRYNUM = occurence[month]
            else:
                DRY = list( map(add, WDATA[month], DRY))
                DRYNUM = DRYNUM + occurence[month]
        else:
            if month =='06':
                WET = WDATA[month]
                WETNUM = occurence[month]
            else:
                WET = list( map(add, WDATA[month], WET))
                WETNUM = WETNUM + occurence[month]
        if len(list_files(OUTPUT,'Waterclass_'+month+'_'+name+'.tif'))==0:
            tmp=[]
            print ('number of bands out of 5 : ' + str(len(WDATA[month])))
            CONTROLE=0
            for b in range(0,len(WDATA[month])):
                if not np.isnan(WDATA[month][b]).all():
                    print('OK, bands not empty')
                    tmpp=WDATA[month][b]/occurence[month]
                    tmp.append(np.vectorize(polymernan)(tmpp))
                    if np.isnan(tmp[b]).all():
                        print('WDATA DATA NOT EMPTY BUT TMP EMPTY, ERROR')
                        sys.exit(-1)
                    print(tmp[b])
                else:
                    print('WDATA[month] '+str(b)+' all nan!')
                    CONTROLE=1
            print (WDATA[month][b])
            WDATA[month] = Chl_CONNECT(tmp,method='logreg',sensor='MSI',logRrsClassif=False,pTransform=False).Class
            print('Output'+month)
            if CONTROLE==0:
                driver = gdal.GetDriverByName("GTiff")
                outdata = driver.Create(OUTPUT+'Waterclass_'+month+'_'+name+'.tif', 5490, 5490, 1, gdal.GDT_UInt16) #UInt16
                dwt=gdal.Open(monthdicW[month][0], gdal.GA_ReadOnly)
                geot=dwt.GetGeoTransform()
                geot=(geot[0],geot[1]*2,geot[2],geot[3],geot[4],geot[5]*2)
                outdata.SetGeoTransform(geot)##sets same geotransform as input
                outdata.SetProjection(dwt.GetProjection())##sets same projection as input
                outdata.GetRasterBand(1).WriteArray(WDATA[month])
                outdata.FlushCache() ##saves to disk!!
                outdata = None
            else:
                print('Not printing data, as WDATA[month] is all nan')
            CONTROLE=0
        else:
            print('skipping one month as it already exist locally. If you want to reprocess, please delete')

    if len(list_files(OUTPUT,'Waterclass_WET_'+name+'.tif'))==0:
        DRYA=[]
        WETA=[]
        for z in range(0,len(DRY)):
            DRYA.append(DRY[z]/DRYNUM)
            WETA.append(WET[z]/WETNUM)
        WDATA=None
        Class = Chl_CONNECT(WETA,sensor='MSI').Class
        print ('Processing WET')
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(OUTPUT+'Waterclass_WET_'+name+'.tif', 5490, 5490, 1, gdal.GDT_UInt16) #UInt16
        dwt=gdal.Open(monthdicW[month][0], gdal.GA_ReadOnly)
        geot=dwt.GetGeoTransform()
        geot=(geot[0],geot[1]*2,geot[2],geot[3],geot[4],geot[5]*2)
        outdata.SetGeoTransform(geot)##sets same geotransform as input
        outdata.SetProjection(dwt.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(Class)
        outdata.FlushCache() ##saves to disk!!
        outdata = None
    else:
        print('skipping WET as it already exist locally. If you want to reprocess, please delete')
    if len(list_files(OUTPUT,'Waterclass_DRY_'+name+'.tif'))==0:
        Class = Chl_CONNECT(DRYA,sensor='MSI').Class
        print ('Processing DRY')
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(OUTPUT+'Waterclass_DRY_'+name+'.tif', 5490, 5490, 1, gdal.GDT_UInt16) #UInt16
        dwt=gdal.Open(monthdicW[month][0], gdal.GA_ReadOnly)
        geot=dwt.GetGeoTransform()
        geot=(geot[0],geot[1]*2,geot[2],geot[3],geot[4],geot[5]*2)
        outdata.SetGeoTransform(geot)##sets same geotransform as input
        outdata.GetRasterBand(1).WriteArray(Class)
        outdata.FlushCache() ##saves to disk!!
        outdata = None
    else:
        print('skipping DRY as it already exist locally. If you want to reprocess, please delete')
