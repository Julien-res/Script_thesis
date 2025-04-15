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
from plot_outlier import plot_results_Band_ratio_outlier
from plot_correl import plot_results_Band_ratio,plot_results
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
datar['Prob1'] = proba[0]
datar['Prob2'] = proba[1]
datar['Prob3'] = proba[2]
datar['Prob4'] = proba[3]
datar['Prob5'] = proba[4]
datar = datar.copy() # Create a copy of the DataFrame to avoid SettingWithCopyWarning and PerformanceWarning

datarLOWPOC = datar[datar['POC_µg_L'] < 1000]
datarHIGHPOC = datar[datar['POC_µg_L'] >= 1000]
datarTran= datar[datar['POC_µg_L'] > 100]


i = 'B5'
j='B1'
def Tran19FT(BR, intercept_no_outliers, slope_no_outliers):
    def calculate_row(row):
        if row is None or np.isnan(row):  # Handle None or NaN values
            return np.nan  # Return NaN instead of None
        X = np.log(row)
        return 10**(slope_no_outliers * X + intercept_no_outliers)  # 10**(0.928 * X + 2.875)
    
    # Filter out NaN or None values before applying the function
    data = pd.DataFrame({'Band_ratio': BR}).dropna()
    return data['Band_ratio'].apply(calculate_row)

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
# fig.savefig(output_path, dpi=300)
plt.show(fig)

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
print(intercept_no_outliers, slope_no_outliers)
Results=Tran19FT(BR, intercept_no_outliers, slope_no_outliers)

fig,ax=plot_results(Results, datar_no_outliers['POC_µg_L'], 
            classif=datar_no_outliers['Class'],logscale= True,label=f'Rrs({i})/Rrs({j})',
)
output_path = os.path.join(ratio_dir, f'POC_TranFT_no_out_{i}_{j}.png')
# fig.savefig(output_path, dpi=300)