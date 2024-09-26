# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 09:00:04 2024
@author: Julien Masson

Plot figure to show the impact of season, and location on detected water
"""
import os
import sys
import numpy as np
import xarray as xr
import rioxarray
import rasterio
from glob import glob
from pathlib import Path
from osgeo import gdal
import optparse
import scipy.ndimage
###########################################################################
WORKDIR=os.getcwd()
INPUT ='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_WiPE/RAW/'
# INPUT='/mnt/d/DATA/WiPE/WiPE_Data_TEST/DATA/'
OUTPUT='/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/S2_PEPS_WiPE/Figure_OO/OUTPUT/'
# OUTPUT='/mnt/d/DATA/WiPE/WiPE_Data_TEST/OUTPUT/'
os.chdir(OUTPUT)

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

# if options.tile==None:
#         TILENAME = open(os.path.join(WORKDIR,"List_tiles.txt"), "r")
# else:
#         TILENAME=[options.tile]
##================================================================================

for name in TILENAME:
    WDATA={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    WDATAPERC={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    monthdic={'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
    occurence={}
    name=name.rstrip()
    Tile='*'+name+'*water.TIF'
    for path in Path(INPUT).rglob(Tile):
        monthdic[path.name[15:17]].append(str(path))
        print (path.name)

    for a in monthdic :
        t=0
        for i in monthdic[a] :
            print (i)
            ds=gdal.Open(i)
            dw=ds.GetRasterBand(1)
            dw=dw.ReadAsArray()
            # tmp = scipy.ndimage.convolve(dw, np.ones((3,3)), mode='constant')
            # dw = np.logical_and(tmp >= 2, dw)
            # tmp=None
            if type(WDATA[a])!=type(np.empty(0)) :
                WDATA[a]=dw.astype(int) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it
            else:
                WDATA[a]=WDATA[a]+dw.astype(int) #Convert np.uint8 (0 to 255) to np.int64 in order to sum it
                occurence[a]=len(monthdic[a])
        WDATAPERC[a]=(WDATA[a]*100)/occurence[a]

    ##======================
    ## Output images to geotiff
    ##======================
    for i in WDATA :
        print ('Processing '+i+' month')
        if type(WDATA[i])==type(np.empty(0)):
            [rows, cols] = dw.shape
            driver = gdal.GetDriverByName("GTiff")
            outdata = driver.Create('Water_presence_'+i+'_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
            outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
            outdata.SetProjection(ds.GetProjection())##sets same projection as input
            outdata.GetRasterBand(1).WriteArray(WDATA[i])
            outdata.FlushCache() ##saves to disk!!
            outdata = None
    for i in WDATAPERC :
        print ('Processing '+i+' month')
        if type(WDATAPERC[i])==type(np.empty(0)):
            [rows, cols] = dw.shape
            driver = gdal.GetDriverByName("GTiff")
            outdata = driver.Create('Water_presence_Perc_'+i+'_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
            outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
            outdata.SetProjection(ds.GetProjection())##sets same projection as input
            outdata.GetRasterBand(1).WriteArray(WDATA[i])
            outdata.FlushCache() ##saves to disk!!
            outdata = None


    ##================================================================================

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
            WETNUM=WETNUM+occurence[i]
        else:
            DRYNUM=DRYNUM+occurence[i]
    WETPERC=(WET*100)/WETNUM
    DRYPERC=(DRY*100)/DRYNUM
    ##======================
    ## Output images to geotiff
    ##======================

    print ('Processing WET')
    outdata = driver.Create('WET_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(WET)
    outdata.FlushCache() ##saves to disk!!
    outdata = None

    print ('Processing WETPERC')
    outdata = driver.Create('WET_PERC_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(WETPERC)
    outdata.FlushCache() ##saves to disk!!
    outdata = None

    print ('Processing DRY')
    outdata = driver.Create('DRY_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(DRY)
    outdata.FlushCache() ##saves to disk!!
    outdata = None

    print ('Processing DRYPERC')
    outdata = driver.Create('DRY_PERC_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(DRYPERC)
    outdata.FlushCache() ##saves to disk!!
    outdata = None

    SPH=[]
    SPHPERC=[]
    SPHNUM=0
    SPS=[]
    SPSPERC=[]
    SPSNUM=0
    for i in WDATA:
        if type(WDATA[i]) == type(np.empty(0)):
            if i in ('01','02','09','10','11','12'):
                if type(SPH) != type(np.empty(0)) :
                    SPH = WDATA[i]
                else :
                    SPH = SPH + WDATA[i]
            elif type(SPS) != type(np.empty(0))  :
                SPS = WDATA[i]
            else :
                SPS = SPS + WDATA[i]
        else:
            print("One whole month as no data=> Climatology won't work well")

    for i in occurence:
        if i in ('01','02','09','10','11','12'):
            SPHNUM=SPHNUM+occurence[i]
        else:
            SPSNUM=SPSNUM+occurence[i]
    SPHPERC=(SPH*100)/SPHNUM
    SPSPERC=(SPS*100)/SPSNUM
    ##======================
    ## Output images to geotiff
    ##======================

    print ('Processing SPH')
    outdata = driver.Create('SPH_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(SPH)
    outdata.FlushCache() ##saves to disk!!
    outdata = None

    print ('Processing SPHPERC')
    outdata = driver.Create('SPH_PERC_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(SPHPERC)
    outdata.FlushCache() ##saves to disk!!
    outdata = None

    print ('Processing SPS')
    outdata = driver.Create('SPS_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(SPS)
    outdata.FlushCache() ##saves to disk!!
    outdata = None

    print ('Processing SPSPERC')
    outdata = driver.Create('SPS_PERC_'+name+'.tif', cols, rows, 1, gdal.GDT_UInt16) #UInt16
    outdata.SetGeoTransform(ds.GetGeoTransform())##sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())##sets same projection as input
    outdata.GetRasterBand(1).WriteArray(SPSPERC)
    outdata.FlushCache() ##saves to disk!!
    outdata = None
    ds=None
# colorm = cm.get_cmap('cool', 256)
# newcolors = colorm(np.linspace(0, 1, 256))
# newcolors[:1, :] = np.array([0/256, 0/256, 0/256, 1])
# newcmp = ListedColormap(newcolors)
# fig, axs = plt.subplots(figsize=(40, 20))
# im=axs.imshow(WDATA[i],cmap=newcmp)
# axs.tick_params(
#     axis='both',
#     which='both',
#     bottom=True,
#     top=False,
#     labelbottom=True,
#     labelsize=10)
# start, end = axs.get_ylim()
# start=int(start)
# end=int(end)
# axs.set_yticks(np.linspace(start=start,stop=end,num=3))
# axs.set_yticklabels(np.linspace(start=miny,stop=maxy,num=3)
#                     ,minor=False,rotation=30)
# axs.set_xticks(np.linspace(start=start,stop=end,num=3))
# axs.set_xticklabels(np.linspace(start=maxx2,stop=minx,num=3)
#                     ,minor=False,rotation=30)
# fig.colorbar(im,ax=axs,fraction=0.046, pad=0.04)
# plt.tight_layout()
# plt.subplots_adjust(wspace=0.1, hspace=0.1)
# plt.savefig(fname=os.path.join(os.getcwd(),'Water_presence'+i+'.png'),format='png',dpi=1000)