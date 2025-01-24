import numpy as np
import matplotlib.pyplot as plt
import sys
import os
os.chdir('/mnt/c/Travail/Script/Script_Thesis/2_WiPE/WiPE_personal/Python_Dev/') # inutile 
sys.path.insert(1, '/home/julien/') # Afin de pouvoir charger esa_snappy, il faut charger son fichier source
from rayleigh_correction import apply_rayleigh_correction
from applyWiPE import applyWiPE
os.chdir('/home/julien/')
import numpy as np
from matplotlib.colors import ListedColormap
#=============================================================================
corrected_bands=np.zeros((7,10980,10980))
bands = ["B2","B3","B4","B7","B10","B11","B12"]
for band in bands:
    corrected_bands[bands.index(band)]=apply_rayleigh_correction(input_path="/mnt/c/Travail/Script/S2A_MSIL1C_20231216T032131_N0510_R118_T48PXQ_20231216T050649.SAFE",target_res=10,band=band,resolution_method="other")
bands=corrected_bands
corrected_bands=None

# Create custom colormap with black for zero values
colors = plt.cm.plasma(np.linspace(0, 1, 256))
custom_cmap = ListedColormap(colors)
custom_cmap.set_under('black')
custom_cmap.set_bad('black')
# Display the matrix as image with custom colormap
plt.imshow(bands[0], cmap=custom_cmap, vmin=0.000001)
plt.colorbar()
plt.title('Matrice en Image avec Colorbar')
plt.show()