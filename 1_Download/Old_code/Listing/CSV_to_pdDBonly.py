# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 09:33:56 2023

@author: Julien Masson
"""

import pandas as pd
import glob
import os
import re

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
#%% Sort data
for f in List_dts:
    locals()[f+'_out']=locals()[f].groupby(['Date'])['Tile'].value_counts().unstack().fillna(0).astype(int).reindex()
    locals()[f+'_out'] = locals()[f+'_out'].groupby(pd.Grouper(freq="M"))
    locals()[f+'_out']=locals()[f+'_out'].sum()

del(A,B,d,all_files,data,date,df,dft,dfa,Listd,Listn,f,path,t)
