# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 14:49:11 2024

@author: Julien Masson

"""
# WORKDIR='/mnt/c/Travail/Script/Chl-CONNECT'
# WORKDIR='/mnt/c/Users/Julien/Documents/Chl-CONNECT/'   
WORKDIR='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_WiPE/Figure_OO/'

import os
os.chdir(WORKDIR)
import sys
import pandas as pd
import os
import sys
import numpy as np
import numpy.ma as ma
import xarray as xr
from glob import glob
from osgeo import gdal
import optparse
from pathlib import Path
INPUT_DATA='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_Sen2Cor/pvu_pvv_puv/MEAN/'
OUTPUT_DATA='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_WiPE/Figure_OO/SPM_OUT/'

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

def list_files(directory_path,pattern):
    files_list = [str(file) for file in Path(directory_path).rglob(pattern)]
    return files_list

def maski(x):
    if x>0:
        r=x
    else:
        r=0
    return(r)


for name in TILENAME: # For all listed TILENAME
    WDATA={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    monthdic={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    occurence={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    name=name.rstrip()
    TILE='S2_'+name+'_S2COR_*_SPMH_MEAN.tif'
    for path in list_files(INPUT_DATA,TILE):
        print (Path(path).name)
        monthdic[Path(path).name[18:20]].append(path)

    for month in monthdic :
        t=0
        for pathdt in monthdic[month] :
            print (pathdt)
            ds=gdal.Open(pathdt)
            dw=ds.GetRasterBand(1)
            dw=dw.ReadAsArray()
            [rows, cols] = dw.shape
            # tmp = scipy.ndimage.convolve(dw, np.ones((3,3)), mode='constant')
            # dw = np.logical_and(tmp >= 2, dw)
            # tmp=None
            if type(WDATA[month])!=type(np.empty(0)) :
                WDATA[month]=dw.astype(int) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it
                occurence[month]=np.vectorize(maski)(WDATA[month])
            else:
                WDATA[month]=WDATA[month]+dw.astype(int) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it
                occurence[month]= occurence[month]+np.vectorize(maski)(WDATA[month])

    WET=[]
    WETPERC=[]
    WETNUM=0
    DRY=[]
    DRYPERC=[]
    DRYNUM=0
    for i in WDATA:
        if type(WDATA[i]) == type(np.empty(0)):
            if i in ('06','07','08','09','10','11'):
                if type(WET) != type(np.empty(0)) :
                    WET = WDATA[i]
                else :
                    WET = WET + WDATA[i]
            elif type(DRY) != type(np.empty(0))  :
                DRY = WDATA[i]
            else :
                DRY = DRY + WDATA[i]
        else:
            print("One whole month as no data=> Climatology won't work well")

    for i in occurence:
        if i in ('06','07','08','09','10','11'):
            if i=='06':
                WETNUM=occurence[i]
            else:
                WETNUM=WETNUM+occurence[i]
        else:
            if i=='01':
                DRYNUM=occurence[i]
            else:
                DRYNUM=DRYNUM+occurence[i]
    WETPERC=WET/WETNUM
    DRYPERC=DRY/DRYNUM
    ##======================
    ## Output images to geotiff
    ##======================

    print ('Processing WETMEAN')
    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(OUTPUT_DATA+'WETMEAN_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(WETPERC)
    outdata.FlushCache() ##saves to disk!!
    outdata = None

    print ('Processing DRYMEAN')
    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(OUTPUT_DATA+'DRYMEAN_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(DRYPERC)
    outdata.FlushCache() ##saves to disk!!
    outdata = None
