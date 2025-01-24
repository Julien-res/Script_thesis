import esa_snappy
from esa_snappy import ProductIO, HashMap, GPF
import numpy as np

def apply_rayleigh_correction(input_path=None, target_res=20, band="B2", resolution_method="Sampling"):
    """
    Applique la correction de Rayleigh à une bande spécifique d'une image Sentinel-2 en utilisant SNAP.

    :param input_path: Chemin d'entrée vers le fichier Sentinel-2 (format SAFE)
    :param target_res: Résolution souhaitée pour la bande (10, 20, 60)
    :param band: Nom de la bande à corriger (ex. "B1")
    :param resolution_method: Méthode de rééchantillonnage (Sampling, Other) => Sampling long mais la correction est calculé à la résolution d'origine
    """
    jpy = esa_snappy.jpy
    Integer = jpy.get_type('java.lang.Integer')
    
    # Charger le produit Sentinel-2
    product = ProductIO.readProduct(input_path)
    if product is None:
        raise RuntimeError("Erreur : le produit Sentinel-2 n'a pas pu être chargé. Vérifiez le chemin d'entrée.")
    print(f"Produit chargé : {product.getName()}")

    # Vérifier si la bande spécifiée existe
    if band not in product.getBandNames():
        raise RuntimeError(f"Erreur : la bande spécifiée '{band}' n'est pas disponible dans le produit.")
    print(f"Bande sélectionnée pour correction : {band}")
    
    resolutions = {
    "B2": 10, "B3": 10, "B4": 10,
    "B7": 20, "B10": 60, "B11": 20, "B12": 20
    }
    res = resolutions.get(band, 60)
    # Rééchantillonnage des bandes à target_res
    print(f'Resolution de la bande : {res}')
    print(f"Rééchantillonnage des bandes à {str(target_res)}m...")

    parameters = HashMap()

    parameters.put('sourceBandNames', band)  # Sélectionner uniquement la bande spécifiée
    parameters.put('computeRBrr', 'true')  # Conserver les bandes corrigées
    if resolution_method == "Sampling":
        print("Méthode de rééchantillonnage : Sampling")
        parameters.put('s2MsiTargetResolution', Integer(res))
    else:
        print("Méthode de rééchantillonnage : Autre")
        parameters.put('s2MsiTargetResolution', Integer(20))

    # Appliquer de la correction
    print("Application de la correction de Rayleigh...")
    # if res!=60:
    try:
        corrected_product = GPF.createProduct("RayleighCorrection", parameters, product)
    except RuntimeError as e:
        raise RuntimeError(f"Erreur lors de l'application de la correction de Rayleigh : {str(e)}")
    
    # Rééchantillonnage des bandes corrigées à target_res
    if target_res != res or (resolution_method != "Sampling" and res != 20):
        resample_params = HashMap()
        resample_params.put('sourceBandNames', band)
        resample_params.put('targetResolution', Integer(target_res))
        resample_params.put('upsampling', 'Nearest')
        resample_params.put('downsampling', 'Mean')
        resample_params.put('targetResolution', Integer(target_res))
        # if res!=60:
        corrected_product = GPF.createProduct("Resample", resample_params, corrected_product)
        # else:
        #     corrected_product = GPF.createProduct("Resample", resample_params, product)
    # if res!=60:
    corrected_band_name = f"rBRR_{band}"
    # else:
    # corrected_band_name = band
    print("Correction et Rééchantillonnage terminés.")

    # Convertir les bandes corrigées en arrays numpy
    if corrected_band_name not in corrected_product.getBandNames():
        raise RuntimeError(f"Erreur : la bande corrigée '{corrected_band_name}' n'est pas disponible après la correction.")

    band = corrected_product.getBand(corrected_band_name)
    width, height = band.getRasterWidth(), band.getRasterHeight()
    print(f"Lecture de la bande corrigée '{corrected_band_name}' ({width}x{height})...")

    # Vérification et initialisation du tableau avec le bon type
    band_type = band.getDataType()
    np_dtype = {
        'float32': np.float32,
        'int16': np.int16,
        'int32': np.int32,
        'uint8': np.uint8,
        'uint16': np.uint16,
    }.get(band_type, np.float32)
    if np_dtype is None:
            raise RuntimeError(f"Type de bande inconnu : {band_type}")
    band_data = np.empty((height, width), dtype=np_dtype)

    # Lecture des pixels
    band.readPixels(0, 0, width, height, band_data)

    print("Correction et rééchantillonnage terminés.")
    return band_data
