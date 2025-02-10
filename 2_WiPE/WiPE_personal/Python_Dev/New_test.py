import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# path = '/mnt/c/Users/Julien/Documents/GitHub/Script_thesis/5_SPM_POC/Determination_Best_algo'
path='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo'
os.chdir(path)
from dictband import bandsS2A, bandsS2B, bandsMeris, Meris_to_S2

def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        exit(1)

def load_srf(band, bands_dict, srf_path):
    srf = load_data(srf_path)
    if band not in bands_dict:
        raise ValueError(f"Band {band} is not in the provided bands dictionary.")
    start, end = bands_dict[band]
    mask = (srf['SR_WL'] >= start) & (srf['SR_WL'] <= end)
    return start, end, srf.loc[mask, band], srf['SR_WL'][mask]

def simulate_band(data, srf_band, start, end):
    data_band = data.loc[:, str(start):str(end)]
    return np.sum(data_band.values * srf_band.values, axis=1) / np.sum(srf_band.values)

def Le(Rrs490, Rrs560, Rrs665):
    D = Rrs560 - (Rrs490 + ((555 - 490) / (555 - 490)) * (Rrs665 - Rrs490))
    return np.where(D <= -0.0005, 10**(185.72*D + 1.97), 10**(485.19*D + 2.1))
def Yu
return None
def Stramski
return None
def Tran
return None
def Duy
return None


file_path = os.path.join(path, 'Data_RRS_In_Situ.csv')
srf_meris_path = os.path.join(path, 'SRF/SRF_MERIS.csv')
srf_s2a_path = os.path.join(path, 'SRF/SRF_S2A.csv')
data = load_data(file_path)

srf_meris = {}
start_meris = {}
end_meris = {}
wl_meris = {}

srf_s2a = {}
start_s2a = {}
end_s2a = {}

band_eq = {}

for band in ['B3', 'B5', 'B7']:
    start_meris[band], end_meris[band], srf_meris[band], wl_meris[band] = load_srf(band, bandsMeris, srf_meris_path)
    start_s2a[band], end_s2a[band], srf_s2a[band], wl_s2a[band] = load_srf(Meris_to_S2[band], bandsS2A, srf_s2a_path)

    band_s2 = simulate_band(data, srf_s2a[band], start_s2a[band], end_s2a[band])

    band_eq[band] = np.array([np.sum(a * weights) for a in band_s2])

results_le = Leetal(band_eq['B3'], band_eq['B5'], band_eq['B7'])
poc = data['POC_microg_L']

plt.plot(poc)
plt.show()

plt.plot(results_le)
plt.show()
