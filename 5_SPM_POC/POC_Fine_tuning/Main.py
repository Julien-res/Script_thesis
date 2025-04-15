#%%
%reload_ext autoreload
%autoreload 2
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score , mean_absolute_error, mean_squared_log_error
import seaborn as sns
path='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/POC_Fine_tuning'
sys.path.append(path)
os.chdir(path)
from load_datas import load_data, load_srf_data, simulate_band
sys.path.append('/mnt/c/Travail/Script/Chl-CONNECT')
# from Dict import SENSOR_BANDS
# from common.Chl_CONNECT import Chl_CONNECT
from common.classification_functions import classif5

# Load data
file_path = os.path.join(path, 'DATA_POC_ONLY.csv')
data = load_data(file_path)

# Remove duplicates based on coordinates and time
datam = data.drop_duplicates(subset=['ID'], keep='first')

datar = datam[datam['BOOL_RRS_ALL'] == 1]

dataMU = datam[datam['BOOL_RRS_ALL'] == 0]
rrs_columns = [col for col in datar.columns if col.startswith("Rrs")]

# Rename Rrs columns to only include the wavelength number
renamed_columns = {col: col[3:] for col in rrs_columns}
datar.rename(columns=renamed_columns, inplace=True)
# Clip values to be within the range [0, 0.08] without removing rows
datar[list(renamed_columns.values())] = datar[list(renamed_columns.values())].clip(lower=0, upper=0.08)

# Remove rows with non-continuous Rrs values between 400 and 900 nm
rrs_wavelengths = [int(col) for col in renamed_columns.values() if col.isdigit()]
continuous_rrs_columns = [col for col in renamed_columns.values() if 400 <= int(col) <= 900]

def has_large_gap(row, threshold=10):
    # Check for gaps larger than the threshold in non-NaN values
    non_nan_indices = np.where(~row.isna())[0]
    if len(non_nan_indices) == 0:
        return True  # Entire row is NaN
    gaps = np.diff(non_nan_indices)
    return any(gaps > threshold)

datar = datar[~datar[continuous_rrs_columns].apply(has_large_gap, axis=1)]
srf_data = load_srf_data(path, 'S2A')

# band_class = {band: simulate_band(datar, srf_data[band]['Values'],
#                                     int(srf_data[band]['Wavelengths'][0]), 
#                                     int(srf_data[band]['Wavelengths'].values[-1])) for band in SENSOR_BANDS['MSI']}

# Rrs_class = np.array(list(band_class.values())).T
# classif = Chl_CONNECT(Rrs_class, method='logreg', sensor='MSI', logRrsClassif=False, pTransform=False).Class
band_class = {band: simulate_band(datar, srf_data[band]['Values'],
                                    int(srf_data[band]['Wavelengths'][0]), 
                                    int(srf_data[band]['Wavelengths'].values[-1])) for band in ['B1', 'B2', 'B3', 'B4']}

Rrs_class = np.array(list(band_class.values())).T
classif, proba = classif5(Rrs_class, method='logreg', sensor='MSI', logRrs=False)
classif = classif[classif != 0]

if isinstance(classif, np.ndarray) and classif.ndim > 1:
    classif = classif[:, 0]  # Keep only the first column for numpy array
datar['Class'] = classif

# Drop the second column of the third dimension from `proba`
proba = np.array(proba)[:, :, 0]

# Assign probabilities to the datar DataFrame
datar = datar.copy() # Create a copy of the DataFrame to avoid SettingWithCopyWarning and PerformanceWarning
for i in range(proba.shape[0]):
    datar[f'Prob{i+1}'] = proba[i]
datar = datar.copy() # Create a copy of the DataFrame to avoid SettingWithCopyWarning and PerformanceWarning
# Remove rows where 'Class' is in [1, 2]
datar = datar[~datar['Class'].isin([1])]

datarLOWPOC = datar[datar['POC_µg_L'] < 1000]
datarHIGHPOC = datar[datar['POC_µg_L'] >= 1000]
datarTran= datar[datar['POC_µg_L'] > 100]
#%% ======================== Map data ========================
from map_poc import plot_world_map
for i in [None, 'europe', 'usa', 'guyane', 'mekongA', 'mekongB']:
    fig, ax = plot_world_map(datar, 'Lat', 'Lon', 'POC_µg_L', 'POC with in-situ Rrs', region=i)
    output_path = os.path.join(path, 'output','Map','W_Rrs', f'POC_WRrs_{i if i else "global"}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    fig, ax = plot_world_map(dataMU, 'Lat', 'Lon', 'POC_µg_L', 'POC without in-situ Rrs', region=i)
    output_path = os.path.join(path, 'output','Map','Wo_Rrs', f'POC_WoRrs_{i if i else "global"}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

#%% ======================== Spectral shape and data cleaning ========================
from spectral_shape import plot_rrs_spectra_interactive,plot_rrs_spectra,plot_rrs_spectra_class
fig = plot_rrs_spectra(datar, 'POC_µg_L')
output_path = os.path.join(path, 'output','Spectra', 'POC_rrs_spectra.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)

fig = plot_rrs_spectra_class(datar, 'Class')
output_path = os.path.join(path, 'output','Spectra', 'Class_rrs_spectra.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
fig = plot_rrs_spectra(datarLOWPOC, 'POC_µg_L')
output_path = os.path.join(path, 'output','Spectra', 'POC_rrs_spectra_LOW_POC.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
fig = plot_rrs_spectra(datarHIGHPOC, 'POC_µg_L')
output_path = os.path.join(path, 'output','Spectra', 'POC_rrs_spectra_HIGHPOC.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
fig = plot_rrs_spectra(datarTran, 'POC_µg_L')
output_path = os.path.join(path, 'output','Spectra', 'POC_rrs_spectra_Wo100POC.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
# Plot Rrs spectra for each class
unique_classes = datar['Class'].unique()
for class_label in unique_classes:
    datar_class = datar[datar['Class'] == class_label]
    fig = plot_rrs_spectra(datar_class, 'POC_µg_L')
    output_path = os.path.join(path, 'output', 'Spectra', f'POC_rrs_spectra_Class_{class_label}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

# plot_rrs_spectra_interactive(datar, 'POC_µg_L')
#%% ======================== Frequency plot ========================
from frequency_plot import plot_frequency_distribution_with_coloring, plot_frequency_distribution
fig = plot_frequency_distribution_with_coloring(datar, 'POC_µg_L', 'Class')
output_path = os.path.join(path, 'output', 'POC_frequency_distribution_colored.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
fig = plot_frequency_distribution(datar, 'POC_µg_L')
output_path = os.path.join(path, 'output', 'POC_frequency_distribution.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
fig = plot_frequency_distribution_with_coloring(datarTran, 'POC_µg_L', 'Class')
output_path = os.path.join(path, 'output', 'POC_frequency_distribution_colored_Tran.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)

#%% ======================== Hyperspectral matrix correlation ========================
from hyperspec_matrix import compute_and_plot_correlation_matrix
band_limits = {band: (int(srf_data[band]['Wavelengths'][0]), 
                        int(srf_data[band]['Wavelengths'].values[-1])) for band in ['B1', 'B2', 'B3', 'B4', 'B5','B6','B7']}

matrix,fig=compute_and_plot_correlation_matrix(datar, band_limits, poc_column='POC_µg_L')
output_path = os.path.join(path, 'output', 'correlation_matrix', 'correlation_matrix.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
#%% ======================== Hyperspectral matrix correlation ========================
from hyperspec_matrix import compute_and_plot_correlation_matrix

# Function to generate connected combinations of classes
def generate_connected_combinations(unique_classes):
    connected_combinations = []
    for r in range(1, len(unique_classes) + 1):  # r = 1 to len(unique_classes)
        for i in range(len(unique_classes) - r + 1):  # Ensure combinations are connected
            connected_combinations.append(unique_classes[i:i + r])
    return connected_combinations

# Generate connected combinations of classes
unique_classes = sorted(datar['Class'].unique())  # Ensure classes are sorted
connected_combinations = generate_connected_combinations(unique_classes)

# Loop through each connected combination of classes and compute the correlation matrix
for class_combination in connected_combinations:
    # Filter data for the current combination of classes
    datar_combination = datar[datar['Class'].isin(class_combination)]
    
    # Define band limits
    band_limits = {band: (int(srf_data[band]['Wavelengths'][0]), 
                          int(srf_data[band]['Wavelengths'].values[-1])) for band in ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']}
    
    # Compute and plot the correlation matrix
    matrix, fig = compute_and_plot_correlation_matrix(datar_combination, band_limits, poc_column='POC_µg_L')
    
    # Generate a descriptive filename for the combination
    combination_label = "_".join(map(str, class_combination))
    output_path = os.path.join(path, 'output', 'correlation_matrix', f'correlation_matrix_classes_{combination_label}.png')
    
    # Save the figure
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
#%% ======================== Hyperspectral matrix correlation datarTran ========================
from hyperspec_matrix import compute_and_plot_correlation_matrix
band_limits = {band: (int(srf_data[band]['Wavelengths'][0]), 
                        int(srf_data[band]['Wavelengths'].values[-1])) for band in ['B1', 'B2', 'B3', 'B4', 'B5','B6','B7']}

matrix,fig=compute_and_plot_correlation_matrix(datarTran, band_limits, poc_column='POC_µg_L')
output_path = os.path.join(path, 'output', 'correlation_matrix', 'correlation_matrixdatarTran.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
#%% ======================== Algo fine tuning ========================
from plot_correl import plot_results_Band_ratio
for i in ['B4','B5','B6']:
    for j in ['B1','B2','B3']:
        print(i,j)
        X,_=simulate_band(datar, 
                        srf_data[i]['Values'],
                        int(srf_data[i]['Wavelengths'][0]),
                        int(srf_data[i]['Wavelengths'].values[-1]))
        Y,_=simulate_band(datar, 
                        srf_data[j]['Values'],
                        int(srf_data[j]['Wavelengths'][0]),
                        int(srf_data[j]['Wavelengths'].values[-1]))
        # plot_log_log_regression(X/Y,datar['POC_µg_L'],xlabel=f'Rrs({i})/Rrs({dic[i]})', ylabel='POC Concentration', title=f'Log-Log Regression for {i} and {dic[i]}')
        
        fig,ax = plt.subplots(figsize=(6, 6))
        ax,_ = plot_results_Band_ratio(datar['POC_µg_L'], X/Y, classif=datar['Class'],
                                     sensor='MSI',ax=ax,labelx=f'Rrs({i})/Rrs({j})',
                                     labely='POC In-situ Concentration',title=f'Log-Log Regression for {i} and {j}',
                                     matrix=False)
        output_path = os.path.join(path, 'output','Band_ratio', f'Band_ratio_{i}_on_{j}.png')
        fig.savefig(output_path, dpi=300)
        plt.close(fig)
#%% ======================== Algo fine tuning datarTran ========================
from plot_correl import plot_results_Band_ratio
for i in ['B4','B5','B6']:
    for j in ['B1','B2','B3']:
        print(i,j)
        X,_=simulate_band(datarTran, 
                        srf_data[i]['Values'],
                        int(srf_data[i]['Wavelengths'][0]),
                        int(srf_data[i]['Wavelengths'].values[-1]))
        Y,_=simulate_band(datarTran, 
                        srf_data[j]['Values'],
                        int(srf_data[j]['Wavelengths'][0]),
                        int(srf_data[j]['Wavelengths'].values[-1]))
        # plot_log_log_regression(X/Y,datar['POC_µg_L'],xlabel=f'Rrs({i})/Rrs({dic[i]})', ylabel='POC Concentration', title=f'Log-Log Regression for {i} and {dic[i]}')
        
        fig,ax = plt.subplots(figsize=(6, 6))
        ax,_ = plot_results_Band_ratio(datarTran['POC_µg_L'], X/Y, classif=datarTran['Class'],
                                     sensor='MSI',ax=ax,labelx=f'Rrs({i})/Rrs({j})',
                                     labely='POC In-situ Concentration',title=f'Log-Log Regression for {i} and {j}',
                                     matrix=False)
        output_path = os.path.join(path, 'output','Band_ratio', f'Band_ratio_{i}_on_{j}_Tran.png')
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

#%% ======================== Matrix of Band_ratio ========================
from plot_correl import plot_results_Band_ratio

# Define the bands for the matrix
bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']

# Create a matrix of plots
fig, axes = plt.subplots(len(bands), len(bands), figsize=(20, 20), constrained_layout=True)

for i, band_x in enumerate(bands):
    for j, band_y in enumerate(bands):
        ax = axes[i, j]
        if i <= j:
            # Leave diagonal and upper triangle plots empty
            ax.axis('off')
            continue
        
        # Simulate bands
        X = simulate_band(datar, 
                          srf_data[band_x]['Values'],
                          int(srf_data[band_x]['Wavelengths'][0]),
                          int(srf_data[band_x]['Wavelengths'].values[-1]))
        Y = simulate_band(datar, 
                          srf_data[band_y]['Values'],
                          int(srf_data[band_y]['Wavelengths'][0]),
                          int(srf_data[band_y]['Wavelengths'].values[-1]))
        
        # Plot the results
        plot_results_Band_ratio(datar['POC_µg_L'], X / Y, classif=datar['Class'], sensor='MSI', ax=ax,
                                labelx=f'Rrs({band_x})/Rrs({band_y})', labely='POC In-situ Concentration',
                                title=f'{band_x} / {band_y}',
                                matrix=True)
        
# Save the matrix of plots
output_path = os.path.join(path, 'output', 'Band_ratio', 'Band_ratio_matrix_lower_triangle.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
#%% ======================== Matrix of Band_ratio ========================
from plot_correl import plot_results_Band_ratio

# Define the bands for the matrix
bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']

# Create a matrix of plots
fig, axes = plt.subplots(len(bands), len(bands), figsize=(20, 20), constrained_layout=True)

for i, band_x in enumerate(bands):
    for j, band_y in enumerate(bands):
        ax = axes[i, j]
        if i <= j:
            # Leave diagonal and upper triangle plots empty
            ax.axis('off')
            continue
        
        # Simulate bands
        X = simulate_band(datarTran, 
                          srf_data[band_x]['Values'],
                          int(srf_data[band_x]['Wavelengths'][0]),
                          int(srf_data[band_x]['Wavelengths'].values[-1]))
        Y = simulate_band(datarTran, 
                          srf_data[band_y]['Values'],
                          int(srf_data[band_y]['Wavelengths'][0]),
                          int(srf_data[band_y]['Wavelengths'].values[-1]))
        
        # Plot the results
        plot_results_Band_ratio(datarTran['POC_µg_L'], X / Y, classif=datarTran['Class'], sensor='MSI', ax=ax,
                                labelx=f'Rrs({band_x})/Rrs({band_y})', labely='POC In-situ Concentration',
                                title=f'{band_x} / {band_y}',
                                matrix=True)
        
# Save the matrix of plots
output_path = os.path.join(path, 'output', 'Band_ratio', 'Band_ratio_matrix_lower_triangleTran.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
#%% ======================== Outlier detection ========================
from plot_outlier import plot_results_Band_ratio_outlier
from spectral_shape import plot_rrs_spectra, plot_rrs_spectra_class
from map_poc import plot_world_map
from plot_correl import plot_results_Band_ratio,plot_results
i = 'B5'
def Tran19FT(BR, intercept_no_outliers, slope_no_outliers):
    def calculate_row(row):
        if row is None or np.isnan(row):  # Handle None or NaN values
            return np.nan  # Return NaN instead of None
        X = np.log(row)
        if intercept_no_outliers is None or slope_no_outliers is None:
            print(intercept_no_outliers, slope_no_outliers)
            raise ValueError("intercept_no_outliers and slope_no_outliers must not be None")
        return 10**(slope_no_outliers * X + intercept_no_outliers)  # 10**(0.928 * X + 2.875)
    
    # Filter out NaN or None values before applying the function
    data = pd.DataFrame({'Band_ratio': BR}).dropna()
    return data['Band_ratio'].apply(calculate_row)

for j in ['B1', 'B2', 'B3']:
    print(i, j)
    X, _ = simulate_band(datar, 
                         srf_data[i]['Values'],
                         int(srf_data[i]['Wavelengths'][0]),
                         int(srf_data[i]['Wavelengths'].values[-1]))
    Y, _ = simulate_band(datar, 
                         srf_data[j]['Values'],
                         int(srf_data[j]['Wavelengths'][0]),
                         int(srf_data[j]['Wavelengths'].values[-1]))
    
    # Create directory for the band ratio if it doesn't exist
    ratio_dir = os.path.join(path, 'output', 'Outliers', f'{i}_on_{j}')
    os.makedirs(ratio_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax, df, intercept_log, slope_log,intercept_no_outliers, slope_no_outliers = plot_results_Band_ratio_outlier(datar, X/Y, classif=datar['Class'],
                                             sensor='MSI', ax=ax, labelx=f'Rrs({i})/Rrs({j})',
                                             labely='POC In-situ Concentration', title=f'Log-Log Regression for {i} and {j}',
                                             matrix=False, remove_outlier=False)
    
    output_path = os.path.join(ratio_dir, f'POC_outliers_{i}_{j}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    # for r in [None, 'europe', 'usa', 'guyane', 'mekongA', 'mekongB']:
    #     fig, ax = plot_world_map(df, 'Lat', 'Lon', 'POC_µg_L', f'Outliers {i}/{j}', region=r)
    #     output_path = os.path.join(ratio_dir, f'POC_OutMap_{i}_{j}_{r if r else "global"}.png')
    #     fig.savefig(output_path, dpi=300)
    #     plt.close(fig)
    
    # fig = plot_rrs_spectra(df, 'POC_µg_L')
    # output_path = os.path.join(ratio_dir, f'POC_Outrrs_spectra_{i}_{j}.png')
    # fig.savefig(output_path, dpi=300)
    # plt.close(fig)

    datar_no_outliers = datar.drop(index=df.index)
    X_noout, _ = simulate_band(datar_no_outliers, 
                         srf_data[i]['Values'],
                         int(srf_data[i]['Wavelengths'][0]),
                         int(srf_data[i]['Wavelengths'].values[-1]))
    Y_noout, _ = simulate_band(datar_no_outliers, 
                         srf_data[j]['Values'],
                         int(srf_data[j]['Wavelengths'][0]),
                         int(srf_data[j]['Wavelengths'].values[-1]))
    BR=X_noout/Y_noout

    Results=Tran19FT(BR, intercept_no_outliers, slope_no_outliers)

    fig,ax=plot_results(Results, datar_no_outliers['POC_µg_L'], 
                classif=datar_no_outliers['Class'],logscale= True,label=f'Rrs({i})/Rrs({j}) no outliers',
    )
    output_path = os.path.join(ratio_dir, f'POC_TranFT_no_out_{i}_{j}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    BR = X / Y
    Results = Tran19FT(BR, intercept_log, slope_log)
    fig,ax=plot_results(Results, datar['POC_µg_L'],
                        classif=datar['Class'],logscale= True,label=f'Rrs({i})/Rrs({j}) with outliers',
    )
    output_path = os.path.join(ratio_dir, f'POC_TranFT_{i}_{j}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
                        

#%% ======================== Empirical algo ========================
from plot_outlier import plot_results_Band_ratio_outlier
from spectral_shape import plot_rrs_spectra, plot_rrs_spectra_class
from map_poc import plot_world_map
from plot_correl import plot_results_Band_ratio,plot_results
def Tran19FT(BR, intercept_no_outliers, slope_no_outliers):
    def calculate_row(row):
        X = np.log1p()
        return 10**(intercept_no_outliers * X + slope_no_outliers) #10**(0.928 * X + 2.875)
    data = pd.DataFrame({'Band_ratio':BR})
    return data.apply(calculate_row, axis=1)

for class_label in datar['Class'].unique():
    datar_class = datar[datar['Class'] == class_label]
    i = 'B5'
    for j in ['B1', 'B2', 'B3']:
        print(f"Class {class_label}: {i} / {j}")
        X, _ = simulate_band(datar_class, 
                             srf_data[i]['Values'],
                             int(srf_data[i]['Wavelengths'][0]),
                             int(srf_data[i]['Wavelengths'].values[-1]))
        Y, _ = simulate_band(datar_class, 
                             srf_data[j]['Values'],
                             int(srf_data[j]['Wavelengths'][0]),
                             int(srf_data[j]['Wavelengths'].values[-1]))
        
        # Create directory for the band ratio if it doesn't exist
        ratio_dir = os.path.join(path, 'output', 'Outliers', f'Class_{class_label}', f'{i}_on_{j}')
        os.makedirs(ratio_dir, exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax, df, intercept_log, slope_log, intercept_no_outliers, slope_no_outliers = plot_results_Band_ratio_outlier(
            datar_class, X/Y, classif=datar_class['Class'], sensor='MSI', ax=ax, 
            labelx=f'Rrs({i})/Rrs({j})', labely='POC In-situ Concentration', 
            title=f'Log-Log Regression for {i} and {j} (Class {class_label})', matrix=False, remove_outlier=False)
        
        output_path = os.path.join(ratio_dir, f'POC_outliers_{i}_{j}.png')
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

        for r in [None, 'europe', 'usa', 'guyane', 'mekongA', 'mekongB']:
            fig, ax = plot_world_map(df, 'Lat', 'Lon', 'POC_µg_L', f'Outliers {i}/{j} (Class {class_label})', region=r)
            output_path = os.path.join(ratio_dir, f'POC_OutMap_{i}_{j}_{r if r else "global"}.png')
            fig.savefig(output_path, dpi=300)
            plt.close(fig)
        
        fig = plot_rrs_spectra(df, 'POC_µg_L')
        output_path = os.path.join(ratio_dir, f'POC_Outrrs_spectra_{i}_{j}.png')
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

        datar_no_outliers = datar_class.drop(index=df.index)
        X_noout, _ = simulate_band(datar_no_outliers, 
                             srf_data[i]['Values'],
                             int(srf_data[i]['Wavelengths'][0]),
                             int(srf_data[i]['Wavelengths'].values[-1]))
        Y_noout, _ = simulate_band(datar_no_outliers, 
                             srf_data[j]['Values'],
                             int(srf_data[j]['Wavelengths'][0]),
                             int(srf_data[j]['Wavelengths'].values[-1]))
        BR = X_noout / Y_noout
        Results = Tran19FT(BR, intercept_no_outliers, slope_no_outliers)
        fig, ax = plot_results(Results,datar_no_outliers['POC_µg_L'], 
                    classif=datar_no_outliers['Class'], logscale=True, 
                    label=f'Rrs({i})/Rrs({j})', title=f'Class {class_label}')
        output_path = os.path.join(ratio_dir, f'POC_TranFT_no_out_{i}_{j}.png')
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

#%% =====================================================================
# ======================== Random Forest Regression + Le 17 Method ========================
from plot_correl import plot_results_Band_ratio,plot_results
bands = ['B2', 'B3', 'B4']
band_eq = {band: simulate_band(datar, srf_data[band]['Values'],
                               int(srf_data[band]['Wavelengths'][0]), 
                               int(srf_data[band]['Wavelengths'].values[-1]))[0] for band in bands}

# Create a DataFrame to facilitate the removal of NaNs
datadf = pd.DataFrame(band_eq)
datadf['POC'] = datar['POC_µg_L']
datadf['Class'] = datar['Class']
# Remove rows containing NaNs
datadf.dropna(inplace=True)

# The columns 'B1', 'B2', ... are the explanatory variables
# And 'POC' is the target variable
X = datadf.filter(like="B")  # Automatically select Rrs columns
y = datadf["POC"]  # Target variable

# Split the data into train (80%) and test (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)

# Create and train the Random Forest model
rf = RandomForestRegressor(n_estimators=1000)
rf.fit(X_train, y_train)

# Predictions
y_pred = rf.predict(X_test)

# Importance of variables (Rrs bands)
importances = pd.Series(rf.feature_importances_, index=X.columns)
importances.sort_values(ascending=False).plot(kind="bar", title="Importance of Rrs bands")
plt.ylabel("Importance")
plt.tight_layout()
plt.savefig('Importance_Rrs_bands.png')
plt.show()

#==============================================================================

# Filtrer les valeurs négatives ou nulles
mask = y > 0
y_filtered = y[mask].reset_index(drop=True)
X_filtered = X[mask].reset_index(drop=True)
Class= datadf['Class'][mask].reset_index(drop=True)
# Appliquer la transformation logarithmique
y_log = np.log(y_filtered)

# Ajuster un nouveau modèle de régression linéaire sur les données transformées en logarithme
lin_reg_log = LinearRegression()
lin_reg_log.fit(X_filtered, y_log)
y_pred_log = lin_reg_log.predict(X_filtered)

# Calcul des statistiques
r2_log = lin_reg_log.score(X_filtered, y_log)
mae_log = mean_absolute_error(y_log, y_pred_log)
rmsle_log = np.sqrt(mean_squared_log_error(y_filtered, np.exp(y_pred_log)))

print(f"R² (log): {r2_log:.3f}")
print(f"MAE (log): {mae_log:.3f}")
print(f"RMSLE: {rmsle_log:.3f}")

# Obtenir les coefficients de la droite de régression
equation_log = f"Log(POC) = {lin_reg_log.intercept_:.3f}"
for i, band in enumerate(X.columns):
    equation_log += f" + ({lin_reg_log.coef_[i]:.3f} * {band})"

print("Équation obtenue (log) :")
print(equation_log)

fig, ax = plot_results(pd.Series(np.exp(y_pred_log)), pd.Series(np.exp(y_log)), classif=Class,
             logscale=True, label='Predicted vs Actual POC', title='Log-Transformed Regression Results')
output_path = os.path.join(path, 'output', 'Regression', 'Log_Transformed_Regression_Results.png')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
fig.savefig(output_path, dpi=300)
plt.show(fig)
#%% =====================================================================
# ======================== Random Forest Regression + Le 17 Method by Class Combination ========================
from itertools import combinations

# Generate connected combinations of classes
def generate_connected_combinations(unique_classes):
    connected_combinations = []
    for r in range(1, len(unique_classes) + 1):  # r = 1 to len(unique_classes)
        for i in range(len(unique_classes) - r + 1):  # Ensure combinations are connected
            connected_combinations.append(unique_classes[i:i + r])
    return connected_combinations

# Get unique classes and generate connected combinations
unique_classes = sorted(datar['Class'].unique())
connected_combinations = generate_connected_combinations(unique_classes)

# Loop through each connected combination of classes
for class_combination in connected_combinations:
    print(f"Processing class combination: {class_combination}")
    
    # Filter data for the current combination of classes
    datar_combination = datar[datar['Class'].isin(class_combination)]
    
    # Simulate bands for the current combination
    bands = ['B2', 'B3', 'B4']
    band_eq = {band: simulate_band(datar_combination, srf_data[band]['Values'],
                                   int(srf_data[band]['Wavelengths'][0]), 
                                   int(srf_data[band]['Wavelengths'].values[-1]))[0] for band in bands}
    
    # Create a DataFrame to facilitate the removal of NaNs
    datadf = pd.DataFrame(band_eq)
    datadf['POC'] = datar_combination['POC_µg_L']
    datadf['Class'] = datar_combination['Class']
    datadf.dropna(inplace=True)  # Remove rows containing NaNs
    
    # Define explanatory variables (bands) and target variable (POC)
    X = datadf.filter(like="B")
    y = datadf["POC"]
    output_dir = os.path.join(path, 'output', 'Regression', f'{len(class_combination)}_Classes')
    
    # Filter out negative or null values for log transformation
    mask = y > 0
    y_filtered = y[mask].reset_index(drop=True)
    X_filtered = X[mask].reset_index(drop=True)
    Class = datadf['Class'][mask].reset_index(drop=True)
    
    # Apply logarithmic transformation
    y_log = np.log(y_filtered)
    
    # Fit a linear regression model on log-transformed data
    lin_reg_log = LinearRegression()
    lin_reg_log.fit(X_filtered, y_log)
    y_pred_log = lin_reg_log.predict(X_filtered)
    
    # Calculate statistics
    r2_log = lin_reg_log.score(X_filtered, y_log)
    mae_log = mean_absolute_error(y_log, y_pred_log)
    rmsle_log = np.sqrt(mean_squared_log_error(y_filtered, np.exp(y_pred_log)))
    
    print(f"Classes {class_combination} - R² (log): {r2_log:.3f}, MAE (log): {mae_log:.3f}, RMSLE: {rmsle_log:.3f}")
    
    # Generate regression equation
    equation_log = f"Log(POC) = {lin_reg_log.intercept_:.3f}"
    for i, band in enumerate(X.columns):
        equation_log += f" + ({lin_reg_log.coef_[i]:.3f} * {band})"
    print(f"Classes {class_combination} - Equation (log): {equation_log}")
    
    # Plot results
    fig, ax = plot_results(pd.Series(np.exp(y_pred_log)), pd.Series(np.exp(y_log)), classif=Class,
                           logscale=True, label='Predicted vs Actual POC',
                           title=f'Log-Transformed Regression Results for Classes {class_combination}')
    output_path = os.path.join(output_dir, f'Log_Transformed_Regression_Results_Classes_{"_".join(map(str, class_combination))}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)