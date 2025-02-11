import os
import numpy as np
import pandas as pd
path='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo'
# path='/mnt/c/Users/Julien/Documents/GitHub/Script_thesis/5_SPM_POC/Determination_Best_algo'
os.chdir(path)
from dictband import bandsS2A, bandsS2B, bandsMeris, Meris_to_S2

def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        exit(1)

def load_srf(band_name, dict_bands, srf_path):
    srf = load_data(srf_path)
    if band_name not in dict_bands:
        raise ValueError(f"Band {band_name} is not in the provided bands dictionary.")
    start_wl, end_wl = dict_bands[band_name]
    mask = (srf['SR_WL'] >= start_wl) & (srf['SR_WL'] <= end_wl)
    return start_wl, end_wl, srf.loc[mask, band_name], srf['SR_WL'][mask]

# Simulate Sentinel-2 bands from "Data_RRS_In_Situ" data
def simulate_sentinel_band(data, srf_band, start_wl, end_wl):
    data_band = data.loc[:, str(start_wl):str(end_wl)]
    return np.sum(data_band.values * srf_band.values, axis=1) / np.sum(srf_band.values)

# Load datas
file_path = os.path.join(path+'/Data_RRS_In_Situ.csv')
SRF_S2A=os.path.join(path+'/SRF/SRF_S2A.csv')
data = load_data(file_path)

results = []

srf_S2A = {}
start_wlS2A = {}
end_wlS2A = {}
wavelengthsS2A = {}
interp_s2 = {}

for i in ['B2', 'B3', 'B5', 'B7']:
    start_wlS2A[i], end_wlS2A[i], srf_S2A[i], wavelengthsS2A[i] = load_srf(Meris_to_S2[i], bandsS2A, SRF_S2A)
    # Normalize weights
    bandS2 = simulate_sentinel_band(data, srf_S2A[i], start_wlS2A[i], end_wlS2A[i])
    results.append([i] + bandS2.tolist())

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Drop columns with any NaN values
results_df.dropna(axis=1, inplace=True)

# Save results to CSV without header
results_df.to_csv(os.path.join(path, 'Simulated_S2INSITU.csv'), index=False, header=False)

# Transpose the DataFrame to save results in columns
results_df_transposed = results_df.T

# Save the transposed results to another CSV
results_df_transposed.to_csv(os.path.join(path, 'Simulated_S2INSITU_columns.csv'), index=False, header=False)