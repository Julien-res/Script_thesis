import numpy as np
import pandas as pd

# Charger les SRFs depuis un fichier Excel
def load_srf(file_path, sheet_name):
    """
    Charge les SRFs depuis un fichier Excel.
    :param file_path: Chemin vers le fichier Excel.
    :param sheet_name: Nom de la feuille contenant les SRFs.
    :return: Tuple (longueurs d'onde, SRFs)
    """
    srf_data = pd.read_excel(file_path, sheet_name=sheet_name)
    wavelengths = srf_data["SR_WL"].values  # Longueurs d'onde
    srf_values = srf_data.drop(columns=["SR_WL"]).values  # SRFs des bandes
    return wavelengths, srf_values

# Charger les bandes Sentinel-2 nécessaires
def load_sentinel2_bands(file_path, bands):
    """
    Charge les données des bandes Sentinel-2 depuis un fichier.
    :param file_path: Chemin vers le fichier des réflectances (CSV ou Excel).
    :param bands: Liste des noms de colonnes des bandes Sentinel-2.
    :return: DataFrame contenant les bandes sélectionnées.
    """
    data = pd.read_csv(file_path) if file_path.endswith(".csv") else pd.read_excel(file_path)
    return data[bands]

# Convolution spectrale pour une bande cible
def convolve_band(source_reflectance, source_wavelengths, source_srf, target_wavelength):
    # Poids interpolés autour de la longueur d'onde cible
    weights = np.interp(source_wavelengths, source_wavelengths, source_srf[:, np.argmax(source_wavelengths == target_wavelength)])
    # Normaliser les poids
    weights /= np.sum(weights)
    # Produit pondéré
    return np.sum(source_reflectance * weights)

# Adapter une fonction MERIS à Sentinel-2
def adapt_meris_function_to_s2(s2_reflectance, s2_wavelengths, s2_srf, meris_bands):
    """
    Adapte une fonction MERIS à Sentinel-2 en convoluant les bandes Sentinel-2 vers les bandes MERIS.
    :param s2_reflectance: Réflectance Sentinel-2.
    :param s2_wavelengths: Longueurs d'onde des bandes Sentinel-2.
    :param s2_srf: SRFs des bandes Sentinel-2.
    :param meris_bands: Longueurs d'onde des bandes MERIS utilisées dans la fonction.
    :return: Réflectances Sentinel-2 adaptées aux bandes MERIS.
    """
    meris_reflectance = []
    for band in meris_bands:
        # Convolution spectrale pour chaque bande MERIS
        band_reflectance = convolve_band(s2_reflectance, s2_wavelengths, s2_srf, band)
        meris_reflectance.append(band_reflectance)
    return np.array(meris_reflectance)

# Exemple d'utilisation
if __name__ == "__main__":
    # Chemin du fichier SRF Sentinel-2A
    srf_file_path = "/mnt/data/S2-SRF_COPE-GSEG-EOPG-TN-15-0007_3.2.xlsx"
    data_file_path = "/mnt/data/sentinel2_reflectances.csv"  # Fichier des réflectances Sentinel-2

    # Charger les SRFs de Sentinel-2A
    s2_wavelengths, s2_srf_values = load_srf(srf_file_path, sheet_name="Spectral Responses (S2A)")

    # Définir les bandes MERIS utilisées dans la fonction (en nm)
    meris_bands = [490, 510, 555, 665, 670]

    # Charger les bandes Sentinel-2 nécessaires (bandes proches des longueurs d'onde MERIS)
    sentinel2_bands = ["B2", "B3", "B4", "B5", "B6", "B7"]  # Exemple de colonnes pour Sentinel-2
    s2_data = load_sentinel2_bands(data_file_path, sentinel2_bands)

    # Simuler une réflectance spectrale Sentinel-2 (remplacer par tes propres données)
    s2_reflectance = s2_data.mean(axis=0).values  # Moyenne des pixels, par exemple

    # Adapter la réflectance Sentinel-2 aux bandes MERIS
    meris_reflectance = adapt_meris_function_to_s2(s2_reflectance, s2_wavelengths, s2_srf_values, meris_bands)

    # Exemple d'appel d'une fonction MERIS avec les réflectances adaptées
    def example_meris_function(band490, band510, band555, band665, band670):
        # Calcul simple utilisant les bandes MERIS
        return (band490 + band510) / (band555 + band665 + band670)

    # Appliquer la fonction MERIS aux réflectances adaptées
    result = example_meris_function(*meris_reflectance)
    print("Résultat de la fonction MERIS adaptée à Sentinel-2 :", result)
