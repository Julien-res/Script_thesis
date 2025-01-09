import numpy as np

def applyWiPE(bands):
    """Applique les calculs de WiPE.
    Prends en entrée les bandes 2,3,4,7,10,11,12 au format liste
                                0,1,2,3,04,05,06"""

    # Vérification des dimensions des bandes
    for i in range(len(bands) - 1):
        if bands[i].shape != bands[i + 1].shape:
            raise ValueError("Toutes les bandes doivent avoir les mêmes dimensions.")
    # Initialisation du masque
    mask = np.ones_like(bands[2], dtype=np.uint64)

    # Identification des pixels où les bandes 2, 3, et 4 sont toutes à 255
    invalid_pixels = (bands[0] == 255) & (bands[1] == 255) & (bands[2] == 255)

    # Remplacement des pixels problématiques par np.nan
    for i in range(3):  # Seulement pour les bandes 2, 3, et 4
        bands[i] = np.where(invalid_pixels, 0, bands[i])

    mask = (invalid_pixels, 0, mask)
    # Étape 1 : Filtrage avec des conditions
    print("Step 1")
    mask[bands[5] / bands[2] > 0.69] = 0 #1.1
    mask[bands[5] > 0.035] = 0 #1.2
    mask[(bands[0] < 0.0065) | (bands[4] > 0.01072)] = 0 #1.3

    # Étape 2 : ""Normalisation des bandes""
    print("Step 2 - Normalisation")
    max_bands = [
        band / np.nanmax(band)  for band in bands[:3]
    ]
    stacked = np.stack(max_bands, axis=0)
    max_bands = None
    # Recherche de V maximum et minimum
    source_max = np.argmax(stacked, axis=0)
    source_min = np.argmin(stacked, axis=0)

    # Parcours de chaque pixel pour appliquer les conditions supplémentaires
    rows, cols = bands[4].shape
    for i in range(rows):
        for j in range(cols):
            if mask[i, j] != 0:
                if source_max[i, j] == 0:  # Cas 2.1
                    if stacked[0, i, j] > (-2.93 * (bands[5][i, j] / bands[3][i, j]) + 2):
                        mask[i, j] = 0
                    if (bands[6][i, j] / bands[2][i, j] > 0.28 or
                        (stacked[0, i, j] - stacked[source_min[i, j], i, j]) / stacked[0, i, j] < 0.12):
                        mask[i, j] = 0
                elif source_max[i, j] == 1:  # Cas 2.2
                    if ((stacked[1, i, j] - stacked[source_min[i, j], i, j]) / stacked[1, i, j] < 0.04 or
                        bands[6][i, j] / bands[2][i, j] > 0.46):
                        mask[i, j] = 0
                    if bands[2][i, j] < bands[0][i, j] and stacked[1, i, j] > 0.3:
                        if ((stacked[1, i, j] - stacked[source_min[i, j], i, j]) / stacked[1, i, j] < 0.12):
                            mask[i, j] = 0
                elif source_max[i, j] == 2:  # Cas 2.3
                    if ((bands[2][i, j] - bands[1][i, j] > 0.001) or
                        (stacked[2, i, j] - stacked[source_min[i, j], i, j]) / stacked[2, i, j] < 0.05):
                        mask[i, j] = 0
                    if stacked[2, i, j] > (-1.107 * (bands[5][i, j] / bands[0][i, j]) + 0.748):
                        mask[i, j] = 0
                else:
                    raise ValueError("Erreur dans le traitement des indices.")
    return mask