#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 11:55:59 2024

@author: Julien Masson
"""

import os
os.chdir("/mnt/c/Travail/Script/Script_thesis/0.1_Insitu_MU/")
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

services='geodes'
CREDENTIAL="/mnt/c/Travail/Script/Script_thesis/1_Download/EODAG/Credential"
OUTPUT="/mnt/d/DATA/S2A_L1C/MATCH-UP"
LOCAL="/mnt/c/Travail/Script/Script_thesis/0.1_Insitu_MU/Output"
DATA = "/mnt/c/Travail/DATA_AGGREGATION/DATA_POC_PON_SPM.xlsx"
# DATA="/mnt/c/Users/Julien/Downloads/DATA_POC_PON_SPM.xlsx"
Dat = pd.read_excel(DATA)
#Setting download location #################################################
Dat = Dat[Dat['Depth (m)'] <= 5]
Dat = Dat[Dat['BOOL_POC'] != 0]

if LOCAL is None:
    if not os.path.isdir('eodag_workspace'):
        os.mkdir('eodag_workspace')
        os.chdir(os.path.join(os.getcwd(),'eodag_workspace'))
        dpath=os.getcwd()
else :
    localp=LOCAL

yaml_path=create_yaml(credential=CREDENTIAL,service=services,dpath=localp,totp=None)
#create_yaml(credential=options.credential,service='creodias',dpath=localp,totp=options.totp)
src_path=os.path.join(localp,'Search_results')

if not os.path.exists(src_path):
    os.mkdir(src_path)
###########################################################################
setup_logging(2) #Startup logging
dag = EODataAccessGateway(yaml_path)
dag.set_preferred_provider(services) #What is the provider of datas
Dat['MU']=0
for p in range(0,len(Dat)-1,1):
    X=Dat.loc[p, 'Lon']
    Y=Dat.loc[p, 'Lat']
    starts=Dat.loc[p, 'Date']-pd.Timedelta(days=1)
    ends=Dat.loc[p, 'Date']+pd.Timedelta(days=1)
    Online,Offline=EODAG_search(download_path=localp,
                                productTypes='S2_MSI_L1C',
                                geom=f'POINT ({X} {Y})',
                                yaml_path=yaml_path,starts=str(starts),ends=str(ends))
    if len(Online)>0 or len(Offline)>0:
        df.at[p, 'MU'] = 1
        print('At least one possible Match-up using Sentinel-2')

        for i in range(0,len(online_search_results),2):
            if i<len(Online):
                dag.download_all(Online[i:i+1])
            else:
                Online[i].download()
        if len(Offline)<2:
            dag.download_all(Offline,wait=1,timeout=20)
        else:
            for i in range(0,len(Offline),2):
                if i<len(products):
                    dag.download_all(Offline[i:i+1],wait=1,timeout=20)
                else:
                    Offline[i].download(wait=1,timeout=20)
        ###########################################################################