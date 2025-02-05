import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

# Charger les SRF (Spectral Response Functions) pour MSI et MERIS
def load_srf(file_path):
    """
    Charge une SRF à partir d'un fichier CSV.
    Le fichier doit contenir deux colonnes : 'wavelength' et 'response'.
    """
    df = pd.read_csv(file_path)
    return df['wavelength'].values, df['response'].values

# Intégration pondérée pour reconstruire la bande MERIS
def integrate_band(target_srf_wavelengths, target_srf_response, spectrum_wavelengths, spectrum_values):
    """
    Effectue l'intégration pondérée pour reconstruire une bande MERIS à partir du spectre MSI.
    """
    # Interpoler le spectre sur les longueurs d'onde des SRF
    interp_spectrum = interp1d(spectrum_wavelengths, spectrum_values, kind='linear', bounds_error=False, fill_value=0)
    
    # Évaluer le spectre sur les longueurs d'onde MERIS
    resampled_spectrum = interp_spectrum(target_srf_wavelengths)
    
    # Intégration pondérée
    numerator = np.trapz(resampled_spectrum * target_srf_response, target_srf_wavelengths)
    denominator = np.trapz(target_srf_response, target_srf_wavelengths)
    
    return numerator / denominator if denominator != 0 else np.nan

# Charger les SRF de MSI et MERIS
msi_srf_wavelengths, msi_srf_response = load_srf("srf_msi.csv")  # Adapter au fichier MSI
meris_srf_wavelengths, meris_srf_response = load_srf("srf_meris.csv")  # Adapter au fichier MERIS

# Charger un spectre d’entrée (ex. réflectance Sentinel-2 interpolée à haute résolution)
spectrum_df = pd.read_csv("spectrum.csv")  # Adapter au fichier
spectrum_wavelengths = spectrum_df['wavelength'].values
spectrum_values = spectrum_df['reflectance'].values

# Reconstruction des bandes MERIS à partir des données MSI
reconstructed_bands = []
for i, (meris_wl, meris_resp) in enumerate(zip(meris_srf_wavelengths, meris_srf_response)):
    reconstructed_value = integrate_band(meris_wl, meris_resp, msi_srf_wavelengths, spectrum_values)
    reconstructed_bands.append(reconstructed_value)

# Affichage des résultats
for i, value in enumerate(reconstructed_bands):
    print(f"Bande MERIS {i+1}: {value:.4f}")
