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
datar = datar.copy()  # Create a copy to avoid SettingWithCopyWarning
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

# Ensure the length of probabilities matches the length of the DataFrame
if proba.shape[1] != len(datar):
    raise ValueError(f"Length of probabilities ({proba.shape[1]}) does not match length of DataFrame ({len(datar)})")

# Assign probabilities to the datar DataFrame
datar = datar.copy()  # Create a copy of the DataFrame to avoid SettingWithCopyWarning and PerformanceWarning
for i in range(proba.shape[0]):
    datar[f'Prob{i+1}'] = proba[i]

# Remove rows where 'Class' is in [1, 2]
datar = datar[~datar['Class'].isin([1])]
#%% ======================== Combine TranFT and Le17 ========================
# Define a function to calculate the weighted POC based on probabilities and algorithm performance
def Tran19FT(BR, intercept, slope):
    def calculate_row(row):
        if row is None or np.isnan(row):  # Handle None or NaN values
            return np.nan  # Return NaN instead of None
        X = np.log(row)
        if intercept is None or slope is None:
            print(intercept, slope)
            raise ValueError("intercept and slope must not be None")
        return 10**(slope * X + intercept)  # 10**(0.928 * X + 2.875)
    
    # Filter out NaN or None values before applying the function
    data = pd.DataFrame({'Band_ratio': BR}).dropna()
    return data['Band_ratio'].apply(calculate_row)

def calculate_weighted_poc(datar, prob_columns, poc_tranft, poc_le17, class_efficiency):
    """
    Calculate the weighted POC using probabilities and algorithm efficiency per class.

    Parameters:
    - datar: DataFrame containing the data.
    - prob_columns: List of probability column names (e.g., ['Prob1', 'Prob2', ...]).
    - poc_tranft: POC values predicted by TranFT.
    - poc_le17: POC values predicted by Le17.
    - class_efficiency: Dictionary mapping classes to the preferred algorithm ('TranFT' or 'Le17').

    Returns:
    - Weighted POC values as a pandas Series.
    """
    weighted_poc = np.zeros(len(datar))
    for i, prob_col in enumerate(prob_columns, start=1):
        preferred_algo = class_efficiency.get(i, 'TranFT')  # Default to TranFT if not specified
        if preferred_algo == 'TranFT':
            weighted_poc += datar[prob_col] * poc_tranft
        elif preferred_algo == 'Le17':
            weighted_poc += datar[prob_col] * poc_le17
    return pd.Series(weighted_poc, index=datar.index)

# Determine POC using TranFT
poc_tranft = np.zeros(len(datar))

bands = ['B1','B2', 'B3', 'B4', 'B5']
band_eq = {band: simulate_band(datar, srf_data[band]['Values'],
                               int(srf_data[band]['Wavelengths'][0]), 
                               int(srf_data[band]['Wavelengths'].values[-1]))[0] for band in bands}

datadf = pd.DataFrame(band_eq)
datadf['POC'] = datar['POC_µg_L']
datadf['Class'] = datar['Class']
# Create a mask for valid rows (no NaN values and no band values equal to 0)
valid_indices = datadf.notna().all(axis=1) & (datadf != 0).all(axis=1)
# Apply the mask to filter valid indices

BR = datadf['B3'] / datadf['B2']

log_X = np.log10(datadf['POC'])
log_Y = np.log10(BR)

# Remove rows with inf or -inf in either log_X or log_Y
log_X = log_X[valid_indices]
log_Y = log_Y[valid_indices]

model = LinearRegression()
model.fit(log_X.values.reshape(-1, 1), log_Y)
log_predicted = model.predict(log_X.values.reshape(-1, 1))
r2 = r2_score(log_Y, log_predicted)
rmsle = np.sqrt(mean_squared_error(log_Y, log_predicted))
slope = model.coef_[0]
intercept = model.intercept_
poc_tranft = np.zeros(len(BR[valid_indices]))
poc_tranft += Tran19FT(BR[valid_indices], intercept, slope)

# Determine POC using Le17 (linear regression in log-log space)
#Remove B1 and B5
POCLe = datadf.drop(columns=['B1', 'B5']).filter(like="B")
# Apply log transformation to both X and y
log_Y = np.log10(POCLe)

log_Y = log_Y[valid_indices]

lin_reg_le17 = LinearRegression()
lin_reg_le17.fit(log_Y, log_X) # X= BR, Y= In situ POC

# Predict in log space and transform back to original scale
log_predicted = lin_reg_le17.predict(log_Y)
poc_le17 = 10**log_predicted
# Print the equation of the line for Tran19FT
print(f"Tran19FT Equation: y = 10^({slope:.3f} * log(x) + {intercept:.3f})")

# Print the equation of the line for Le17
coefficients = lin_reg_le17.coef_
intercept_le17 = lin_reg_le17.intercept_
print(f"Le17 Equation: y = 10^({coefficients[0]:.3f} * log(x) + {intercept_le17:.3f})")

# Obtenir les coefficients de la droite de régression
equation_log = f"Log(POC) = {lin_reg_le17.intercept_:.3f}"
for i, band in enumerate(POCLe.columns):
    equation_log += f" + ({lin_reg_le17.coef_[i]:.3f} * {band})"
# Print the equation of the line for Le17
print("Équation Le17 obtenue (log) :")
print(equation_log)
# Test multiple class efficiency configurations
possible_configurations = [
    # {1: 'Le17', 2: 'Le17', 3: 'Le17', 4: 'Le17', 5: 'Le17'},
    {1: 'TranFT', 2: 'Le17', 3: 'Le17', 4: 'Le17', 5: 'Le17'},
    {1: 'TranFT', 2: 'TranFT', 3: 'Le17', 4: 'Le17', 5: 'Le17'},
    {1: 'TranFT', 2: 'TranFT', 3: 'TranFT', 4: 'Le17', 5: 'Le17'},
    {1: 'TranFT', 2: 'TranFT', 3: 'TranFT', 4: 'TranFT', 5: 'Le17'}
    # {1: 'TranFT', 2: 'TranFT', 3: 'TranFT', 4: 'TranFT', 5: 'TranFT'},
    # {1: 'Le17', 2: 'Le17', 3: 'Le17', 4: 'Le17', 5: 'TranFT'},
    # {1: 'Le17', 2: 'Le17', 3: 'Le17', 4: 'TranFT', 5: 'TranFT'},
    # {1: 'Le17', 2: 'Le17', 3: 'TranFT', 4: 'TranFT', 5: 'TranFT'},
    # {1: 'Le17', 2: 'TranFT', 3: 'TranFT', 4: 'TranFT', 5: 'TranFT'},
]

best_configuration = None
best_score = float('inf')
prob_columns = ['Prob1', 'Prob2', 'Prob3', 'Prob4', 'Prob5']

results = []

for config in possible_configurations:
    # Calculate the weighted POC for the current configuration
    datar['POC_Weighted'] = calculate_weighted_poc(datar[valid_indices], prob_columns, poc_tranft, poc_le17, config)
    
    # Evaluate the performance using R², RMSLE, MAPD, slope, and intercept in log scale
    log_actual = np.log10(datar['POC_µg_L'][valid_indices])
    log_predicted = np.log10(datar['POC_Weighted'][valid_indices])
    
    r2 = r2_score(log_actual, log_predicted)
    rmsle = np.sqrt(mean_squared_error(log_actual, log_predicted))
    mapd = np.mean(np.abs((datar['POC_µg_L'][valid_indices] - datar['POC_Weighted'][valid_indices]) / datar['POC_µg_L'][valid_indices])) * 100

    # Perform linear regression to evaluate slope and intercept
    slope, intercept = np.polyfit(log_actual, log_predicted, 1)

    # Combine metrics into a single score (e.g., weighted sum of the three metrics and slope/intercept penalties)
    slope_penalty = abs(slope - 1)  # Penalize deviation from slope = 1
    intercept_penalty = abs(intercept)  # Penalize deviation from intercept = 0
    combined_score = rmsle + (1 - r2) + mapd / 100 + slope_penalty + intercept_penalty

    # Store results for visualization
    results.append({
        'Configuration': config,
        'R² (log)': r2,
        'RMSLE (log)': rmsle,
        'MAPD (%)': mapd,
        'Slope': slope,
        'Intercept': intercept,
        'Combined Score': combined_score
    })

    if combined_score < best_score:
        best_score = combined_score
        best_configuration = config

# Convert results to a DataFrame for visualization
results_df = pd.DataFrame(results)

# Plot the results as a table
# fig, ax = plt.subplots(figsize=(10, 4))
# ax.axis('tight')
# ax.axis('off')
# table = ax.table(cellText=results_df.values, colLabels=results_df.columns, loc='center', cellLoc='center')
# table.auto_set_font_size(False)
# table.set_fontsize(10)
# table.auto_set_column_width(col=list(range(len(results_df.columns))))

# plt.title("Comparison Results")
# plt.show()

# Print the sorted DataFrame for reference
results_df = results_df.sort_values(by='Combined Score', ascending=True)
print("Sorted Results:")
print(results_df)

# Use the best configuration
datar['POC_Weighted'] = calculate_weighted_poc(datar[valid_indices], prob_columns, poc_tranft, poc_le17, best_configuration)

from plot_correl import plot_results
fig, ax = plot_results(datar['POC_Weighted'], datar['POC_µg_L'],
                    classif=datar['Class'], logscale=True, 
                    label=f'Le17+Tran19', title=f'POC_Weighted')
plt.show()
print(f"Best configuration: {best_configuration}")
