# -*- coding: utf-8 -*-
WPATH='/mnt/c/Travail/Script/Chl-CONNECT/'   
import pandas as pd
import os
os.chdir(WPATH)
import common.meta as meta
import numpy as np
import glob


MUDATA = os.path.join(WPATH,'MDB_1990_08_28_2023_07_17_modis_l2gen.csv')
MUDF = pd.read_csv(MUDATA)
MUDF = MUDF[~MUDF['Comments'].isin(['Non qualifié'])]
MUDF = MUDF.reset_index()
MSI=[443,490,560,665,705, 740,783]
# Load Rrs
bands = meta.SENSOR_BANDS['MSI']
# bands = [412, 443, 488, 531, 551, 667, 748]
Rrs = {}
Rrs_mc = {}
for band in bands:
    try:
        Rrs_mc[f'{band}'] = matchup_df[f'Rrs{band}_med'].values
    except:
        pass


# Construct input
Rrs_mc_vis_nir = [ Rrs_mc['443'], Rrs_mc['490'], 
                Rrs_mc['560'], Rrs_mc['665'], Rrs_mc['705'], Rrs_mc['740'], Rrs_mc['783']]
Rrs_mc_vis_nir = np.array(Rrs_mc_vis_nir).T

# Perform CONNECT algorithm
from common.Chl_CONNECT import Chl_CONNECT
Chl_NN_mc = Chl_CONNECT(Rrs_mc_vis_nir)

Chl = Chl_NN_mc.Chl_comb
Class = Chl_NN_mc.Class