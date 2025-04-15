import os
import numpy as np
import rasterio
import xml.etree.ElementTree as ET
import pandas as pd
from glob import glob
from scipy.ndimage import zoom
from scipy.interpolate import RegularGridInterpolator

# === CONSTANTES ===
WAVELENGTHS = {
    'B01': (443, 60),
    'B02': (490, 10),
    'B03': (560, 10),
    'B04': (665, 10),
    'B05': (705, 20),
    'B06': (740, 20),
    'B07': (783, 20),
    'B08': (842, 10),
    'B8A': (865, 20),
}
STANDARD_PRESSURE = 1013.25  # hPa

# === SRF ===
def load_srf(band, srf_path='SRF_S2A.csv'):
    band_column = band.replace('B8A', 'B8A').replace('B0', 'B')
    if not hasattr(load_srf, "srf_cache"):
        load_srf.srf_cache = pd.read_csv(srf_path)
    df = load_srf.srf_cache
    wavelengths = df['SR_WL'].values
    responses = df[band_column].values
    return wavelengths, responses

def rayleigh_optical_thickness(wavelength_nm):
    wl_um = wavelength_nm / 1000.0
    return 0.008569 * wl_um**(-4) * (1 + 0.0113 * wl_um**(-2) + 0.00013 * wl_um**(-4))

def tau_r_from_srf(srf_wl, srf_resp):
    tau = rayleigh_optical_thickness(srf_wl)
    return np.trapz(tau * srf_resp, srf_wl) / np.trapz(srf_resp, srf_wl)

# === PHYSIQUE RAYLEIGH ===
def scattering_angles(sza, saa, vza, vaa):
    sza_rad, saa_rad = np.radians(sza), np.radians(saa)
    vza_rad, vaa_rad = np.radians(vza), np.radians(vaa)
    delta_phi = np.abs(saa_rad - vaa_rad)

    theta_plus = np.arccos(np.clip(np.cos(sza_rad)*np.cos(vza_rad) + np.sin(sza_rad)*np.sin(vza_rad)*np.cos(delta_phi), -1, 1))
    theta_minus = np.arccos(np.clip(np.cos(sza_rad)*np.cos(vza_rad) - np.sin(sza_rad)*np.sin(vza_rad)*np.cos(delta_phi), -1, 1))
    return theta_plus, theta_minus

def fresnel_reflectance(theta_rad, n_w=1.34):
    sin_theta_t = np.sin(theta_rad) / n_w
    sin_theta_t = np.clip(sin_theta_t, 0, 1)
    theta_t = np.arcsin(sin_theta_t)
    rs = (np.sin(theta_rad - theta_t) / np.sin(theta_rad + theta_t))**2
    rp = (np.tan(theta_rad - theta_t) / np.tan(theta_rad + theta_t))**2
    return 0.5 * (rs + rp)

def rayleigh_phase_full(theta_plus, theta_minus):
    Pr_plus = 0.75 * (1 + np.cos(theta_plus)**2)
    Pr_minus = 0.75 * (1 + np.cos(theta_minus)**2)
    r = fresnel_reflectance(theta_minus)
    return Pr_plus + r * Pr_minus

def compute_rho_r_full(wl, sza, saa, vza, vaa, band, pressure=STANDARD_PRESSURE,SRF_PATH='SRF_S2A.csv'):
    theta_plus, theta_minus = scattering_angles(sza, saa, vza, vaa)
    Pr = rayleigh_phase_full(theta_plus, theta_minus)
    srf_wl, srf_resp = load_srf(band, srf_path=SRF_PATH)
    tau_r = tau_r_from_srf(srf_wl, srf_resp) * pressure / STANDARD_PRESSURE
    denom = 4 * np.cos(np.radians(sza)) * np.cos(np.radians(vza))
    return tau_r * Pr / denom

# === MÉTADONNÉES XML ===
def parse_angle_grid(xml_path,band):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extraire dynamiquement le namespace
    nsmap = root.tag[root.tag.find("{")+1:root.tag.find("}")]
    ns = {'n': nsmap}

    def extract_values_list(path):
        element = root.find(path, ns)
        values = []
        for val_list in element.findall('Values_List/VALUES', ns):
            row = [float(v) for v in val_list.text.strip().split()]
            values.append(row)
        return np.array(values)

    def extract_mean_value(path, band, angle_type):
        elements = root.findall(path, ns)
        for elem in elements:
            if elem.attrib.get('bandId') == str(band):
                angle = elem.find(f"{angle_type}", ns)
                if angle is not None and angle.text.strip():
                    return float(angle.text.strip())
        return 0

    # Extraire les grilles d'angles
    sza = extract_values_list('.//Sun_Angles_Grid/Zenith')
    saa = extract_values_list('.//Sun_Angles_Grid/Azimuth')
    vza_mean = extract_mean_value('.//Mean_Viewing_Incidence_Angle_List/Mean_Viewing_Incidence_Angle', band, 'ZENITH_ANGLE')
    vaa_mean = extract_mean_value('.//Mean_Viewing_Incidence_Angle_List/Mean_Viewing_Incidence_Angle', band, 'AZIMUTH_ANGLE')

    # Créer des matrices 23x23 pour vza et vaa avec la valeur moyenne
    vza = np.full((23, 23), vza_mean)
    vaa = np.full((23, 23), vaa_mean)

    return {'SZA': sza, 'SAA': saa, 'VZA': vza, 'VAA': vaa}

def interpolate_angle_grid(grid_23x23, target_shape):
    ny, nx = grid_23x23.shape
    y = np.linspace(0, 1, ny)
    x = np.linspace(0, 1, nx)
    interpolator = RegularGridInterpolator((y, x), grid_23x23, bounds_error=False, fill_value=None)

    tgt_y = np.linspace(0, 1, target_shape[0])
    tgt_x = np.linspace(0, 1, target_shape[1])
    mesh_y, mesh_x = np.meshgrid(tgt_y, tgt_x, indexing='ij')
    coords = np.stack((mesh_y, mesh_x), axis=-1)
    return interpolator(coords)

# === IMAGE ===
def read_jp2(path):
    with rasterio.open(path) as src:
        return src.read(1).astype(np.float32), src.transform, src.res

# === TRAITEMENT PRINCIPAL ===
def correct_rayleigh_safe_resampled(safe_path, band_name, output_resolution):
    # Convertir le nom de la bande pour correspondre au format attendu
    band_name = band_name if len(band_name) == 3 else f"B0{band_name[1]}"

    granule_dir = os.path.join(safe_path, 'GRANULE')
    granule = next(os.walk(granule_dir))[1][0]
    granule_path = os.path.join(granule_dir, granule)
    sensor = os.path.basename(safe_path).split('_')[0]
    # Déterminer le chemin du fichier SRF en fonction du capteur
    srf_path = os.path.join(os.path.dirname(__file__), f"SRF_{sensor}.csv")
    # Lire le XML de métadonnées de la tuile
    xml_path = glob(os.path.join(granule_path, 'MTD_TL*.xml'))[0]

    img_data_path = os.path.join(granule_path, 'IMG_DATA')

    # Vérifier si la bande demandée existe dans les constantes
    if band_name not in WAVELENGTHS:
        raise ValueError(f"La bande {band_name} n'est pas supportée.")

    wl, band_resolution = WAVELENGTHS[band_name]

    # Vérifier si la résolution demandée est valide
    if output_resolution not in [10, 20, 60]:
        raise ValueError("La résolution de sortie doit être 10, 20 ou 60 mètres.")

    # Trouver le chemin de l'image pour la bande demandée
    band_path = glob(os.path.join(img_data_path, f'*{band_name}*.jp2'))
    if not band_path:
        raise FileNotFoundError(f"Aucune image trouvée pour la bande {band_name}.")

    with rasterio.open(band_path[0]) as src:
        rho_toa = src.read(1).astype(np.float32) / 10000
        transform = src.transform
        target_shape = rho_toa.shape

    # Si la résolution de la bande ne correspond pas à la résolution de sortie, interpoler
    if band_resolution != output_resolution:
        scale_factor = band_resolution / output_resolution
        rho_toa = zoom(rho_toa, scale_factor, order=1)
        target_shape = rho_toa.shape

    # Récupération des grilles d'angles spécifiques à la bande
    band_angle_grids = parse_angle_grid(xml_path, band_name)

    # Interpolation des grilles d’angles
    sza = interpolate_angle_grid(band_angle_grids['SZA'], target_shape)
    saa = interpolate_angle_grid(band_angle_grids['SAA'], target_shape)
    vza = interpolate_angle_grid(band_angle_grids['VZA'], target_shape)
    vaa = interpolate_angle_grid(band_angle_grids['VAA'], target_shape)

    # Calcul de la correction Rayleigh
    rho_r = compute_rho_r_full(wl, sza, saa, vza, vaa, band_name, SRF_PATH=srf_path)
    rho_rc = rho_toa - rho_r

    return rho_rc
