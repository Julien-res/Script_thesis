# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 09:45:04 2024
@author: Julien Masson
"""

import os
import re
import rioxarray as rxr
import pandas as pd
import numpy
from osgeo import gdal, ogr
os.chdir('/mnt/c/Travail/Script/Script_thesis/WiPE/Test_WiPE/WiPE_First_Stats')
from retrieve_filename import retrieve_filename
import numpy
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import cm
import matplotlib.ticker as ticker
#=======================
Path_new='/mnt/c/Travail/TEST/Test_WiPE/2017/NEW/'
Path_old='/mnt/c/Travail/TEST/Test_WiPE/2017/OLD/'
#========================
puv_old,pvv_old,puv_new,pvv_new=retrieve_filename(Path_old,Path_new)

a=0
for i in puv_new:
    if a==0:
        ds = gdal.Open(i) # Open image
        data = ds.ReadAsArray()
        data=data.astype('int')
        ys, xs = data.shape
        ulx, xres, _, uly, _, yres = ds.GetGeoTransform()
        extent = [ulx, ulx+xres*xs, uly, uly+yres*ys] # Generate X and Y limits of the image
        ds = None
    else:
        ds = gdal.Open(i)
        data_1 = ds.ReadAsArray()
        data_1=data_1.astype('int')
        ds = None
        data=numpy.add(data,data_1)
        data_1=None

    #Find the old WiPE mask matching the date of the new one
    match=re.findall(r'\d+',i)
    old_o=next((s for s in puv_old if (match[-2]+'T'+match[-1]) in s),None)

    if a==0:
        ds = gdal.Open(old_o)
        data_o = ds.ReadAsArray()
        data_o=data_o.astype('int')
        ds = None
    else:
        ds = gdal.Open(old_o)
        data_o1 = ds.ReadAsArray()
        data_o1=data_o1.astype('int')
        ds = None
        data_o=numpy.add(data_o,data_o1)
        data_o1=None
    a=a+1

extent=list(map(int, extent))
col=range(extent[0], extent[1], int(xres))
idx=range(extent[2], extent[3], int(yres))



#Error : 3*100=44...
# type(data[0,0]) = numpy.uint8? 
# ok c'est ça l'erreur, c'est limité a 255 lol a chier

datap=(data*100)/a
data_op=(data_o*100)/a
difference=numpy.subtract(data,data_o)
#====================================


#Fig OLD DATA (percent)
#==Cmap
Percent=50
jet = cm.get_cmap('jet', Percent-1)
newcolors = jet(numpy.linspace(0, 1, Percent-1))
dark = numpy.array([0/256, 0/256, 0/256, 1])
newcolors[:1, :] = dark
newcmp = ListedColormap(newcolors)

#==FIG

fig, ax = plt.subplots()
heatmap=ax.imshow(data_op,cmap=newcmp,vmin=0,vmax=Percent)
plt.title('Old WiPE data retrieval in percent (2017)')
#==Colorbar
cbar=plt.colorbar(heatmap)
cbar.ax.set_yticks(numpy.linspace(start=0,stop=Percent,num=3))
cbar.set_label('Percent of data retrieval', rotation=270)

#==Ticks (X,Y)
start, end = ax.get_xlim()
start=int(start)
end=int(end)
ax.set_xticks(numpy.linspace(start=start,stop=end,num=3))
ax.set_xticklabels(numpy.linspace(start=extent[0],stop=extent[1],num=3)
                    ,minor=False)

start, end = ax.get_ylim()
start=int(start)
end=int(end)
ax.set_yticks(numpy.linspace(start=start,stop=end,num=3))
ax.set_yticklabels(numpy.linspace(start=extent[3],stop=extent[2],num=3)
                    ,minor=False)

plt.savefig(fname=os.path.join(os.getcwd(),'Old.png'),format='png',dpi=300)

#====================================

Percent=50

jet = cm.get_cmap('jet', Percent-1)
newcolors = jet(numpy.linspace(0, 1, Percent-1))
dark = numpy.array([0/256, 0/256, 0/256, 1])
newcolors[:1, :] = dark
newcmp = ListedColormap(newcolors)

#==FIG

fig, ax = plt.subplots()
heatmap=ax.imshow(datap,cmap=newcmp,vmin=0,vmax=Percent)
plt.title('New WiPE data retrieval in percent (2017)')
#==Colorbar
cbar=plt.colorbar(heatmap)
cbar.ax.set_yticks(numpy.linspace(start=0,stop=Percent,num=3))
cbar.set_label('Percent of data retrieval', rotation=270)

#==Ticks (X,Y)
start, end = ax.get_xlim()
start=int(start)
end=int(end)
ax.set_xticks(numpy.linspace(start=start,stop=end,num=3))

ax.set_xticklabels(numpy.linspace(start=extent[0],stop=extent[1],num=3)
                    ,minor=False)

start, end = ax.get_ylim()
start=int(start)
end=int(end)
ax.set_yticks(numpy.linspace(start=start,stop=end,num=3))
ax.set_yticklabels(numpy.linspace(start=extent[3],stop=extent[2],num=3)
                    ,minor=False)

plt.savefig(fname=os.path.join(os.getcwd(),'New.png'),format='png',dpi=300)

#====================================

Percent=5
YlOrBr=cm.get_cmap('winter', Percent)
GnBu=cm.get_cmap('autumn', Percent)

if Percent<10:
    no=Percent/4
    newcolors = YlOrBr(numpy.linspace(0, no, Percent))
else:
    newcolors = YlOrBr(numpy.linspace(0, 1, Percent))
newcolors=numpy.flip(newcolors,0)
dark = numpy.array([[0/256, 0/256, 0/256, 1]])
newcolors=numpy.append(newcolors,dark,axis=0)
coladd=GnBu(numpy.linspace(0, 1, Percent))
newcolors=numpy.append(newcolors,coladd,axis=0)
newcmp = ListedColormap(newcolors)

#==FIG

fig, ax = plt.subplots()
heatmap=ax.imshow(difference,cmap=newcmp,vmin=-Percent,vmax=Percent)
plt.title('Difference of data retrieval in percent (2017)')
#==Colorbar
cbar=plt.colorbar(heatmap)
cbar.ax.set_yticks([-Percent,0,Percent])
cbar.set_label('Percent of data retrieval', rotation=270)

#==Ticks (X,Y)
start, end = ax.get_xlim()
start=int(start)
end=int(end)
ax.set_xticks(numpy.linspace(start=start,stop=end,num=3))
ax.set_xticklabels(numpy.linspace(start=extent[0],stop=extent[1],num=3)
                    ,minor=False)

start, end = ax.get_ylim()
start=int(start)
end=int(end)
ax.set_yticks(numpy.linspace(start=start,stop=end,num=3))
ax.set_yticklabels(numpy.linspace(start=extent[3],stop=extent[2],num=3)
                    ,minor=False)


plt.savefig(fname=os.path.join(os.getcwd(),'Difference.png'),format='png',dpi=300)