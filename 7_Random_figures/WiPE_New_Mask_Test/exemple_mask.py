import os
import re
import rasterio
import numpy as np
from collections import defaultdict

directory = '/mnt/d/DATA/WiPE/TREATED'
mask_values = [0, 1, 10, 20, 30, 40, 50, 60, 70, 80, 90]
pattern_regex = re.compile(r'T\d{2}[A-Z]{3}')

# Récupère toutes les tuiles correspondant au pattern
tif_files = [f for f in os.listdir(directory) if f.endswith('.tif')]
patterns = set()
for f in tif_files:
    match = pattern_regex.search(f)
    if match:
        patterns.add(match.group())

images_by_pattern = defaultdict(lambda: defaultdict(list))

# Parcourt chaque pattern et sélectionne max 2 images remplissant la condition pour chaque valeur
for pat in patterns:
    for val in mask_values:
        count_found = 0
        for f in tif_files:
            if pat in f:
                filepath = os.path.join(directory, f)
                with rasterio.open(filepath) as src:
                    img = src.read(1)
                    total_pixels = img.size
                    val_count = np.count_nonzero(img == val)
                    percentage = (val_count / total_pixels) * 100
                    print(f" Pat : {pat}, Valeur: {val}, Pourcentage: {percentage:.2f}%")
                    if percentage >= 10:
                        images_by_pattern[pat][val].append(f)
                        count_found += 1
                        print(f"\033[91mImage trouvée pour {pat}, Valeur {val}: {f}\033[0m")
                        if count_found == 2:
                            break

print("Images sélectionnées :")
for pat, val_imgs in images_by_pattern.items():
    for val, imgs in val_imgs.items():
        print(f"{pat}, Valeur {val}: {imgs}")
