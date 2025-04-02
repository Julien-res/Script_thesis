import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns  # Import Seaborn
from scipy.stats import norm  # Import to fit a normal distribution

def plot_frequency_distribution(df, column_name):
    """
    Generates a frequency distribution plot for a given column of a DataFrame.
    The x-axis is in log scale, and the median is indicated on the plot.
    A density curve is added to check normality.
    A second x-axis is added for density.

    :param df: pandas DataFrame
    :param column_name: Name of the column for which to generate the plot
    :return: matplotlib.figure.Figure
    """
    if column_name not in df.columns:
        raise ValueError(f"The column '{column_name}' does not exist in the DataFrame.")
    
    # Extract data from the column and drop missing values
    data = df[column_name].dropna()

    # Calculate the median
    median_value = np.median(data)

    # Calculate the total number of values
    total_values = len(data)

    # Configure Seaborn style
    sns.set_theme(style="whitegrid")

    # Create the frequency plot
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Define bins in logarithmic scale
    min_data = data.min()
    max_data = data.max()
    padding_factor = 2  # Factor to add padding around the median
    log_min = np.log10(median_value) - padding_factor
    log_max = np.log10(median_value) + padding_factor
    bins = np.logspace(log_min, log_max, num=30)  # 30 bins in log scale

    # Histogram
    ax1.hist(data, bins=bins, edgecolor='black', log=False, density=False, alpha=0.6, label='Histogram')
    ax1.set_xscale('log')
    ax1.set_xlabel('POC Concentration '+"$\mu$g.L$^{-1}$ " + ' (log scale)', color='black')
    ax1.set_ylabel('Frequency', color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    # Add a vertical line for the median
    ax1.axvline(median_value, color='red', linestyle='--', label=f'Median: {median_value:.2f}')
    ax1.legend(loc='upper left')

    # Add a second axis for density
    ax2 = ax1.twinx()
    sns.kdeplot(data, ax=ax2, color='blue', label='KDE', linewidth=2)
    # Fit a normal distribution to the data in logarithmic scale
    log_data = np.log10(data)
    mean, std = norm.fit(log_data)
    x = np.logspace(log_min, log_max, 1000)
    log_x = np.log10(x)
    pdf = norm.pdf(log_x, mean, std)
    ax2.plot(x, pdf, color='orange', linestyle='--', label=f'Fitted Normal\n(µ={mean:.2f}, σ={std:.2f})')
    ax2.set_ylabel('Density', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.grid(False)

    # Add a legend for the second axis
    ax2.legend(loc='upper right')

    # Add labels and a title
    plt.title(f'Frequency and Density Plot of POC Concentration ($\mu$g.L$^{-1}$)\n'
              f'Total number of values: {total_values}, Bins: {len(bins)}')
    fig.tight_layout()

    # Return the figure
    return fig

def plot_frequency_distribution_with_coloring(df, column_name, color_column_name):
    """
    Generates a frequency distribution plot with coloring based on another column.
    The x-axis is in log scale, and the median is indicated on the plot.
    A density curve is added to check normality.
    A color bar is added to represent the mean of the coloring column per bin.

    :param df: pandas DataFrame
    :param column_name: Name of the column for which to generate the plot
    :param color_column_name: Name of the column used for coloring
    :return: matplotlib.figure.Figure
    """
    if column_name not in df.columns or color_column_name not in df.columns:
        raise ValueError(f"The columns '{column_name}' or '{color_column_name}' do not exist in the DataFrame.")
    
    data = df[[column_name, color_column_name]].dropna()
    median_value = np.median(data[column_name])
    total_values = len(data[column_name])
    
    sns.set(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    min_data, max_data = data[column_name].min(), data[column_name].max()
    padding_factor = 2  
    log_min, log_max = np.log10(median_value) - padding_factor, np.log10(median_value) + padding_factor
    bins = np.logspace(log_min, log_max, num=30)  
    
    bin_indices = np.digitize(data[column_name], bins)
    bin_means = [data[color_column_name][bin_indices == i].mean() if not data[color_column_name][bin_indices == i].empty else 0 for i in range(1, len(bins))]
    
    color_norm = plt.Normalize(vmin=min(bin_means), vmax=max(bin_means))
    colors = plt.cm.viridis(color_norm(bin_means))
    
    for i in range(len(bins) - 1):
        bin_data = data[column_name][(data[column_name] >= bins[i]) & (data[column_name] < bins[i + 1])]
        ax1.bar((bins[i] + bins[i + 1]) / 2, len(bin_data), width=(bins[i + 1] - bins[i]), color=colors[i], edgecolor='black', alpha=0.6)
    
    ax1.set_xscale('log')
    ax1.set_xlabel('POC Concentration '+"$\mu$g.L$^{-1}$ " + ' (log scale)', color='black')
    ax1.set_ylabel('Frequency', color='black')
    ax1.axvline(median_value, color='red', linestyle='--', label=f'Median: {median_value:.2f}')
    ax1.legend(loc='upper left')
    
    ax2 = ax1.twinx()
    sns.kdeplot(data[column_name], ax=ax2, color='blue', label='KDE', linewidth=2)
    log_data = np.log10(data[column_name])
    mean, std = norm.fit(log_data)
    x = np.logspace(log_min, log_max, 1000)
    pdf = norm.pdf(np.log10(x), mean, std)
    ax2.plot(x, pdf, color='orange', linestyle='--', label=f'Fitted Normal\n(µ={mean:.2f}, σ={std:.2f})')
    ax2.set_ylabel('Density', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.grid(False)
    # Add a legend for the second axis
    ax2.legend(loc='upper right')

    # Add a color bar
    cax = fig.add_axes([0.9, 0.2, 0.03, 0.6])  # Position of the color bar
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=color_norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cax)
    cbar.set_label(f'Mean of {color_column_name} per bin')
    
    fig.suptitle(f'Frequency and Density Plot of POC Concentration \nTotal number of values: {total_values}, Bins: {len(bins)}', y=0.95)
    fig.tight_layout(rect=[0, 0, 0.9, 1])  # Adjust to avoid overlap
    
    return fig
