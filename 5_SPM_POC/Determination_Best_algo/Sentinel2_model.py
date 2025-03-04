%reload_ext autoreload
%autoreload 2
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

def Tran19S2(Rrs490, Rrs510, Rrs555, Rrs665,**kwargs):
    if kwargs.get('sensor', None) != 'S2A' and kwargs.get('sensor', None) != 'S2B':
        raise ValueError("This algorithm is dev for S2A or S2B.")
    def calculate_row(row):
        X = np.log1p(max(row['Rrs665'] / row['Rrs490'] - 1, row['Rrs665'] / row['Rrs510'] - 1, row['Rrs665'] / row['Rrs555'] - 1))
        return 10**(0.928 * X + 2.875)

    data = pd.DataFrame({'Rrs490': Rrs490, 'Rrs510': Rrs510, 'Rrs555': Rrs555, 'Rrs665': Rrs665})
    return data.apply(calculate_row, axis=1)

# =====================================================================
# Define the path to the data file
file_path = os.path.join(path, 'Data_RRS_In_Situ.csv')
process_and_plot(
    data=file_path,
    srf_path=path,
    bands=['B1', 'B2', 'B3', 'B4'],
    func=Tran19S2,
    sensor='S2A',
    outlier=1.5,
    logscale=False
)
process_and_plot(
    data=file_path,
    srf_path=path,
    bands=['B1', 'B2', 'B3', 'B4'],
    func=Tran19S2,
    sensor='S2A',
    outlier=1.5,
    logscale=True
)

def Tran19S2(Rrs490, Rrs510, Rrs555, Rrs665,**kwargs):
    if kwargs.get('sensor', None) != 'S2A' and kwargs.get('sensor', None) != 'S2B':
        raise ValueError("This algorithm is dev for S2A or S2B.")
    def calculate_row(row):
        X = np.log1p(max(row['Rrs665'] / row['Rrs490'] - 1, row['Rrs665'] / row['Rrs510'] - 1, row['Rrs665'] / row['Rrs555'] - 1))
        return 10**(0.928 * X + 2.875)

    data = pd.DataFrame({'Rrs490': Rrs490, 'Rrs510': Rrs510, 'Rrs555': Rrs555, 'Rrs665': Rrs665})
    return data.apply(calculate_row, axis=1)


# =====================================================================
from scipy.optimize import curve_fit



# TUTO
# import numpy as np
# from scipy.optimize import curve_fit

# # Données
# x = np.array([1, 2, 3, 4, 5])
# y = np.array([2.2, 4.1, 6.0, 7.9, 9.8])

# # Définir l'équation avec les coefficients à ajuster
# def my_model(x, a, b):  
#     return a * x + b  

# # Ajustement
# params, _ = curve_fit(my_model, x, y, p0=[1, 1])  # p0 = estimation initiale

# # Résultats
# a_opt, b_opt = params
# print(f"Meilleurs coefficients: a = {a_opt:.3f}, b = {b_opt:.3f}")