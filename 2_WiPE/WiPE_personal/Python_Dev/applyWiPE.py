import numpy as np

def applyWiPE(bands):
    """Applies WiPE calculations.
    Takes as input bands 2,3,4,7,10,11,12 in list format
                           0,1,2,3,4,5,6"""

    # Verify that all bands have the same dimensions
    for i in range(len(bands) - 1):
        if bands[i].shape != bands[i + 1].shape:
            raise ValueError("All bands must have the same dimensions.")
    
    # Initialize the mask
    mask = np.ones_like(bands[2], dtype=np.uint16)
    mask[np.isnan(bands[0]) | np.isnan(bands[1]) | np.isnan(bands[2]) | np.isnan(bands[3]) | (bands[3] == 0)] = 0

    # Step 1: Filtering with conditions
    print("Step 1")
    mask[(bands[5] / bands[2] > 0.69) & (mask == 1)] = 10  # Condition 1.1
    mask[(bands[5] > 0.035) & (mask == 1)] = 20         # Condition 1.2
    mask[(bands[0] < 0.0065) | (bands[4] > 0.01072) & (mask == 1)] = 30  # Condition 1.3

    # Step 2: Band normalization
    print("Step 2 - Normalization")
    max_bands = [band / np.nanmax(band) for band in bands[:3]]
    stacked = np.stack(max_bands, axis=0)
    max_bands = None
    
    # Find source of maximum and minimum values
    source_max = np.argmax(stacked, axis=0)
    source_min = np.argmin(stacked, axis=0)

    # Iterate over each pixel to apply additional conditions
    rows, cols = bands[4].shape
    for i in range(rows):
        for j in range(cols):
            if mask[i, j] == 1:
                if source_max[i, j] == 0:  # Case 2.1
                    if stacked[0, i, j] > (-2.93 * (bands[5][i, j] / bands[3][i, j]) + 2):
                        mask[i, j] = 40
                    if (bands[6][i, j] / bands[2][i, j] > 0.28 or
                        (stacked[0, i, j] - stacked[source_min[i, j], i, j]) / stacked[0, i, j] < 0.12):
                        mask[i, j] = 50
                elif source_max[i, j] == 1:  # Case 2.2
                    if ((stacked[1, i, j] - stacked[source_min[i, j], i, j]) / stacked[1, i, j] < 0.04 or
                        bands[6][i, j] / bands[2][i, j] > 0.46):
                        mask[i, j] = 60
                    if bands[2][i, j] < bands[0][i, j] and stacked[1, i, j] > 0.3:
                        if ((stacked[1, i, j] - stacked[source_min[i, j], i, j]) / stacked[1, i, j] < 0.12):
                            mask[i, j] = 70
                elif source_max[i, j] == 2:  # Case 2.3
                    if ((bands[2][i, j] - bands[1][i, j] > 0.001) or
                        (stacked[2, i, j] - stacked[source_min[i, j], i, j]) / stacked[2, i, j] < 0.05):
                        mask[i, j] = 80
                    if stacked[2, i, j] > (-1.107 * (bands[5][i, j] / bands[0][i, j]) + 0.748):
                        mask[i, j] = 90
                else:
                    raise ValueError("Error in index processing.")
    return mask