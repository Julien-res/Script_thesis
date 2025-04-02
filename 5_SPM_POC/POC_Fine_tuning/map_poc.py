import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from matplotlib.colors import LogNorm
import numpy as np
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature

def plot_world_map(dataframe, lat_col, lon_col, var_col, title="World Map", region=None):
    """
    Plots a world map with points colored based on a variable, with an optional histogram below the map.

    Parameters:
        dataframe (pd.DataFrame): Input dataframe containing latitude, longitude, and variable data.
        lat_col (str): Name of the column containing latitude values.
        lon_col (str): Name of the column containing longitude values.
        var_col (str): Name of the column containing the variable to color the points.
        title (str): Title of the plot.
        region (str): Region to zoom into. Options: 'europe', 'usa', 'guyane', 'mekong'.
    """
    # Create a figure with two subplots: one for the map and one for the histogram
    fig = plt.figure(figsize=(12, 10))
    gs = fig.add_gridspec(2, 1, height_ratios=[4, 1], hspace=0.2)
    
    # Map subplot
    ax_map = fig.add_subplot(gs[0], projection=ccrs.PlateCarree())
    if region == 'europe':
        extent = [-12, 23, 35, 55]
    elif region == 'usa':
        extent = [-130, -60, 20, 55]
    elif region == 'guyane':
        extent = [-55, -49, 3, 7]
    elif region == 'mekongA':
        extent = [104, 110, 7, 13]
    elif region == 'mekongB':
        extent = [105, 108, 19, 21.5]
    else:
        extent = None

    if extent:
        ax_map.set_extent(extent, crs=ccrs.PlateCarree())
    else:
        ax_map.set_global()
    
    # Add features to the map
    ax_map.add_feature(cfeature.LAND, facecolor='gray')
    ax_map.add_feature(cfeature.BORDERS, edgecolor='white', linestyle=':')
    ax_map.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=0.5)
    
    if region is not None:
        ax_map.add_feature(cfeature.LAKES, edgecolor='blue', facecolor='lightblue')
        ax_map.add_feature(cfeature.RIVERS, edgecolor='blue', linewidth=0.2)
        ax_map.set_title(f"{title}\nRegion: {region.capitalize()}", fontsize=14)
    
    # Filter out non-positive values for LogNorm
    filtered_df = dataframe[dataframe[var_col] > 0]
    
    # Filter data based on map extent
    if extent:
        filtered_df = filtered_df[
            (filtered_df[lon_col] >= extent[0]) & (filtered_df[lon_col] <= extent[1]) &
            (filtered_df[lat_col] >= extent[2]) & (filtered_df[lat_col] <= extent[3])
        ]
    
    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        ax_map.text(0.5, 0.5, "No data available", transform=ax_map.transAxes,
                    ha='center', va='center', fontsize=16, color='red')
        ax_map.set_title(title, fontsize=16)
        ax_hist = fig.add_subplot(gs[1])
        ax_hist.text(0.5, 0.5, "No data available for histogram", transform=ax_hist.transAxes,
                     ha='center', va='center', fontsize=14, color='red')
        ax_hist.axis('off')
        plt.tight_layout()
        return fig, (ax_map, ax_hist)
    
    # Scatter plot of the data with LogNorm for color scale
    vmin = filtered_df[var_col].min()
    vmax = filtered_df[var_col].max()
    scatter = ax_map.scatter(
        filtered_df[lon_col], filtered_df[lat_col], 
        c=filtered_df[var_col], cmap='viridis', s=20, 
        norm=LogNorm(vmin=vmin, vmax=vmax), 
        transform=ccrs.PlateCarree(), alpha=0.7, zorder=3
    )
    
    # Add a colorbar
    cbar = plt.colorbar(scatter, ax=ax_map, orientation='vertical', shrink=0.7, pad=0.05)
    cbar.set_label(r"Concentration ($\mu$g.L$^{-1}$)")
    
    # Add a title
    ax_map.set_title(title, fontsize=16)
    
    # Histogram subplot
    median_value = np.median(filtered_df[var_col])
    padding_factor = 2
    log_min = np.log10(median_value) - padding_factor
    log_max = np.log10(median_value) + padding_factor
    bins = np.logspace(log_min, log_max, num=30)
    ax_hist = fig.add_subplot(gs[1])
    ax_hist.hist(filtered_df[var_col], bins=bins, color='blue', alpha=0.7)
    ax_hist.set_xscale('log')
    ax_hist.set_xlabel(r"Concentration ($\mu$g.L$^{-1}$)")
    ax_hist.set_ylabel("Frequency")
    ax_hist.set_title("Distribution of Data")

    plt.tight_layout()
    return fig, (ax_map, ax_hist)
