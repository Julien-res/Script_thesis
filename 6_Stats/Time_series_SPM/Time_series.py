import os
import re
import rasterio
import pandas as pd
from rasterio.transform import rowcol
from pyproj import Transformer
import numpy as np

def extract_time_series(lat, lon, cell_name, directory):
    """
    Extracts a time series from georeferenced .tiff files at a given lat/lon and cell name.

    :param lat: Latitude of the point
    :param lon: Longitude of the point
    :param cell_name: Cell name to filter files (e.g., "48PUV")
    :param directory: Directory containing the .tiff files
    :return: A pandas DataFrame with dates and values
    """
    time_series = []

    # Regular expression to extract date and match cell name
    pattern = re.compile(rf"({cell_name}).*?(\d{{8}}).*\.tif$")

    for file_name in os.listdir(directory):
        match = pattern.search(file_name)
        if match:
            date_str = match.group(2)
            date = pd.to_datetime(date_str, format='%Y%m%d')

            file_path = os.path.join(directory, file_name)
            with rasterio.open(file_path) as src:
                # Print the bounds of the image
                bounds = src.bounds
                print(f"File: {file_name}, Bounds: {bounds}")

                # Convert lat/lon to the CRS of the raster (EPSG:32648)
                transformer = Transformer.from_crs("EPSG:4326", "EPSG:32648", always_xy=True)
                x, y = transformer.transform(lon, lat)
                print(f"Transformed coordinates: ({x}, {y})")

                # Convert projected coordinates to row/col
                row, col = rowcol(src.transform, x, y)
                try:
                    # Extract a 3x3 window around the target pixel (including the pixel itself)
                    window = src.read(1)[max(0, row-1):row+2, max(0, col-1):col+2]
                    valid_values = window[window > 0]  # Filter out null or zero values

                    if len(valid_values) >= 3:  # Check if at least 3 valid pixels are available
                        value = np.mean(valid_values)  # Compute the mean of valid pixels
                    else:
                        value = None  # Discard the data if less than 3 valid pixels
                        print(f"Insufficient valid pixels around ({lat}, {lon}) for file {file_name}")
                except IndexError:
                    value = None  # Handle case where coordinates are out of bounds
                    print(f"Coordinates ({lat}, {lon}) out of bounds for file {file_name}")
            # Append the date and value to the time series list
            time_series.append({'date': date, 'value': value})

    # Create a DataFrame and sort by date
    df = pd.DataFrame(time_series)
    if not df.empty:
        df = df.dropna().sort_values(by='date').reset_index(drop=True)
    return df

# Example usage
if __name__ == "__main__":
    lat = 11.5977  # Replace with your latitude
    lon = 104.9412   # Replace with your longitude
    cell_name = "48PVT"  # Replace with your cell name
    directory = "/mnt/d/DATA/SPM_Polymer_Han/"  # Replace with the directory containing your .tiff files

    time_series_df = extract_time_series(lat, lon, cell_name, directory)
    print(time_series_df)
    # Save to CSV if needed
    time_series_df.to_csv("time_series.csv", index=False)

    import matplotlib.pyplot as plt

    # Remove outliers using the IQR method
    if not time_series_df.empty:
        Q1 = time_series_df['value'].quantile(0.25)
        Q3 = time_series_df['value'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Filter the DataFrame to exclude outliers and values greater than 100
        filtered_df = time_series_df[
            (time_series_df['value'] >= lower_bound) & 
            (time_series_df['value'] <= upper_bound) & 
            (time_series_df['value'] <= 100)
        ]

        # Plot the filtered time series
        if not filtered_df.empty:
            plt.figure(figsize=(10, 6))
            plt.plot(filtered_df['date'], filtered_df['value'], marker='o', linestyle='-', color='b')
            plt.title('Time Series Plot (Outliers Removed)')
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            print("No data available to plot after removing outliers and values greater than 100.")
    else:
        print("No data available to plot.")