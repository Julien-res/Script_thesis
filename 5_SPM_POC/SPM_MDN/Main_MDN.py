import os
import sys
import rasterio
from netCDF4 import Dataset
from rasterio.transform import from_bounds
from rasterio.enums import Compression

os.chdir('/mnt/c/Travail/')
sys.path.append('/mnt/c/Travail/')
from MDN import image_estimates, get_sensor_bands

sensor = 'MSI'

# Charger les données depuis le fichier NetCDF
nc_file = "/mnt/d/TEST/SPM_HAN/L1C_T48PUV_A014773_20200104T034232_polymer20m.nc"
with Dataset(nc_file, mode='r') as nc:
    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]

kwargs = {'product': 'tss'}
TSS, idxs = image_estimates(nc_file, sensor=sensor, **kwargs)

# Calculer le transform à partir des latitudes et longitudes
min_lon, max_lon = lons.min(), lons.max()
min_lat, max_lat = lats.min(), lats.max()
transform = from_bounds(min_lon, min_lat, max_lon, max_lat, TSS.shape[1], TSS.shape[0])
crs = "EPSG:4326"  # CRS correspondant aux latitudes/longitudes

# Exporter en .tif avec compression lossless
output_path = "/mnt/d/TEST/SPM_HAN/TSS_output.tif"
with rasterio.open(
    output_path,
    'w',
    driver='GTiff',
    height=TSS.shape[0],
    width=TSS.shape[1],
    count=1,
    dtype=TSS.dtype,
    crs=crs,
    transform=transform,
    compress='LZW'  # Compression sans perte
) as dst:
    dst.write(TSS[:, :, 0], 1)

print(f"Fichier TSS exporté avec succès : {output_path}")
