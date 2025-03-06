#!/usr/bin/env python
# -*- coding: utf-8 -*-
#%%
"""
Created on Tue June 04 11:47:32 2024

@author: Julien Masson
"""

import pandas as pd
import glob
import os
import re
import matplotlib as mp
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
from datetime import date as datet
import seaborn as sbs

sbs.set_theme()
sbs.set_style('ticks')
sbs.set_context('paper')

Opath='/mnt/c/Travail/Script/Script_thesis/0_Data_alrd_prc/Before_after/Before_PEPS_L1C.data'
Npath='/mnt/c/Travail/Script/Script_thesis/0_Data_alrd_prc/Before_after/After_PEPS_L1C.data'
#%% Old Data
dft=pd.read_csv(Opath,index_col=False,header=None)

Listd=[]
Listn=[]
for t in dft[0]:
    Listd.append(re.search(r'\d{8}', t).group())
    Listn.append(re.search(r'\d{2}[A-Z]{3}', t).group())
d = {'Date': Listd,'Tile': Listn}
dft=pd.DataFrame(data=d)
date=pd.to_datetime(dft.iloc[:,0],format='%Y%m%d',yearfirst=True)
data={'Tile':dft.iloc[:,1],'Date':date}
df=pd.DataFrame(data)
OLD=df.set_index('Date')
del (d,data,date,df,dft,Listd,Listn,Opath)
#%% New Data
dft=pd.read_csv(Npath,index_col=False,header=None)
Listd=[]
Listn=[]
for t in dft[0]:
    Listd.append(re.search(r'\d{8}', t).group())
    Listn.append(re.search(r'\d{2}[A-Z]{3}', t).group())
d = {'Date': Listd,'Tile': Listn}
dft=pd.DataFrame(data=d)
date=pd.to_datetime(dft.iloc[:,0],format='%Y%m%d',yearfirst=True)
data={'Tile':dft.iloc[:,1],'Date':date}
df=pd.DataFrame(data)
NEW=df.set_index('Date')
del (d,data,date,df,dft,Listd,Listn,Npath)

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap


OLD_m=OLD.groupby(['Date'])['Tile'].value_counts().unstack().fillna(0).astype(int).reindex()
OLD_m = OLD_m.groupby(pd.Grouper(freq="M"))
OLD_m=OLD_m.sum()

NEW_m=NEW.groupby(['Date'])['Tile'].value_counts().unstack().fillna(0).astype(int).reindex()
NEW_m = NEW_m.groupby(pd.Grouper(freq="M"))
NEW_m=NEW_m.sum()

A=0
for f in [OLD_m,NEW_m]:
    # Plot grid with data
    cmap = colors.ListedColormap(['black','indianred', 'bisque','yellowgreen','lightsteelblue','cornflowerblue','plum'])
    # cmap = mp.colormaps['inferno'].resampled(7)
    bounds = [0,1,2,5,10,15,20]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(60,13))
    cset1=ax.imshow(f.to_numpy().transpose(), cmap=cmap, norm=norm,origin='upper')

    column_names = list(f.columns.values)

    # draw gridlines
    ax.grid(which='minor',axis='y', linestyle='-', color='ghostwhite', linewidth=2)
    ax.grid(which='minor',axis='x', linestyle='-', color='ghostwhite', linewidth=0.5)
    ax.grid(which='major',axis='x', linestyle='-', color='dimgray', linewidth=2)

    ax.tick_params(which='minor', left=False)

    ax.set_yticks(np.arange(0, len(column_names), 1));
    ax.set_yticks(np.arange(-.5, len(column_names), 1), minor=True);

    ax.set_yticklabels(column_names, fontsize=35, ha='right')

    listtick=[]
    nametick=[]
    #f.index.get_indexer([datet(f.index.min().year, 1, 1)], method='nearest')
    if A==0:
        for i in np.arange(f.index.min().year,f.index.max().year):
            listtick.append(f.index.get_loc(f'{i}-12-31'))
            nametick.append(f'{i+1}')
    else:
        for i in np.arange(f.index.min().year,f.index.max().year+1):
            listtick.append(f.index.get_loc(f'{i}-12-31'))
            nametick.append(f'{i+1}')
    ax.set_xticks(listtick,nametick, fontsize=35)
    ax.set_xticks(np.arange(0,f.shape[0], 1), minor=True);

    cb = fig.colorbar(cset1,ax=ax,fraction=0.046, pad=0.04)
    cb.ax.set_yticks(bounds,['0','1','2','5','10','15','20+'])
    cb.ax.tick_params(labelsize=35)
    if A==0:
        name='OLD_DATA'
    else:
        name='NEW_DATA'
    A=A+1

    fig.tight_layout()
    os.chdir('/mnt/c/Travail/Script/Script_thesis/0_Data_alrd_prc/Before_after/Output')
    #plt.show()

    plt.savefig(os.path.join(os.getcwd(),'{}.png'.format(name)),dpi=300,format='png')
    del (ax,fig,cset1)