import snappy
from snappy import ProductIO, HashMap, GPF
def apply_rayleigh_correction(input_path, output_path):
    """
    Applique la correction de Rayleigh à une image Sentinel-2 en utilisant SNAP.
    
    :param input_path: Chemin d'entrée vers le fichier Sentinel-2 (format SAFE)
    :param output_path: Chemin de sauvegarde pour le fichier corrigé
    """
    # Charger le produit Sentinel-2
    product = ProductIO.readProduct(input_path)
    print(f"Produit chargé : {product.getName()}")

    # Paramètres pour la correction Rayleigh
    parameters = HashMap()
    parameters.put('outputBands', 'true')  # Exemple : conserver les bandes corrigées

    # Appliquer l'opérateur Rayleigh Correction
    corrected_product = GPF.createProduct("RayleighCorrection", parameters, product)
    
    # Sauvegarder le produit corrigé
    ProductIO.writeProduct(corrected_product, output_path, "GeoTIFF")
    print(f"Produit corrigé sauvegardé dans : {output_path}")
