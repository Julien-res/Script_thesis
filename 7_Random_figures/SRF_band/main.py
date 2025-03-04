import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def wavelength_to_rgb(wavelength):
    """Convert a wavelength in nm to an RGB color."""
    gamma = 0.8
    intensity_max = 255

    def adjust(color, factor):
        return int(intensity_max * ((color * factor) ** gamma))

    if 380 <= wavelength <= 440:
        R, G, B = -(wavelength - 440) / 60, 0.0, 1.0
    elif 440 < wavelength <= 490:
        R, G, B = 0.0, (wavelength - 440) / 50, 1.0
    elif 490 < wavelength <= 510:
        R, G, B = 0.0, 1.0, -(wavelength - 510) / 20
    elif 510 < wavelength <= 580:
        R, G, B = (wavelength - 510) / 70, 1.0, 0.0
    elif 580 < wavelength <= 645:
        R, G, B = 1.0, -(wavelength - 645) / 65, 0.0
    elif 645 < wavelength <= 780:
        R, G, B = 1.0, 0.0, 0.0
    else:
        R, G, B = 0.0, 0.0, 0.0

    if 380 <= wavelength <= 420:
        factor = 0.3 + 0.7 * (wavelength - 380) / 40
    elif 420 < wavelength <= 645:
        factor = 1.0
    elif 645 < wavelength <= 780:
        factor = 0.3 + 0.7 * (780 - wavelength) / 135
    else:
        factor = 0.0

    R, G, B = adjust(R, factor), adjust(G, factor), adjust(B, factor)
    return (R / 255, G / 255, B / 255)

def get_srf_and_band_ranges(Srf_path, sensor_name, band_names=None):
    # Load the SRF data from the CSV file
    srf_data = pd.read_csv(os.path.join(Srf_path, f'SRF_{sensor_name}.csv'))
    # Set the wavelength column as the index for easier access
    srf_data.set_index('SR_WL', inplace=True)
    
    band_ranges = []
    if band_names is None:
        band_names = srf_data.columns.tolist()
    else:
        for band in band_names:
            if band in srf_data.columns:
                non_zero_data = srf_data[srf_data[band] != 0]
                if not non_zero_data.empty:
                    start_wavelength = non_zero_data.index.min()
                    end_wavelength = non_zero_data.index.max()
                    band_ranges.append([start_wavelength, end_wavelength])
    
    if not band_ranges:
        band_ranges = None
    
    return band_ranges

def plot_srf(srf_path, sensor_name, font=12, *highlight_bands):
    # Load the SRF data from the CSV file
    srf_data = pd.read_csv(os.path.join(srf_path, f'SRF_{sensor_name}.csv'))
    # Set the wavelength column as the index for easier access
    srf_data.set_index('SR_WL', inplace=True)
    # Set Seaborn style
    sns.set(style="ticks")
    # Create a new figure with a 1:2 ratio
    plt.figure(figsize=(20, 4))
    # Plot the SRF for the sensor
    band_names = []
    for column in srf_data.columns:
        # Filter out zero values
        non_zero_data = srf_data[srf_data[column] != 0]
        if not non_zero_data.empty:
            avg_wavelength = np.mean(non_zero_data.index.values)
            color = wavelength_to_rgb(avg_wavelength)
            plt.plot(non_zero_data.index, non_zero_data[column], color=color, linestyle='-')
            plt.fill_between(non_zero_data.index, non_zero_data[column], color=color, alpha=0.3)
            band_names.append((column, avg_wavelength, color))
    
    sns.despine()
    
    # Add labels and title
    plt.xlabel('Wavelength (nm)', fontsize=font+2)
    plt.ylabel('SRF', fontsize=font+2)
    plt.title(f'Spectral Response Function (SRF) for {sensor_name}', fontsize=font+4, pad=40)
    plt.grid()
    
    # Limit the x-axis to 1000 nm
    plt.xlim(400, 1000)
    # Set y-axis limits
    plt.ylim(0, None)
    # Set major and minor ticks
    plt.xticks(range(400, 1001, 100))  # Major ticks every 100 nm
    plt.minorticks_on()  # Enable minor ticks
    plt.tick_params(axis='x', which='minor', length=5)  # Customize minor ticks
    plt.tick_params(axis='x', which='major', length=10, labelsize=font, width=2)  # Customize major ticks
    
    # Customize the x-tick labels to make the hundreds bold and add labels for the fifties
    ax = plt.gca()
    ax.set_xticks(range(400, 1001, 10), minor=True)  # Minor ticks every 10 nm
    ax.set_xticks(range(400, 1001, 50), minor=False)  # Major ticks every 50 nm
    
    # Set labels for major ticks (hundreds) and minor ticks (fifties)
    ax.set_xticklabels([f'{int(tick)}' if tick % 100 == 0 else '' for tick in range(400, 1001, 50)], fontsize=font, fontweight='bold')
    ax.set_xticklabels([f'{int(tick)}' if tick % 50 == 0 and tick % 100 != 0 else '' for tick in range(400, 1001, 10)], minor=True, fontsize=font)

    # Highlight specified bands
    for bands in highlight_bands:
        for band in bands:
            if isinstance(band, list) and len(band) == 2:
                plt.axvspan(band[0], band[1], color='grey', alpha=0.3)
            elif isinstance(band, int):
                plt.axvspan(band - 5, band + 5, color='grey', alpha=0.3)
    
    # Combine close band names
    combined_band_names = []
    current_combination = [band_names[0]]
    for i in range(1, len(band_names)):
        if abs(band_names[i][1] - band_names[i-1][1]) < 20:  # If bands are within 10 nm
            current_combination.append(band_names[i])
        else:
            combined_band_names.append(current_combination)
            current_combination = [band_names[i]]
    combined_band_names.append(current_combination)
    
    # Add a text box for each combined band below the title
    for combination in combined_band_names:
        avg_wavelength = np.mean([band[1] for band in combination])
        band_name = ' - '.join([band[0] for band in combination])
        color = combination[0][2]
        if 400 <= avg_wavelength <= 1000:
            plt.text(avg_wavelength, 1.05, f'{band_name}', fontsize=font, color='black', ha='center', va='bottom', bbox=dict(facecolor=color, alpha=0.2, edgecolor='none'), transform=ax.get_xaxis_transform())
    
    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # Show the plot
    return plt.gcf()

SRF_PATH = "/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo/SRF"

Tran19 = {'dicname':'Tran19','Sensor': 'MERIS', 'Bands': ['B3', 'B4', 'B5', 'B7']}
Le18BG = {'dicname':'Le18BG','Sensor': 'MERIS', 'Bands': ['B2', 'B3', 'B5', 'B7']}
Le18CI = {'dicname':'Le18CI','Sensor': 'MERIS', 'Bands': ['B3', 'B5', 'B7']}
Stramski08 = {'dicname':'Stramski08','Sensor': 'SEAWIFS', 'Bands': ['B2', 'B3', 'B4', 'B5']}
Hu16 = {'dicname':'Hu16','Sensor': 'SEAWIFS', 'Bands': ['B2', 'B3', 'B4', 'B5']}

# Example usage

output_dir = os.path.dirname(__file__)

output_dir_all = os.path.join(output_dir, "All_bands")
os.makedirs(output_dir_all, exist_ok=True)

for sensor in ['MERIS', 'S2A', 'S2B', 'SEAWIFS', 'OLCIA', 'OLCIB']:
    fig = plot_srf(SRF_PATH, sensor, 12)
    output_path = os.path.join(output_dir_all, f"{sensor}_all_bands.png")
    fig.savefig(output_path)
    plt.close(fig)

for algo in [Tran19, Le18BG, Le18CI, Stramski08, Hu16]:
    band_ranges = get_srf_and_band_ranges(SRF_PATH, algo['Sensor'], algo['Bands'])
    algo_dir = os.path.join(output_dir, "Func", algo['dicname'])
    os.makedirs(algo_dir, exist_ok=True)
    for sensor in [algo['Sensor'], 'S2A', 'S2B']:
        fig = plot_srf(SRF_PATH, sensor, 12, band_ranges)
        output_path = os.path.join(algo_dir, f"{sensor}.png")
        fig.savefig(output_path)
        plt.close(fig)
