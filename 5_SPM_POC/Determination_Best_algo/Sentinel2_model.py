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
from plot_result import process_and_plot

# def Tran19S2510(Rrs490, Rrs510, Rrs555, Rrs665,**kwargs):
#     if kwargs.get('sensor', None) != 'S2A' and kwargs.get('sensor', None) != 'S2B':
#         raise ValueError("This algorithm is dev for S2A or S2B.")
#     def calculate_row(row):
#         X = np.log1p(max(row['Rrs665'] / row['Rrs490'] - 1, row['Rrs665'] / row['Rrs510'] - 1, row['Rrs665'] / row['Rrs555'] - 1))
#         return 10**(0.928 * X + 2.875)

#     data = pd.DataFrame({'Rrs490': Rrs490, 'Rrs510': Rrs510, 'Rrs555': Rrs555, 'Rrs665': Rrs665})
#     return data.apply(calculate_row, axis=1)

def Tran19S2(Rrs490, Rrs555, Rrs665,**kwargs):
    if kwargs.get('sensor', None) != 'S2A' and kwargs.get('sensor', None) != 'S2B':
        raise ValueError("This algorithm is dev for S2A or S2B.")
    def calculate_row(row):
        X = np.log1p(max(row['Rrs665'] / row['Rrs490'] - 1, row['Rrs665'] / row['Rrs555'] - 1))
        return 10**(0.928 * X + 2.875)

    data = pd.DataFrame({'Rrs490': Rrs490, 'Rrs555': Rrs555, 'Rrs665': Rrs665})
    return data.apply(calculate_row, axis=1)

# =====================================================================
# Define the path to the data file
pathmeta='/mnt/c/Travail/Script/Chl-CONNECT/'
file_path = os.path.join(path, 'Data_RRS_In_Situ.csv')
# for logscale in [False, True]:
    # process_and_plot(
    #     data=file_path,
    #     srf_path=path,
    #     bands=['B2', 'B2', 'B3', 'B4'],
    #     func=Tran19S2510,
    #     sensor='S2A',
    #     outlier=1.5,
    #     logscale=logscale,
    #     pathmeta=pathmeta
    # )


# ====================================================================

from scipy.optimize import curve_fit, minimize

def Tran19S2Opti(Rrs490, Rrs555, Rrs665, **kwargs):
    if kwargs.get('sensor', None) != 'S2A' and kwargs.get('sensor', None) != 'S2B':
        raise ValueError("This algorithm is dev for S2A or S2B.")
    
    def model(X, a, b):
        return 10**(a * X + b)
    
    def calculate_row(row, a, b):
        X = np.log1p(max(row['Rrs665'] / row['Rrs490'] - 1, row['Rrs665'] / row['Rrs555'] - 1))
        return model(X, a, b)
    
    data = pd.DataFrame({'Rrs490': Rrs490, 'Rrs555': Rrs555, 'Rrs665': Rrs665})
    
    # Flatten the data for curve fitting
    X_data = np.log1p(np.maximum(data['Rrs665'] / data['Rrs490'] - 1, data['Rrs665'] / data['Rrs555'] - 1))
    y_data = 10**(0.928 * X_data + 2.875)  # Initial guess based on original coefficients
    
    # Fit the model to find the best coefficients
    # Remove NaN values from X_data and y_data
    mask = ~np.isnan(X_data) & ~np.isnan(y_data)
    X_data_clean = X_data[mask]
    y_data_clean = y_data[mask]

    popt, _ = curve_fit(model, X_data_clean, y_data_clean, p0=[0.928, 2.875])
    
    # Print the optimized coefficients
    print(f"Meilleurs coefficients: a = {popt[0]:.3f}, b = {popt[1]:.3f}")
    
    # Apply the optimized coefficients
    return data.apply(lambda row: calculate_row(row, *popt), axis=1)


def Tran19S2Opti_2(Rrs490, Rrs555, Rrs665, **kwargs):
    if kwargs.get('sensor', None) != 'S2A' and kwargs.get('sensor', None) != 'S2B':
        raise ValueError("This algorithm is dev for S2A or S2B.")
    
    def calculate_row(row, a, b):
        X = np.log1p(max(row['Rrs665'] / row['Rrs490'] - 1, row['Rrs665'] / row['Rrs555'] - 1))
        return 10**(a * X + b)
    
    data = pd.DataFrame({'Rrs490': Rrs490, 'Rrs555': Rrs555, 'Rrs665': Rrs665})
    
    # Prepare the data for optimization
    X_data = np.log1p(np.maximum(data['Rrs665'] / data['Rrs490'] - 1, data['Rrs665'] / data['Rrs555'] - 1)).values
    y_data = 10**(0.928 * X_data + 2.875)  # Initial guess based on original coefficients
    
    # Remove NaN values from X_data and y_data
    mask = ~np.isnan(X_data) & ~np.isnan(y_data)
    X_data_clean = X_data[mask]
    y_data_clean = y_data[mask]
    
    # Define the objective function to minimize
    def objective(params):
        a, b = params
        y_pred = 10**(a * X_data_clean + b)
        return np.sum((y_pred - y_data_clean)**2)
    
    # Initial guess for the coefficients
    initial_guess = [0.928, 2.875]
    # Perform the optimization
    result = minimize(objective, initial_guess, method='Nelder-Mead')
    a_opt, b_opt = result.x
    
    # Print the optimized coefficients
    print(f"Meilleurs coefficients: a = {a_opt:.3f}, b = {b_opt:.3f}")
    
    # Apply the optimized coefficients
    return data.apply(lambda row: calculate_row(row, a_opt, b_opt), axis=1)

for outlier in [1.5, None]:
    for logscale in [False, True]:
        process_and_plot(
            data=file_path,
            srf_path=path,
            bands=['B2', 'B3', 'B4'],
            func=Tran19S2,
            sensor='S2A',
            outlier=outlier,
            logscale=logscale,
            pathmeta=pathmeta,
            save_result=f'Tran19S2{str(logscale)}_out_{outlier}.png'
        )

        process_and_plot(
            data=file_path,
            srf_path=path,
            bands=['B2', 'B3', 'B4'],
            func=Tran19S2Opti,
            sensor='S2A',
            outlier=outlier,
            logscale=logscale,
            pathmeta=pathmeta,
            save_result=f'Tran19OptiS2{str(logscale)}_out_{outlier}.png'
        )
        
        process_and_plot(
            data=file_path,
            srf_path=path,
            bands=['B2', 'B3', 'B4'],
            func=Tran19S2Opti_2,
            sensor='S2A',
            outlier=outlier,
            logscale=logscale,
            pathmeta=pathmeta,
            save_result=f'Tran19Opti2S2{str(logscale)}_out_{outlier}.png'
        )

