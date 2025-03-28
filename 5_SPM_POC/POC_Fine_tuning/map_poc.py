import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LogNorm  # Import LogNorm

def plot_world_map(dataframe, lat_col, lon_col, var_col, title="World Map", region=None):
    """
    Plots a world map with points colored based on a variable, with optional zoom on specific regions.

    Parameters:
        dataframe (pd.DataFrame): Input dataframe containing latitude, longitude, and variable data.
        lat_col (str): Name of the column containing latitude values.
        lon_col (str): Name of the column containing longitude values.
        var_col (str): Name of the column containing the variable to color the points.
        title (str): Title of the plot.
        region (str): Region to zoom into. Options: 'europe', 'usa', 'guyane', 'mekong'.
    """
    # Create a figure and axis with Cartopy projection
    # Set region-specific extents
    if region == 'europe':
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([-12, 23, 35, 55], crs=ccrs.PlateCarree())
    elif region == 'usa':
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([-130, -60, 20, 55], crs=ccrs.PlateCarree())
    elif region == 'guyane':
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([-55, -50, 2, 6], crs=ccrs.PlateCarree())
    elif region == 'mekongA':
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([104, 110, 7, 13], crs=ccrs.PlateCarree())
    elif region == 'mekongB':
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([105, 108, 19, 21.5], crs=ccrs.PlateCarree())
    else:
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Add features to the map
    ax.add_feature(cfeature.LAND, facecolor='gray')
    ax.add_feature(cfeature.BORDERS, edgecolor='white', linestyle=':')
    
    # Only set global extent if no specific region is provided
    if region is None:
        ax.set_global()
    
    # Filter out non-positive values for LogNorm
    filtered_df = dataframe[dataframe[var_col] > 0]
    
    # Scatter plot of the data with LogNorm for color scale
    scatter = ax.scatter(
        filtered_df[lon_col], filtered_df[lat_col], 
        c=filtered_df[var_col], cmap='viridis', s=20, 
        norm=LogNorm(vmin=filtered_df[var_col].min(), vmax=filtered_df[var_col].max()),  # Use LogNorm
        transform=ccrs.PlateCarree(), alpha=0.7
    )
    
    # Add a colorbar
    cbar = plt.colorbar(scatter, ax=ax, orientation='vertical', shrink=0.7, pad=0.05)
    cbar.set_label(r"Concentration ($\mu$g.L$^{-1}$)")
    
    
    # Add a title
    ax.set_title(title, fontsize=16)
    plt.tight_layout()
    # Return the figure and axis for further customization or saving
    return fig, ax
