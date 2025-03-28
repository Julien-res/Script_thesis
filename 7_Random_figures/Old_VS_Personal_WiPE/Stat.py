import os
import numpy as np
from osgeo import gdal
import matplotlib.pyplot as plt
from tqdm import tqdm  # Importer tqdm pour la barre de progression

def analyze_pixel_proportions(folder_path):
    # Initialisation des compteurs pour chaque valeur de pixel
    pixel_values = [0, 1, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    categories = {'R1': {value: 0 for value in pixel_values}, 
                  'R2': {value: 0 for value in pixel_values}}
    total_pixels = {'R1': 0, 'R2': 0}

    # Lister tous les fichiers dans le dossier
    files = [file_name for file_name in os.listdir(folder_path) if file_name.endswith('.tif')]
    total_files = len(files)

    # Parcourir toutes les images avec une barre de progression
    with tqdm(total=total_files, desc="Analyse des images") as pbar:
        for file_name in files:
            if file_name.startswith('R1'):
                category = 'R1'
            elif file_name.startswith('R2'):
                category = 'R2'
            else:
                pbar.update(1)  # Mettre à jour la barre même si le fichier est ignoré
                continue

            image_path = os.path.join(folder_path, file_name)
            dataset = gdal.Open(image_path)
            band = dataset.GetRasterBand(1)
            image_array = band.ReadAsArray()

            # Filtrer les pixels -999 (NaN)
            valid_pixels = image_array[image_array != -999]

            # Compter les pixels pour chaque valeur
            for value in pixel_values:
                count = np.sum(valid_pixels == value)
                categories[category][value] += count

            total_pixels[category] += valid_pixels.size

            # Mettre à jour la barre de progression
            pbar.update(1)

    # Calculer les proportions pour chaque catégorie
    proportions = {}
    for category in ['R1', 'R2']:
        proportions[category] = {value: (count / total_pixels[category] if total_pixels[category] > 0 else 0) 
                                 for value, count in categories[category].items()}

    return proportions, pixel_values


# Exemple d'utilisation
folder_path = "/mnt/d/DATA/WiPE/Output"
proportions, pixel_values = analyze_pixel_proportions(folder_path)

# Générer les diagrammes en colonne pour chaque catégorie
for category in ['R1', 'R2']:
    # Exclure la valeur 0 des calculs
    labels = [str(value) for value in pixel_values if value != 0]
    total_without_zeros = sum(proportions[category][value] for value in pixel_values if value != 0)
    proportion_values = [(proportions[category][value] / total_without_zeros) * 100 if total_without_zeros > 0 else 0 
                         for value in pixel_values if value != 0]

    plt.bar(labels, proportion_values, color='skyblue')
    plt.ylabel('Proportion (%)')  # Indiquer que c'est en pourcentages
    if category == 'R1':
        plt.title(f"Proportion de valeurs du nouveau masque parmi l'ancien")
    else:
        plt.title(f"Proportion de valeurs du nouveau masque en dehors de l'ancien")
    plt.ylim(0, 100)  # Ajuster la limite supérieure à 100 pour les pourcentages
    plt.xticks(rotation=45)

    # Ajouter les pourcentages au-dessus des colonnes
    for i, value in enumerate(proportion_values):
        plt.text(i, value + 1, f"{value:.1f}%", ha='center', va='bottom', rotation=45)

    # Sauvegarder l'image au format PNG
    output_file = f"/mnt/c/Travail/Script/Script_thesis/7_Random_figures/Old_VS_Personal_WiPE/{category}_proportions.png"
    plt.savefig(output_file, format='png', bbox_inches='tight')
    plt.close()