# -*- coding: utf-8 -*-

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
import pathlib

mp.style.use('seaborn')
sbs.set_style('ticks')
sbs.set_context('paper')

List_dts=[]

#%% MREN PEPS
path=r'C:\Travail\Script\Listing\List_data\MREN'

all_files =[]

for filename in glob.glob('{}\**/*.csv'.format(path), recursive=True):
    all_files.append(filename)  
    
dfa=pd.DataFrame()
for f in all_files:
    A=f.replace("\\", "/")
    B=re.split('/|\.',A)
    B=B[-2]
    A=A.replace('.csv','')
    dft=pd.read_csv(f,delimiter=';',index_col=False,header=None)
    Listd=[]
    Listn=[]
    for t in dft[0]:
        Listd.append(re.search(r'\d{8}', t).group())
        if re.search(r'Landsat', t)!=None:
            Listn.append(re.search(r'(?<=_)\d{6}(?=_)', t).group())
        else:
            Listn.append(re.search(r'\d{2}[A-Z]{3}', t).group())
    d = {'Date': Listd,'Tile': Listn}
    dft=pd.DataFrame(data=d)
    date=pd.to_datetime(dft.iloc[:,0],format='%Y%m%d',yearfirst=True)
    data={'Tile':dft.iloc[:,1],'Date':date}
    df=pd.DataFrame(data)
    locals()['MREN__'+B]=df.set_index('Date')
    List_dts.append('MREN__'+B)

#%% CALCULCO PEPS

path=r'C:/Travail/Script/Listing/List_data/CALCULCO'

all_files =[]

for filename in glob.glob('{}\**/*.csv'.format(path), recursive=True):
    all_files.append(filename)  
    
dfa=pd.DataFrame()
for f in all_files:
    A=f.replace("\\", "/")
    B=re.split('/|\.',A)
    B=B[-2]
    A=A.replace('.csv','')
    dft=pd.read_csv(f,delimiter=';',index_col=False,header=None)
    Listd=[]
    Listn=[]
    for t in dft[0]:
        Listd.append(re.search(r'\d{8}', t).group())
        if re.search(r'Landsat', t)!=None:
            Listn.append(re.search(r'(?<=_)\d{6}(?=_)', t).group())
        else:
            Listn.append(re.search(r'\d{2}[A-Z]{3}', t).group())
    d = {'Date': Listd,'Tile': Listn}
    dft=pd.DataFrame(data=d)
    date=pd.to_datetime(dft.iloc[:,0],format='%Y%m%d',yearfirst=True)
    data={'Tile':dft.iloc[:,1],'Date':date}
    df=pd.DataFrame(data)
    locals()['CCLO__'+B]=df.set_index('Date')
    List_dts.append('CCLO__'+B)
#%% Sort data and plot
for f in List_dts:
    locals()[f+'_out']=locals()[f].groupby(['Date'])['Tile'].value_counts().unstack().fillna(0).astype(int).reindex()
    locals()[f+'_out'] = locals()[f+'_out'].groupby(pd.Grouper(freq="M"))
    locals()[f+'_out']=locals()[f+'_out'].sum()
    
    # Plot grid with data
    cmap = colors.ListedColormap(['indianred', 'bisque','yellowgreen','cornflowerblue','plum'])
    bounds = [0,1,5,10,15,20]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(60,13))
    cset1=ax.imshow(locals()[f+'_out'].to_numpy().transpose(), cmap=cmap, norm=norm,origin='upper')

    column_names = list(locals()[f+'_out'].columns.values)
    
    # draw gridlines
    ax.grid(which='minor',axis='y', linestyle='-', color='ghostwhite', linewidth=2)
    ax.grid(which='minor',axis='x', linestyle='-', color='ghostwhite', linewidth=0.5)
    ax.grid(which='major',axis='x', linestyle='-', color='dimgray', linewidth=2)
    
    ax.tick_params(which='minor', left=False)

    ax.set_yticks(np.arange(0, len(column_names), 1));
    ax.set_yticks(np.arange(-.5, len(column_names), 1), minor=True);

    ax.set_yticklabels(column_names, fontsize=18, rotation=30, ha='right')

    listtick=[]

    locals()[f+'_out'].index.get_indexer([datet(locals()[f+'_out'].index.min().year, 1, 1)], method='nearest')
    
    # for i in np.arange(locals()[f+'_out'].index.get_indexer([datet(locals()[f+'_out'].index.min().year, 1, 1)], method='nearest'), locals()[f+'_out'].shape[0], 12):
    #     if locals()[f+'_out'].index[i].year!=pd.Timestamp.today().year:
    #         listtick.append(str(locals()[f+'_out'].index[i]+pd.offsets.DateOffset(years=1)).replace(str(locals()[f+'_out'].index[i])[5:], '01-01'))
    #     else :
    #         listtick.append(str(locals()[f+'_out'].index[i]).replace(str(locals()[f+'_out'].index[i])[11:], ''))
    
    for i in np.arange(locals()[f+'_out'].index.get_indexer([datet(locals()[f+'_out'].index.min().year, 1, 1)], method='nearest'), locals()[f+'_out'].shape[0], 12):
        listtick.append(str(locals()[f+'_out'].index[i]).replace(str(locals()[f+'_out'].index[i])[11:], ''))
        
    ax.set_xticks(np.arange(0, locals()[f+'_out'].shape[0], 12),listtick, fontsize=18)
    
    ax.set_xticks(np.arange(0,locals()[f+'_out'].shape[0], 3), minor=True);
    
    cb = fig.colorbar(cset1,ax=ax,fraction=0.046, pad=0.04)
    cb.ax.set_yticks(bounds,['0','1','5','10','15','20+'])
    cb.ax.tick_params(labelsize=20)
    ax.set_title(f.replace('_',' '), fontdict={'fontsize': 20, 'fontweight': 'medium'})
    
    fig.tight_layout()
    os.chdir('C:/Travail/Script/Listing/List_data/IMG/')
    # plt.show()
    plt.savefig(os.path.join(os.getcwd(),'{}.png'.format(f)),dpi=300,format='png')
    
# del(A,B,d,all_files,data,date,df,dft,dfa,Listd,Listn,listtick,i,f,path,t,ax,fig,bounds,cb,cmap,column_names,cset1)
