# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 09:45:04 2024

@author: Julien Masson
"""
import os
import re
from datetime import datetime
import rioxarray as rxr
import pandas as pd
import numpy as np
from retrieve_filename import retrieve_filename

#=======================
Path_new='/mnt/c/Travail/TEST/Test_WiPE/2017/NEW/'
Path_old='/mnt/c/Travail/TEST/Test_WiPE/2017/OLD/'
#========================
puv_old,pvv_old,puv_new,pvv_new=retrieve_filename(Path_old,Path_new)



a=0
for i in puv_old:
    match = re.search(r'\d{4}-\d{2}-\d{2}', i)
    match = re.search(r'03*\d{4}', i)
    date = datetime.strptime(match.group(), '%Y-%m-%d').date()
    data = rxr.open_rasterio(i)
    datadf = data[0].to_pandas()
    if a==0:
        pixel_map = pd.DataFrame(data=np.zeros((datadf.shape[0], datadf.shape[0])),columns=datadf.columns.values,index=datadf.index.values)
    
    
    a=a+1
    
df = dataarray[0].to_pandas()
pixel_map = pd.DataFrame(data=np.zeros((df.shape[0], df.shape[0])),columns=df.columns.values,index=df.index.values)
