import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from dictband import bandsS2A, bandsS2B, bandsMeris, Meris_to_S2

# Used datasets don't have Rrs more than 950nm, so I will use only bands from 412nm to 950nm
# Load data from "Data_RRS_In_Situ"
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return None

def load_srf(band_name, dict_bands, srf_path):
    srf=load_data(srf_path)
    if band_name not in dict_bands:
        raise ValueError(f"Band {band_name} is not in the provided bands dictionary.")
    start_wl, end_wl = dict_bands[band_name]
    wavelengths = srf['SR_WL']
    mask = (wavelengths >= start_wl) & (wavelengths <= end_wl)
    srf_band = srf.loc[mask, band_name]
    return srf_band, start_wl, end_wl

# Simulate Sentinel-2 bands from "Data_RRS_In_Situ" data
def simulate_sentinel_band(data, srf_band, start_wl, end_wl, band_name_MERIS):
    band_name = Meris_to_S2[band_name_MERIS]
    data_band = data.loc[:, str(start_wl):str(end_wl)]
    band = np.sum(data_band.values * srf_band.values, axis=1) / np.sum(srf_band.values)
    return band

# Interpolate Sentinel-2 bands to match the wavelengths of MERIS bands
def interpolate_band(band_MERIS, srf_MERIS, srf_meris, band_name_MERIS):
    interp_func = interp1d(wavelengths_MERIS, srf_meris, kind='linear', bounds_error=False, fill_value="extrapolate")
    interpolated_bands = interp_func(wavelengths_meris)
    # en gros : faut faire une fonction qui va sortir le SRF estimé de ce que sentinel-2 a récupéré basé sur MERIS pour créer une fausse bande MERIS?
    #Je suis pas sûr d'avoir compris
    return interpolated_band

def Leetal(Rrs490,Rrs560,Rrs665)
    D=Rrs560-(Rrs490+(Rrs665-Rrs490)*(Rrs560-Rrs490)/(Rrs665-Rrs490))
    return D


# Charger les données
file_path = '/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo/Data_RRS_In_Situ.csv'
SRF_MERIS='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo/SRF/SRF_MERIS.csv'
SRF_S2A='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo/SRF/SRF_S2A.csv'
data = load_data(file_path)


srf_S2A = {}
srf_S2MERIS = {}

# Charger les SRF
for i in ['B3', 'B5', 'B7']:
    srf_MERIS[i], start_wl[i], end_wl[i] = load_srf(i,bandsMeris,SRF_MERIS)
    srf_S2A[i], start_wl[i], end_wl[i] = load_srf(Meris_to_S2[i], bandsS2A, SRF_S2A)

B3s= simulate_sentinel_band(data, srf_S2A['B3'], start_wl['B3'], end_wl['B3'], 'B3')
B5s= simulate_sentinel_band(data, srf_S2A['B5'], start_wl['B5'], end_wl['B5'], 'B5')
B7s= simulate_sentinel_band(data, srf_S2A['B7'], start_wl['B7'], end_wl['B7'], 'B7')

B3 = interpolate_band(B3s, srf_S2A['B3'], srf_MERIS['B3'], 'B3', bandsS2A, bandsMeris)
B5 = interpolate_band(B5s, srf_S2A['B5'], srf_MERIS['B5'], 'B5', bandsS2A, bandsMeris)
B7 = interpolate_band(B7s, srf_S2A['B7'], srf_MERIS['B7'], 'B7', bandsS2A, bandsMeris)
Results_Le=Leeetal(B3,B5,B7)


import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

# Charger les SRF (exemple avec des fichiers CSV)
srf_meris = pd.read_csv("MERIS_SRF.csv")  # Colonnes: Wavelength, Response
srf_s2 = pd.read_csv("Sentinel2_SRF.csv")  # Colonnes: Wavelength, Response

# Interpolation des SRF sur une même grille spectrale
common_wavelengths = np.linspace(400, 1000, 1000)  # Adapter selon ton besoin
interp_meris = interp1d(srf_meris["Wavelength"], srf_meris["Response"], kind='linear', bounds_error=False, fill_value=0)
interp_s2 = interp1d(srf_s2["Wavelength"], srf_s2["Response"], kind='linear', bounds_error=False, fill_value=0)

srf_meris_resampled = interp_meris(common_wavelengths)
srf_s2_resampled = interp_s2(common_wavelengths)

# Ajustement des bandes Sentinel-2 pour correspondre aux bandes MERIS
weights = srf_meris_resampled / (srf_s2_resampled + 1e-6)  # Éviter division par zéro
sentinel2_fitted = np.dot(weights, srf_s2_resampled)

# Vérifier les résultats
import matplotlib.pyplot as plt
plt.plot(common_wavelengths, srf_meris_resampled, label="MERIS SRF")
plt.plot(common_wavelengths, sentinel2_fitted, label="Sentinel-2 Fitted", linestyle="dashed")
plt.legend()
plt.show()


# bandS2 est ta bande Sentinel-2 sous forme de tableau NumPy (exemple: (rows, cols))

# Normalisation des pondérations pour éviter des erreurs d’échelle
weights /= np.sum(weights)  # Assure que la somme des poids est 1

# Appliquer le band fitting
band_meris_equivalent = bandS2 * weights

# Vérifier que la transformation a bien fonctionné
print("Bande MERIS simulée, shape:", band_meris_equivalent.shape)
