import pandas as pd
from geopy.distance import geodesic
import geopandas as gpd
from shapely.geometry import Point

# Function to classify the distance from the coast
def classify_distance(lat, lon, coast_gdf):
    point = Point(lon, lat)
    min_distance = coast_gdf.distance(point).min()
    if min_distance > 20:
        return 'Ocean'
    elif min_distance <= 20 and min_distance >= 0:
        return 'Coast'
    else:
        return 'Inland'

# Load the CSV file
input_file = r"/mnt/c/Travail/ODATIS/DATA_POC_PON_SPM.csv"
data = pd.read_csv(input_file)

# Load the shapefile containing the coastlines
coast_shapefile = r"/mnt/c/Travail/ODATIS/ne_10m_coastline/ne_10m_coastline.shp"
coast_gdf = gpd.read_file(coast_shapefile)

# Apply the classification to each row
data['Distance_Class'] = data.apply(lambda row: classify_distance(row['Lat'], row['Lon'], coast_gdf), axis=1)

# Save the updated dataframe to a new CSV file
output_file = '/mnt/c/Travail/ODATIS/output_data.csv'
data.to_csv(output_file, index=False)