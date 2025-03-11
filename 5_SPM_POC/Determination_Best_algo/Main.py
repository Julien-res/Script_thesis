import os
import sys
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
# path = '/mnt/c/Users/Julien/Documents/GitHub/Script_thesis/5_SPM_POC/Determination_Best_algo'
path='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo'
sys.path.append(path)
os.chdir(path)
pathmeta='/mnt/c/Travail/Script/Chl-CONNECT'
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from plot_result import process_and_plot
from load_datas import load_data, load_srf_data, simulate_band
from taylor_diagram import taylor_diagram
# =====================================================================
# Define the algorithms

# def Le17(Rrs490, Rrs510, Rrs555, Rrs665, **kwargs):
#     return(1000*np.exp(709.291*Rrs490-797.831*Rrs510+101.013*Rrs555+53.661*Rrs665-0.520))

def Le18BG(*args, **kwargs):
    sensor = kwargs.get('sensor', None)
    if sensor =='MERIS':
        Rrs443=args[0]
        Rrs490=args[1]
        Rrs560=args[2]
        Rrs665=args[3]
        Ci = Rrs560 - (Rrs490 + ((560 - 490) / (665 - 490)) * (Rrs665 - Rrs490))
        Ratio= Rrs443/Rrs560
        return np.where(Ci <= -0.0005, 10**(-0.68*Ratio+1.13), 10**(-1*Ratio + 0.94))
    elif sensor =='MODIS':
        Rrs443=args[0]
        Rrs490=args[0]
        Rrs555=args[1]
        Rrs670=args[2]
        Ci = Rrs555 - (Rrs490 + ((555 - 490) / (670 - 490)) * (Rrs670 - Rrs490))
        Ratio= Rrs443/Rrs560
        return np.where(Ci < -0.0005, 10**(-0.29*Ci + 0.82), 10**(-4.39*Ci + 0.83))
    elif sensor =='SEAWIFS':
        Rrs490=args[0]
        Rrs555=args[1]
        Rrs670=args[2]
        Ci = Rrs555 - (Rrs490 + ((555 - 490) / (670 - 490)) * (Rrs670 - Rrs490))
        return np.where(Ci < -0.0005, 10**(-0.76*Ci + 0.97), 10**(-1.11*Ci + 1.07))
    else:
        raise ValueError("Invalid sensor. Choose from 'MERIS', 'MODIS', or 'SEAWIFS'.")

# NEED TO CODE SAME BUT WITH CI
        # Ci = Rrs555 - (Rrs490 + ((555 - 490) / (670 - 490)) * (Rrs670 - Rrs490))
        # return np.where(Ci < -0.0005, 10**(185.72*Ci + 1.97), 10**(485.19*Ci + 2.1))

def Le18CI(*args, **kwargs):
    sensor = kwargs.get('sensor', None)
    if sensor =='MERIS':
        Rrs490=args[0]
        Rrs555=args[1]
        Rrs670=args[2]
        Ci = Rrs555 - (Rrs490 + ((555 - 490) / (670 - 490)) * (Rrs670 - Rrs490))
        return np.where(Ci < -0.0005, 10**(185.72*Ci + 1.97), 10**(485.19*Ci + 2.1))

def Stramski08(Rrs443, Rrs490, Rrs510, Rrs555, **kwargs):
    mode=kwargs.get('mode','max')
    if kwargs.get('sensor', None) != 'SEAWIFS':
        raise ValueError("Stramski08 algorithm is only available for SEAWIFS sensor.")
    # SeaWiFS
    if Rrs555 is None:
        raise ValueError("Rrs555 cannot be None")
    def calculate_row(row):
        band_values = {'Rrs443': row['Rrs443'], 'Rrs490': row['Rrs490'], 'Rrs510': row['Rrs510']}
        if mode == 'max':
            band = max((value for value in band_values.values() if value is not None), default=None)
            if band is None:
                raise ValueError("At least one of Rrs443, Rrs490, or Rrs510 must be provided")
            if band == row['Rrs443']:
                return 203.2 * (row['Rrs443'] / row['Rrs555']) ** (-1.034)
            elif band == row['Rrs490']:
                return 308.3 * (row['Rrs490'] / row['Rrs555']) ** (-1.639)
            elif band == row['Rrs510']:
                return 423.0 * (row['Rrs510'] / row['Rrs555']) ** (-3.075)
        elif mode == 'Rrs443':
            return 203.2 * (row['Rrs443'] / row['Rrs555']) ** (-1.034)
        elif mode == 'Rrs490':
            return 308.3 * (row['Rrs490'] / row['Rrs555']) ** (-1.639)
        elif mode == 'Rrs510':
            return 423.0 * (row['Rrs510'] / row['Rrs555']) ** (-3.075)
        else:
            raise ValueError("Invalid mode. Choose from 'max', 'Rrs443', 'Rrs490', or 'Rrs510'.")

    data = pd.DataFrame({'Rrs443': Rrs443, 'Rrs490': Rrs490, 'Rrs510': Rrs510, 'Rrs555': Rrs555})
    return data.apply(calculate_row, axis=1)

def Hu16(Rrs443, Rrs490, Rrs510, Rrs555, **kwargs):
    mode=kwargs.get('mode','max')
    if kwargs.get('sensor', None) != 'SEAWIFS':
        raise ValueError("Hu16 algorithm is only available for MERIS sensor.")
    if Rrs555 is None:
        raise ValueError("Rrs555 cannot be None")
    
    def calculate_row(row):
        band_values = {'Rrs443': row['Rrs443'], 'Rrs490': row['Rrs490'], 'Rrs510': row['Rrs510']}
        if mode == 'max':
            band = max((value for value in band_values.values() if value is not None), default=None)
            if band is None:
                raise ValueError("At least one of Rrs443, Rrs490, or Rrs510 must be provided")
            return 360.1333 * (band / row['Rrs555']) ** (-1.1790)
        elif mode == 'Rrs443':
            return 262.1730 * (row['Rrs443'] / row['Rrs555']) ** (-0.940)
        elif mode == 'Rrs490':
            return 285.0929 * (row['Rrs490'] / row['Rrs555']) ** (-1.2292)
        elif mode == 'Rrs510':
            return 243.8148 * (row['Rrs510'] / row['Rrs555']) ** (-2.4777)
        else:
            raise ValueError("Invalid mode. Choose from 'max', 'Rrs443', 'Rrs490', or 'Rrs510'.")
    data = pd.DataFrame({'Rrs443': Rrs443, 'Rrs490': Rrs490, 'Rrs510': Rrs510, 'Rrs555': Rrs555})
    return data.apply(calculate_row, axis=1)


def Tran19(Rrs490, Rrs510, Rrs555, Rrs665,**kwargs):
    if kwargs.get('sensor', None) != 'MERIS':
        raise ValueError("Tran19 algorithm is only available for MERIS sensor.")
    def calculate_row(row):
        X = np.log1p(max(row['Rrs665'] / row['Rrs490'] - 1, row['Rrs665'] / row['Rrs510'] - 1, row['Rrs665'] / row['Rrs555'] - 1))
        return 10**(0.928 * X + 2.875) #10**(0.928 * X + 2.875)

    data = pd.DataFrame({'Rrs490': Rrs490, 'Rrs510': Rrs510, 'Rrs555': Rrs555, 'Rrs665': Rrs665})
    return data.apply(calculate_row, axis=1)

def Masson (B1,B2,B3,B4,B5,B6,B7,**kwargs):
    if kwargs.get('sensor', None) != 'S2A' and kwargs.get('sensor', None) != 'S2B':
        raise ValueError("Masson algorithm is only available for S2A or S2B (MSI) sensor.")
    POC = 616.948 + (-158199.279 * B1) + (26243.212 * B2) + (49729.572 * B3) + (-90867.531 * B4) + (89122.649 * B5) + (271187.117 * B6) + (-165030.846 * B7)
    return POC
# def Manh23(Rrs490, Rrs510, Rrs555, Rrs665,**kwargs):
#     if kwargs.get('sensor', None) != 'MERIS':
#         raise ValueError("Manh23 algorithm is only available for MERIS sensor.")
#     def Tran(row):
#         X = np.log1p(max(row['Rrs665'] / row['Rrs490'] - 1, row['Rrs665'] / row['Rrs555'] - 1))
#         return 10**(0.928 * X + 2.875)
#     def Le17(row):
#         return(np.exp(-115.69*row['Rrs490']-53.64*row['Rrs510']+172.13*row['Rrs555']-40.06*row['Rrs665']-0.54))
#     data = pd.DataFrame({'Rrs490': Rrs490, 'Rrs510': Rrs510, 'Rrs555': Rrs555, 'Rrs665': Rrs665})
#     A= data.apply(Tran, axis=1)
#     B= data.apply(Le17, axis=1)
#     #==================Chl-CONNECT==================
#     sys.path.append(kwargs.get('pathmeta', None))
#     from Dict import SENSOR_BANDS
#     from common.Chl_CONNECT import Chl_CONNECT
#     if kwargs.get('sensor', None) == 'MERIS' or kwargs.get('sensor', None) == 'SEAWIFS':
#         senso = 'MODIS'
#     elif kwargs.get('sensor', None) == 'S2A' or kwargs.get('sensor', None) == 'S2B':
#         senso='MSI'
#     else:
#         senso = kwargs.get('sensor', None)
#     # senso='MSI'

#     datar = load_data(kwargs.get('datatot', None))
#     srf_data = load_srf_data(kwargs.get('srf_patht',None), kwargs.get('sensor', None))
#     band_class = {band: simulate_band(datar, srf_data[band]['Values'],
#                                         int(srf_data[band]['Wavelengths'][0]), 
#                                         int(srf_data[band]['Wavelengths'].values[-1])) for band in SENSOR_BANDS[senso]}
#     Rrs_class = np.array(list(band_class.values())).T
#     classif = Chl_CONNECT(Rrs_class,method='logreg', sensor=senso,logRrsClassif=False,pTransform=False).Class
#     p1 = 
#     p2 = 
#     p3 = 
#     return A*(p1+p2)+B*p3


# ======================== Load data and SRF
file_path = os.path.join(path, 'Data_RRS_In_Situ.csv')
pathmeta='/mnt/c/Travail/Script/Chl-CONNECT/'
# Define the parameters for each algorithm
algorithms = [
    {
        'func': Tran19,
        'sensor': 'MERIS',
        'bands': ['B3', 'B4', 'B5', 'B7'],
        'save_result': 'Tran19.png'
    },
    {
        'func': Le18BG,
        'sensor': 'MERIS',
        'bands': ['B2', 'B3', 'B5', 'B7'],
        'save_result': 'Le18BG.png'
    },
    {
        'func': Le18CI,
        'sensor': 'MERIS',
        'bands': ['B3', 'B5', 'B7'],
        'save_result': 'Le18CI.png'
    },
    {
        'func': Stramski08,
        'sensor': 'SEAWIFS',
        'bands': ['B2', 'B3', 'B4', 'B5'],
        'modes': ['max', 'Rrs443', 'Rrs490', 'Rrs510'],
        'title': 'Stramski08 algorithm for different modes',
        'save_result': 'Stramski08.png'
    },
    {
        'func': Hu16,
        'sensor': 'SEAWIFS',
        'bands': ['B2', 'B3', 'B4', 'B5'],
        'modes': ['max', 'Rrs443', 'Rrs490', 'Rrs510'],
        'title': 'Hu16 algorithm for different modes',
        'save_result': 'Hu16.png'
    },
    {
        'func': Masson,
        'sensor': 'S2A',
        'bands': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
        'title': 'Masson algorithm using S2A',
        'save_result': 'Masson.png'
    }
]

test=algorithms[-1]
process_and_plot(
    data=file_path,
    srf_path=path,
    bands=test['bands'],
    func=test['func'],
    sensor=test['sensor'],
    pathmeta=pathmeta,
    outlier=1.5,
    logscale=True)

process_and_plot(
    data=file_path,
    srf_path=path,
    bands=test['bands'],
    func=test['func'],
    sensor=test['sensor'],
    pathmeta=pathmeta,
    outlier=1.5,
    logscale=False)

# # Loop through each algorithm and plot results for both logscale True and False

# if __name__ == '__main__':
#     for algo in algorithms:
#         for outlier in [1.5, None]:
#             for logscale in [True, False]:
#                 process_and_plot(
#                     data=file_path,
#                     srf_path=path,
#                     bands=algo['bands'],
#                     func=algo['func'],
#                     sensor=algo['sensor'],
#                     outlier=outlier,
#                     logscale=logscale,
#                     pathmeta=pathmeta,
#                     save_result=algo['save_result'].replace('.png', f'_logscale_{str(logscale)}_out_{str(outlier)}.png'),
#                     **{k: v for k, v in algo.items() if k not in ['func', 'sensor', 'bands', 'save_result']},

#                 )

