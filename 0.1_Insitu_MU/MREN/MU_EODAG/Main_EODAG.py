#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 11:55:59 2024

@author: Julien Masson
"""

import os
os.chdir("/work/users/cverpoorter/VolTransMESKONG/Code/Code_S2_PEPS/Match_up/")
import calendar
import sys
import optparse
from EODAG_search import EODAG_search
from create_yaml import create_yaml
import pip
import time
try:
    __import__('eodag')
except ImportError:
    pip.main(['install', 'eodag'])    
from eodag import setup_logging
from eodag.api.core import EODataAccessGateway
import pandas as pd
from datetime import datetime
import pytz
import mgrs

services='geodes'
CREDENTIAL="/work/users/cverpoorter/VolTransMESKONG/Code/Code_S2_PEPS/Match_up/Credential"
OUTPUT="/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/Match_up/"
LOCAL="/work/users/cverpoorter/VolTransMESKONG/Code/Code_S2_PEPS/Match_up/Output/"
DATA = "/work/users/cverpoorter/VolTransMESKONG/Code/Code_S2_PEPS/Match_up/DATA_POC_PON_SPM_light.csv"
# DATA="/mnt/c/Users/Julien/Downloads/DATA_POC_PON_SPM.csv"
Dat = pd.read_csv(DATA)
#Setting download location #################################################
Dat = Dat[Dat['Depth (m)'] <= 5]
Dat = Dat[Dat['BOOL_POC'] != 0]
Dat = Dat.dropna(subset=['Hour (UTC)'])
if LOCAL is None:
    if not os.path.isdir('eodag_workspace'):
        os.mkdir('eodag_workspace')
        os.chdir(os.path.join(os.getcwd(),'eodag_workspace'))
        dpath=os.getcwd()
else :
    localp=OUTPUT

yaml_path=create_yaml(credential=CREDENTIAL,service=services,dpath=localp,totp=None)
#create_yaml(credential=options.credential,service='creodias',dpath=localp,totp=options.totp)
src_path=os.path.join(localp,'Search_results')

if not os.path.exists(src_path):
    os.mkdir(src_path)

def latlon_to_s2_tile(lat, lon):
    m = mgrs.MGRS()
    mgrs_code = m.toMGRS(lat, lon, MGRSPrecision=5)  # MGRS avec précision 5 (caractéristique des tuiles S2)
    
    # Extraire le code de la tuile Sentinel-2
    zone = mgrs_code[:3]   # Zone UTM
    band = mgrs_code[3]    # Bande de latitude
    square = mgrs_code[4:5]  # Identifiant de la tuile
    s2_tile = f"T{zone}{band}{square}"
    
    return s2_tile

###########################################################################
setup_logging(3) #Startup logging
dag = EODataAccessGateway(yaml_path)
dag.set_preferred_provider(services) #What is the provider of datas
df=Dat
df['dateheure'] = pd.to_datetime(df['Date (UTC)'])+pd.to_timedelta(df['Hour (UTC)'])
df['MU']=0
df.reset_index(drop=True, inplace=True)
for p in range(0,len(Dat)-1,1):
    X=df.loc[p, 'Lon']
    Y=df.loc[p, 'Lat']
    Tile=latlon_to_s2_tile(Y, X)
    starts=df.loc[p, 'dateheure']-pd.Timedelta(days=1)
    starts=str(starts.strftime('%Y-%m-%dT%H:%M:%S'))
    ends=df.loc[p, 'dateheure']+pd.Timedelta(days=1)
    ends=str(ends.strftime('%Y-%m-%dT%H:%M:%S'))
    Results=dag.search(download_path=localp,
                                productType="S2_MSI_L1C",
                                tileIdentifier=Tile,
                                yaml_path=yaml_path,
                                start=starts,
                                end=ends,
                                provider=services,
                                count=True)
    Online = Results.filter_property(storageStatus="ONLINE")
    Offline = Results.filter_property(storageStatus="OFFLINE")
    if len(Online)>0 or len(Offline)>0:
        df.at[p, 'MU'] = 1
        print('At least one possible Match-up using Sentinel-2')

        for i in range(0,len(Online),2):
            if i<len(Online):
                dag.download_all(Online[i:i+1],output_dir=OUTPUT)
            else:
                Online[i].download()
        if len(Online)<2:
            dag.download_all(Offline,wait=1,timeout=20,output_dir=OUTPUT)
        else:
            for i in range(0,len(Offline),2):
                if i<len(Offline):
                    dag.download_all(Offline[i:i+1],wait=1,timeout=20,output_dir=OUTPUT)
                else:
                    Offline[i].download(wait=1,timeout=20,output_dir=OUTPUT)
df.to_csv(path_or_buf=LOCAL+'OUTPUT_RESULT.csv')
        ###########################################################################