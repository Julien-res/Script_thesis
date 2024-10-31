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
import os
import sys
os.chdir(WORKDIR)
import common.meta as meta
import numpy as np
from glob import glob
from common.Chl_CONNECT import Chl_CONNECT
from osgeo import gdal
import optparse
from pathlib import Path
import rasterio
from rasterio.enums import Resampling
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
OUTPUT='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_OWTM/'
convert=['Rw443','Rw490','Rw560','Rw665','Rw705']
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

for name in TILENAME: # For all listed TILENAME
    name=name.rstrip()
    for year in range(2015,2025):
        monthdic={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
        monthdicW={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
        occurence={}
        TILE='*'+name+'*_'+str(year)+'*_polymer20m.nc'
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
        for month in monthdic : #For all month
            WDATA={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
            t=0
            print('number of elem to treat this month : '+str(len(monthdic[month])))
            print(monthdic[month])
            i=None
            for pathdt in monthdic[month] : # For all images in those month
                print (pathdt)
                if not os.path.exists(OUTPUT+os.path.basename(pathdt)+'.tif'):
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
                        print('Watermask Opened : '+monthdicW[month][t])
                    # Mask ==================
                    dww=np.squeeze(dww) #Convert np.uint8 (0 to 255) to np.int64 and remove dim 1
                    dww=dww.astype(bool) #Convert to mask True or False to apply
                    # bitmask = np.vectorize(bitmaskp)(np.flip(bitmask,axis=0)) #Convert bitmask to True or False, and flip it to correspond WiPE projection
                    bitmask = np.vectorize(bitmaskp)(bitmask)
                    bitmask = np.where(dww,bitmask,False) #Fusion bitmask and WiPE to save compute time
                    if t==0:
                        occurence[month]=bitmask.astype(int)
                    else:
                        occurence[month]= occurence[month] + bitmask.astype(int)
                    dww=None
                    CONTROLE=0
                    if np.isnan(np.vectorize(testnan)(bitmask)).all():
                        print('Empty bitmask, no data')
                    else:
                        tmp=[]
                        for b in range(0,len(DATA)):
                            DATA[b] = np.where(bitmask,DATA[b],0) #apply bitmask
                            if not np.isnan(np.where(bitmask,DATA[b],np.nan)).all(): #test doesn't work? => no nan but 0, test if all 0
                                print('OK, bands not empty')
                                tmp.append(np.vectorize(polymernan)(DATA[b]))
                                if np.isnan(tmp[b]).all():
                                    print('DATA NOT EMPTY BUT TMP EMPTY, ERROR')
                                    sys.exit(-1)
                                print(tmp[b])
                            else:
                                print('DATA '+str(b)+' all nan!')
                                CONTROLE=1
                        print('Output '+os.path.basename(pathdt))
                        if CONTROLE==0:
                            if t == 0:
                                WDATA[month] = tmp
                            else:
                                WDATA[month] = list( map(add, WDATA[month], tmp))
                        else:
                            print('Not printing data, as DATA is all nan')
                        CONTROLE=0
                else:
                    '======Image already exist in file======'
                t += 1
            print (t)
            print(str(t) + ' treated out of '+ str(len(monthdic[month])))
            tmp=[]
            CONTROLE=0
            for b in range(0,len(WDATA[month])):
                tmpp=WDATA[month][b]/occurence[month]
                tmp.append(np.vectorize(polymernan)(tmpp))
            try :
                OUT = Chl_CONNECT(tmp,method='logreg',sensor='MSI',logRrsClassif=False,pTransform=False).Class
            except:
                print("Can't process the code properly. Possible error with multiple images the same day or empty month. ")
                CONTROLE=2
            if CONTROLE==0:
                print('Output '+name+month+str(year)+'.tif')
                driver = gdal.GetDriverByName("GTiff")
                outdata = driver.Create(OUTPUT+name+'_'+month+str(year)+'.tif', 5490, 5490, 1, gdal.GDT_UInt16) #UInt16
                dwt=gdal.Open(monthdicW[month][0], gdal.GA_ReadOnly)
                geot=dwt.GetGeoTransform()
                geot=(geot[0],geot[1]*2,geot[2],geot[3],geot[4],geot[5]*2)
                outdata.SetGeoTransform(geot)##sets same geotransform as input
                outdata.SetProjection(dwt.GetProjection())##sets same projection as input
                outdata.GetRasterBand(1).WriteArray(OUT)
                outdata.FlushCache() ##saves to disk!!
                outdata = None