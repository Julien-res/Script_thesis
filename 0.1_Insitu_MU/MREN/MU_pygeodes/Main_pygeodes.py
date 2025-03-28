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
import pip
import time
import pandas as pd
from datetime import datetime
import pytz
import mgrs
CONFIG="/work/users/cverpoorter/VolTransMESKONG/Code/Code_S2_PEPS/Match_up/MU_pygeodes/conf.json"
LOCAL="/work/users/cverpoorter/VolTransMESKONG/Code/Code_S2_PEPS/Match_up/Output/"
DATA = "/work/users/cverpoorter/VolTransMESKONG/Code/Code_S2_PEPS/Match_up/MU_pygeodes/DATA_POC_PON_SPM_light.csv"
from pygeodes import Geodes, Config
conf = Config.from_file(CONFIG)
geodes = Geodes(conf)
from pygeodes.utils.datetime_utils import complete_datetime_from_str
from pygeodes.utils.profile import DownloadQueue, Profile
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
df=Dat
df['dateheure'] = pd.to_datetime(df['Date (UTC)'])+pd.to_timedelta(df['Hour (UTC)'])
df['MU']=0
df.reset_index(drop=True, inplace=True)
for p in range(0,len(Dat)-1,1):
    X=df.loc[p, 'Lon']
    Y=df.loc[p, 'Lat']
    Tile=latlon_to_s2_tile(Y, X)
    starts=df.loc[p, 'dateheure']-pd.Timedelta(days=1)
    starts=str(starts.strftime('%Y-%m-%dT%H:%M'))
    ends=df.loc[p, 'dateheure']+pd.Timedelta(days=1)
    ends=str(ends.strftime('%Y-%m-%dT%H:%M'))
    query = {
    "spaceborne:productType": {"eq": "S2MSI1C"},
    "spaceborne:tile": {"eq": Tile},
    "temporal:startDate": {"lte": complete_datetime_from_str(ends)},
    "temporal:endDate": {"gte": complete_datetime_from_str(starts)},
    }

    items, dataframe = geodes.search_items(query=query)
    for item in items:
        geodes.download_item_archive(item,outfile="my_item.zip")
    ###########################################################################
