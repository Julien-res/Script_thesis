import numpy as np

def calculate_spm(rrs_665):
    """
    Calcule la concentration de SPM à partir des données de réflectance Rrs(665) de Sentinel-2 MSI
    selon l'algorithme semi-analytique du papier.
    
    :param rrs_665: numpy array, réflectance Rrs(665) en sr^-1
    :return: numpy array, concentration de SPM en g/m^3
    """
    pi = np.pi
    rho_w_665 = pi * rrs_665  # Calcul de la réflectance de l'eau
    
    # Initialisation du tableau de sortie
    spm = np.zeros_like(rrs_665)
    
    # Cas 1 : Faible à moyenne turbidité (SAA-L)
    low_turbidity = rrs_665 <= 0.03
    A_rho_L, C_rho_L = 396.005, 0.5
    spm[low_turbidity] = (A_rho_L * rho_w_665[low_turbidity]) / (1 - rho_w_665[low_turbidity] / C_rho_L)
    
    # Cas 2 : Eau très turbide (SAA-HR)
    high_turbidity = rrs_665 >= 0.04
    A_rho_H, C_rho_H = 1208.481, 0.3375
    spm[high_turbidity] = (A_rho_H * rho_w_665[high_turbidity]) / (1 - rho_w_665[high_turbidity] / C_rho_H)
    
    # Cas 3 : Transition entre faible et forte turbidité (pondération)
    transition_zone = (rrs_665 > 0.03) & (rrs_665 < 0.04)
    if np.any(transition_zone):
        w_L = (np.log10(0.04) - np.log10(rrs_665[transition_zone])) / (np.log10(0.04) - np.log10(0.03))
        w_H = (np.log10(rrs_665[transition_zone]) - np.log10(0.03)) / (np.log10(0.04) - np.log10(0.03))
        spm_L = (A_rho_L * rho_w_665[transition_zone]) / (1 - rho_w_665[transition_zone] / C_rho_L)
        spm_H = (A_rho_H * rho_w_665[transition_zone]) / (1 - rho_w_665[transition_zone] / C_rho_H)
        spm[transition_zone] = (w_L * spm_L + w_H * spm_H) / (w_L + w_H)
    
    return spm

# Exemple d'utilisation avec des valeurs fictives de Rrs(665)
rrs_665_values = np.array([0.01, 0.02, 0.035, 0.045, 0.05])  # Exemple de valeurs Rrs(665)
spm_values = calculate_spm(rrs_665_values)
print("SPM estimée (g/m^3) :", spm_values)
