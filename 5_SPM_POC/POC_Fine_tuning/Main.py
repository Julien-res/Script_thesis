#%%
%reload_ext autoreload
%autoreload 2
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
path='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/POC_Fine_tuning'
sys.path.append(path)
os.chdir(path)
from load_datas import load_data, load_srf_data, simulate_band
sys.path.append('/mnt/c/Travail/Script/Chl-CONNECT')
from Dict import SENSOR_BANDS
from common.Chl_CONNECT import Chl_CONNECT

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

band_class = {band: simulate_band(datar, srf_data[band]['Values'],
                                    int(srf_data[band]['Wavelengths'][0]), 
                                    int(srf_data[band]['Wavelengths'].values[-1])) for band in SENSOR_BANDS['MSI']}

Rrs_class = np.array(list(band_class.values())).T
classif = Chl_CONNECT(Rrs_class, method='logreg', sensor='MSI', logRrsClassif=False, pTransform=False).Class
datar['Class'] = classif
#%% ======================== Map data ========================
from map_poc import plot_world_map
for i in [None, 'europe', 'usa', 'guyane', 'mekongA', 'mekongB']:
    fig, ax = plot_world_map(datar, 'Lat', 'Lon', 'POC_µg_L', 'POC with in-situ Rrs', region=i)
    output_path = os.path.join(path, 'output', f'POC_with_in_situ_Rrs_{i if i else "global"}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    fig, ax = plot_world_map(dataMU, 'Lat', 'Lon', 'POC_µg_L', 'POC without in-situ Rrs', region=i)
    output_path = os.path.join(path, 'output', f'POC_without_in_situ_Rrs_{i if i else "global"}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

#%% ======================== Spectral shape and data cleaning ========================
from spectral_shape import plot_rrs_spectra_interactive,plot_rrs_spectra,plot_rrs_spectra_class
fig = plot_rrs_spectra(datar, 'POC_µg_L')
output_path = os.path.join(path, 'output', 'POC_rrs_spectra.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)

fig = plot_rrs_spectra_class(datar, 'Class')
output_path = os.path.join(path, 'output', 'Class_rrs_spectra.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
# plot_rrs_spectra_interactive(datar, 'POC_µg_L')
#%% ======================== Frequency plot ========================
from frequency_plot import plot_frequency_distribution
fig = plot_frequency_distribution(datar, 'POC_µg_L')
output_path = os.path.join(path, 'output', 'POC_frequency_distribution.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)
#%% ======================== Hyperspectral matrix correlation ========================
from hyperspec_matrix import compute_and_plot_correlation_matrix
band_limits = {band: (int(srf_data[band]['Wavelengths'][0]), 
                        int(srf_data[band]['Wavelengths'].values[-1])) for band in ['B1', 'B2', 'B3', 'B4', 'B5','B6','B7']}

matrix,fig=compute_and_plot_correlation_matrix(datar, band_limits, poc_column='POC_µg_L')
output_path = os.path.join(path, 'output', 'correlation_matrix.png')
fig.savefig(output_path, dpi=300)
plt.close(fig)

#%% ======================== Algo fine tuning ========================
from plot_correl import plot_results_Band_ratio

dic={'B4':'B2','B5':'B2','B6':'B2','B1':'B5','B2':'B5','B3':'B5'}
for i in dic.keys():
    print(i,dic[i])
    X=simulate_band(datar, 
                    srf_data[i]['Values'],
                    int(srf_data[i]['Wavelengths'][0]),
                    int(srf_data[i]['Wavelengths'].values[-1]))
    Y=simulate_band(datar, 
                    srf_data[dic[i]]['Values'],
                    int(srf_data[dic[i]]['Wavelengths'][0]),
                    int(srf_data[dic[i]]['Wavelengths'].values[-1]))
    # plot_log_log_regression(X/Y,datar['POC_µg_L'],xlabel=f'Rrs({i})/Rrs({dic[i]})', ylabel='POC Concentration', title=f'Log-Log Regression for {i} and {dic[i]}')
    
    fig,ax = plt.subplots(figsize=(6, 6))
    ax = plot_results_Band_ratio(datar['POC_µg_L'], X/Y, classif=datar['Class'], sensor='MSI', label=f'Rrs({i})/Rrs({dic[i]})',ax=ax)
    output_path = os.path.join(path, 'output', f'Band_ratio_{i}_to_{dic[i]}.png')
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


#%% =====================================================================
# POC algo
algorithms = [
    {
        'sensor': 'MERIS',
        'bands': ['B3', 'B4', 'B5', 'B7'],
    }
]
def Tran19(Rrs490, Rrs510, Rrs555, Rrs665,**kwargs):
    if kwargs.get('sensor', None) != 'MERIS':
        raise ValueError("Tran19 algorithm is only available for MERIS sensor.")
    def calculate_row(row):
        X = np.log1p(max(row['Rrs665'] / row['Rrs490'] - 1, row['Rrs665'] / row['Rrs510'] - 1, row['Rrs665'] / row['Rrs555'] - 1))
        return 10**(0.928 * X + 2.875) #10**(0.928 * X + 2.875)

    data = pd.DataFrame({'Rrs490': Rrs490, 'Rrs510': Rrs510, 'Rrs555': Rrs555, 'Rrs665': Rrs665})
    return data.apply(calculate_row, axis=1)