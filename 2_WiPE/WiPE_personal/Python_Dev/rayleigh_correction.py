import esa_snappy
from esa_snappy import ProductIO, HashMap, GPF
import numpy as np
import subprocess
import os
def apply_rayleigh_correction(input_path,target_res):
    """
    Applique la correction de Rayleigh à des bandes spécifiques d'une image Sentinel-2 en utilisant SNAP.
    
    :param input_path: Chemin d'entrée vers le fichier Sentinel-2 (format SAFE)
    :param target_res: Resolution souhaité pour TOUTES les bandes (10,20,60)
    """
    jpy = esa_snappy.jpy
    Integer = jpy.get_type('java.lang.Integer')
    # Charger le produit Sentinel-2
    product = ProductIO.readProduct(input_path)
    if product is None:
        raise RuntimeError("Erreur : le produit Sentinel-2 n'a pas pu être chargé. Vérifiez le chemin d'entrée.")
    print(f"Produit chargé : {product.getName()}")

    # Bandes à corriger
    target_bands = ['B2', 'B3', 'B4', 'B7', 'B10', 'B11', 'B12']  # Noms des bandes Sentinel-2 à corriger
    available_bands = list(product.getBandNames())
    print(f"Bandes disponibles : {', '.join(available_bands)}")

    # Vérifier si les bandes spécifiées existent
    bands_to_correct = [band for band in target_bands if band in available_bands]
    if  len(bands_to_correct)<7:
        raise RuntimeError("Erreur : une des bandes spécifiées n'est pas disponible dans le produit.")
    print(f"Bandes à corriger : {', '.join(bands_to_correct)}")
    
    # Paramètres pour la correction Rayleigh
    parameters = HashMap()
    parameters.put('sourceBandNames', ','.join(bands_to_correct))  # Sélectionner uniquement les bandes spécifiées
    parameters.put('computeRBrr', 'true')  # Conserver les bandes corrigées
    # Appliquer l'opérateur Rayleigh Correction
    print("Application de la correction de Rayleigh...")
    try:
        corrected_product = GPF.createProduct("RayleighCorrection", parameters, product)
    except RuntimeError as e:
        raise RuntimeError(f"Erreur lors de l'application de la correction de Rayleigh : {str(e)}")

    # Rééchantillonnage des bandes à 10m
    print(f"Rééchantillonnage des bandes à {str(target_res)}m...")
    resample_params = HashMap()
    resample_params.put('targetResolution', Integer(target_res))
    if target_res ==10:
        resample_params.put('upsampling', 'Nearest')  # Méthode de rééchantillonnage
        resample_params.put('sourceBandNames', 'B7,B10,B11,B12')
    elif target_res==20:
        resample_params.put('downsampling', 'Mean')  # Méthode de rééchantillonnage
        resample_params.put('upsampling', 'Nearest')  # Méthode de rééchantillonnage
        resample_params.put('sourceBandNames', 'B2,B3,B4,B10')
    elif target_res==60:
        resample_params.put('downsampling', 'Mean')  # Méthode de rééchantillonnage
        resample_params.put('sourceBandNames', 'B2,B3,B4,B7,B11,B12')
    resampled_product = GPF.createProduct("Resample", resample_params, corrected_product)
    # Convertir les bandes corrigées en arrays numpy
    arrays = {}
    prefix = "rBRR_"
    corrected_band_names = [f"{prefix}{band}" for band in bands_to_correct]
    print(f"Bandes disponibles après correction : {', '.join(resampled_product.getBandNames())}")
    for band_name, corrected_name in zip(bands_to_correct, corrected_band_names):
        if corrected_name not in resampled_product.getBandNames():
            print(f"Attention : la bande {corrected_name} n'est pas disponible après la correction.")
            continue  # Passer à la bande suivante

        band = resampled_product.getBand(corrected_name)
        width, height = band.getRasterWidth(), band.getRasterHeight()
        print(f"Lecture de la bande {corrected_name} ({width}x{height})...")

        # Vérification et initialisation du tableau avec le bon type
        band_type = band.getDataType()
        np_dtype = {
            'float32': np.float32,
            'int16': np.int16,
            'int32': np.int32,
            'uint8': np.uint8,
            'uint16': np.uint16,
        }.get(band_type, np.float32)

        band_data = np.empty((height, width), dtype=np_dtype)

        # Lecture des pixels
        band.readPixels(0, 0, width, height, band_data)
        arrays[band_name] = band_data  # Utiliser le nom d'origine pour le dictionnaire

    print("Correction et rééchantillonnage terminés.")
    return arrays
