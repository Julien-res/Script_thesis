import os
import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.enums import Resampling
import re
from collections import Counter


def sum_masks(directory, output, substring):
    # Initialize matrices for each mask value
    mask_values = [0, 1, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    result_matrices = {value: None for value in mask_values}
    transform = None
    crs = None

    print(f"Processing files in directory: {directory} with substring: {substring}")

    # Iterate over all .tif files in the given directory
    for filename in os.listdir(directory):
        if filename.endswith(".tif") and substring in filename:
            filepath = os.path.join(directory, filename)
            print(f"Reading file: {filepath}")
            with rasterio.open(filepath) as src:
                mask = src.read(1)
                if transform is None:
                    transform = src.transform
                    crs = src.crs

                # Sum the mask values in the corresponding matrices
                for value in mask_values:
                    mask_value_matrix = (mask == value).astype(np.uint8)
                    if result_matrices[value] is None:
                        result_matrices[value] = mask_value_matrix
                    else:
                        result_matrices[value] += mask_value_matrix

    # Save the resulting matrices as images
    for value, matrix in result_matrices.items():
        if matrix is not None:
            output_path = os.path.join(output, f"result_mask_{substring}_{value}.tif")
            print(f"Saving result to: {output_path}")
            with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=matrix.shape[0],
                width=matrix.shape[1],
                count=1,
                dtype=np.uint8,
                crs=crs,
                transform=transform,
                compress='LZW'  # Apply lossless compression
            ) as dst:
                dst.write(matrix, 1)

directory = '/mnt/d/DATA/WiPE/TREATED'
output = "/mnt/c/Travail/Script/Script_thesis/7_Random_figures/WiPE_New_Mask_Test/Output"
# Retrieve all filenames ending in .tif in the "directory" folder
tif_files = [f for f in os.listdir(directory) if f.endswith('.tif')]

# Extract the parts of filenames following the regex pattern (T48PWQ)
pattern = re.compile(r'T\d{2}[A-Z]{3}')
matches = [pattern.search(f).group() for f in tif_files if pattern.search(f)]

# Count the number of times each name appears
counter = Counter(matches)
# Create a list with all the different names
unique_names = list(counter.keys())

print("Unique names and their counts:", counter)
for tiles in unique_names:
    sum_masks(directory, output, tiles)
