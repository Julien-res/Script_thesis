import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
# path='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo'
path='/mnt/c/Users/Julien/Documents/GitHub/Script_thesis/5_SPM_POC/Determination_Best_algo'
os.chdir(path)
from dictband import bandsS2A, bandsS2B, bandsMeris, Meris_to_S2

# Used datasets don't have Rrs more than 950nm, so I will use only bands from 412nm to 950nm
# Load data from "Data_RRS_In_Situ"
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

def Leetal(Rrs490, Rrs560, Rrs665):
    D = Rrs560 - (Rrs490 + ((555 - 490) / (555 - 490)) * (Rrs665 - Rrs490))
    return np.where(D <= -0.0005, 10**(185.72*D + 1.97), 10**(485.19*D + 2.1))

# Load datas
file_path = os.path.join(path+'/Data_RRS_In_Situ.csv')
SRF_MERIS=os.path.join(path+'/SRF/SRF_MERIS.csv')
SRF_S2A=os.path.join(path+'/SRF/SRF_S2A.csv')
SRF_S2B=os.path.join(path+'/SRF/SRF_S2B.csv')
data = load_data(file_path)

srf_MERIS = {}
start_wlMERIS = {}
end_wlMERIS = {}
wavelengthsMERIS = {}
interp_meris = {}

srf_S2A = {}
start_wlS2A = {}
end_wlS2A = {}
wavelengthsS2A = {}
interp_s2 = {}

band_meris_equivalent_tot={}

for i in ['B3', 'B5', 'B7']:
    start_wlMERIS[i], end_wlMERIS[i], srf_MERIS[i], wavelengthsMERIS[i] = load_srf(i,bandsMeris,SRF_MERIS)
    start_wlS2A[i], end_wlS2A[i], srf_S2A[i], wavelengthsS2A[i] = load_srf(Meris_to_S2[i], bandsS2A, SRF_S2A)
    common_wavelengths = np.linspace(int(wavelengthsS2A[i].values[0])-2, int(wavelengthsS2A[i].values[-1])+2, 1000)  # Adapt to needs

    interp_meris[i] = interp1d(wavelengthsMERIS[i], srf_MERIS[i], kind='linear', bounds_error=False, fill_value=0)
    interp_s2[i] = interp1d(wavelengthsS2A[i], srf_S2A[i], kind='linear', bounds_error=False, fill_value=0)

    srf_meris_resampled = interp_meris[i](common_wavelengths)
    srf_s2_resampled = interp_s2[i](common_wavelengths)
    plt.plot(common_wavelengths, srf_meris_resampled, label="MERIS SRF")
    # Band fitting
    weights = srf_meris_resampled / (srf_s2_resampled + 1e-6)  # avoid dividing by zero
    sentinel2_fitted = weights * srf_s2_resampled

    plt.plot(common_wavelengths, sentinel2_fitted, label="Sentinel-2 Fitted", linestyle="dashed")
    plt.legend()
    plt.show()

    # Normalize weights
    weights /= np.sum(weights)  # Assure que la somme des poids est 1
    bandS2 = simulate_sentinel_band(data, srf_S2A[i], start_wlS2A[i], end_wlS2A[i])

    # Apply bad fitting
    band_meris_equivalent = np.zeros(bandS2.shape[0])
    b=0
    for a in bandS2:
        band_meris_equivalent [b] = np.sum(a * weights)
        b=b+1
    band_meris_equivalent_tot[i]=band_meris_equivalent

Results_Le=Leetal(band_meris_equivalent_tot['B3'],band_meris_equivalent_tot['B5'],band_meris_equivalent_tot['B7'])
# Results_Le=Results_Le/100
POC=data['POC_microg_L']
plt.plot(POC)
plt.show

plt.plot(Results_Le)
plt.show()
