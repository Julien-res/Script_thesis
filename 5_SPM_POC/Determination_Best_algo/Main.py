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
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from plot_result import plot_results, process_and_plot, process_and_plot_modes
# =====================================================================
# Define the algorithms
def Le18(Rrs490, Rrs555, Rrs670):
    Ci = Rrs555 - (Rrs490 + ((555 - 490) / (555 - 490)) * (Rrs670 - Rrs490))
    return np.where(Ci <= -0.0005, 10**(185.72*Ci + 1.97), 10**(485.19*Ci + 2.1))

def Stramski08(Rrs443, Rrs490, Rrs510, Rrs555, mode='max'):
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

def Hu16(Rrs443, Rrs490, Rrs510, Rrs555, mode='max'):
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


# Load data and SRF
file_path = os.path.join(path, 'Data_RRS_In_Situ.csv')

# Plot the results for Stramski08
process_and_plot(
    data=file_path,
    srf_path=path,
    sensor='MERIS',
    bands=['B3', 'B5', 'B7'],
    func=Le18,
    outlier=1.5,
    logscale=True
)

# Plot the results for Stramski08
process_and_plot_modes(
    data=file_path,
    srf_path=path,
    sensor='SEAWIFS',
    bands=['B2', 'B3', 'B4', 'B5'],
    func=Stramski08,
    modes=['max', 'Rrs443', 'Rrs490', 'Rrs510'],
    title='Stramski08 algorithm for different modes',
    outlier=1.5,
    logscale=True
)

# Plot the results for Hu16
process_and_plot_modes(
    data=file_path,
    srf_path=path,
    sensor='SEAWIFS',
    bands=['B2', 'B3', 'B4', 'B5'],
    func=Hu16,
    modes=['max', 'Rrs443', 'Rrs490', 'Rrs510'],
    title='Hu16 algorithm for different modes',
    outlier=1.5,
    logscale=True
)
