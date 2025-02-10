import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# path = '/mnt/c/Users/Julien/Documents/GitHub/Script_thesis/5_SPM_POC/Determination_Best_algo'
path='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo'
os.chdir(path)
# from dictband import bandsS2A, bandsS2B, bandsMeris, Meris_to_S2
from dictband import Meris_to_S2
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        exit(1)


def load_srf_data(srf_path):
    srf = load_data(srf_path)
    bands = srf.columns[1:]  # Skip the first column which is 'SR_WL'
    srf_data = {}
    for band in bands:
        non_zero_values = srf[srf[band] != 0][band].values
        wavelengths = srf[srf[band] != 0]['SR_WL'].values
        srf_data[band] = pd.DataFrame({
            'Wavelengths': wavelengths,
            'Values': non_zero_values
        })
    return srf_data


def simulate_band(data, srf_band, start, end):
    startr = str(start)
    endr = str(end)
    if start > end:
        raise ValueError("The start wavelength must be lower than the end wavelength.")
    if start < 310:
        raise ValueError("The start wavelength must be greater than 310 nm.")
    if end > 950:
        raise ValueError("The end wavelength must be lower than 950 nm.")
    if startr not in data.columns or endr not in data.columns:
        print('{} not in data'.format(startr))
        print('{} not in data'.format(endr))
        raise ValueError("The start or end wavelength is not in the provided data.")
    data_band = data.loc[:, startr:endr]
    srf_band = srf_band.values  # Use srf_band as it is
    weighted_sum = np.zeros(data_band.shape[0])
    for i in range(data_band.shape[1]):
        weighted_sum += data_band.iloc[:, i] * srf_band[i]
    return weighted_sum / np.sum(srf_band)


def Le18(Rrs490, Rrs555, Rrs670):
    Ci = Rrs555 - (Rrs490 + ((555 - 490) / (555 - 490)) * (Rrs670 - Rrs490))
    return np.where(Ci <= -0.0005, 10**(185.72*Ci + 1.97), 10**(485.19*Ci + 2.1))


def Stramski08(Rrs443, Rrs490, Rrs510, Rrs555):
    # Stramski 2008 Maximum band ratio
    if Rrs555 is None:
        raise ValueError("Rrs555 cannot be None")
    band_values = {'Rrs443': Rrs443, 'Rrs490': Rrs490, 'Rrs510': Rrs510}
    band = max((value for value in band_values.values() if value is not None), default=None)
    if band is None:
        raise ValueError("At least one of Rrs443, Rrs490, or Rrs510 must be provided")
    if band == Rrs443:
        return 203.2 * (Rrs443 / Rrs555) ** (-1.034)
    elif band == Rrs490:
        return 308.3 * (Rrs490 / Rrs555) ** (-1.639)
    elif band == Rrs510:
        return 423.0 * (Rrs510 / Rrs555) ** (-3.075)

def plot_results(poc, results, label):
    # Remove NaN values
    mask = ~np.isnan(results)
    results = results[mask]
    poc = poc[mask]

    # Remove outliers
    q1 = np.percentile(results, 25)
    q3 = np.percentile(results, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outlier_mask = (results >= lower_bound) & (results <= upper_bound)
    results = results[outlier_mask]
    poc = poc[outlier_mask]

    # Plot the results
    plt.plot(poc, results, 'o', label='Data points')

    # Plot the x=y line
    x = np.linspace(min(poc), max(poc), 100)
    plt.plot(x, x, 'r--', alpha=0.5, label='x=y')

    # Calculate and plot the linear regression line
    model = LinearRegression()
    model.fit(poc.values.reshape(-1, 1), results)
    predicted = model.predict(poc.values.reshape(-1, 1))
    plt.plot(poc, predicted, 'b-', label='Linear fit')

    # Calculate R²
    r2 = r2_score(poc, results)
    plt.text(0.05, 0.95, f'R² = {r2:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')

    # Add labels and legend
    plt.xlabel('POC (microg/L)')
    plt.ylabel(label)
    plt.legend()
    plt.show()

def process_and_plot(data, srf_path, bands, poc_column, func, label):
    band_eq = {}
    srf_data = load_srf_data(srf_path)
    for band in bands:
        bandr = srf_data[band]
        bandr['Wavelengths'] = bandr['Wavelengths'].round().astype(int)
        bandr = bandr.groupby('Wavelengths', as_index=False).mean()
        band_eq[band] = simulate_band(data, bandr['Values'], int(bandr['Wavelengths'][0]), int(bandr['Wavelengths'].values[-1]))
    results = func(*[band_eq[band] for band in bands])
    poc = data[poc_column]
    plot_results(poc, results, label)


# Load data and SRF
file_path = os.path.join(path, 'Data_RRS_In_Situ.csv')
srf_meris_path = os.path.join(path, 'SRF/SRF_MERIS.csv')
srf_s2a_path = os.path.join(path, 'SRF/SRF_S2A.csv')
data = load_data(file_path)

# # Le2018
# band_eq = {}
# Meris = load_srf_data(srf_meris_path)
# for band in ['B3', 'B5', 'B7']:
#     bandr = Meris[band]
#     bandr['Wavelengths'] = bandr['Wavelengths'].round().astype(int)
#     bandr = bandr.groupby('Wavelengths', as_index=False).mean()
#     band_eq[band] = simulate_band(data, bandr['Values'], int(bandr['Wavelengths'][0]), int(bandr['Wavelengths'].values[-1]))
# # Calculate the results using the Le function
# results_le = Le18(band_eq['B3'], band_eq['B5'], band_eq['B7'])


poc = data['POC_microg_L']
# Plot the results
process_and_plot(data, srf_meris_path, ['B3', 'B5', 'B7'], 'POC_microg_L', Le18, 'Le Results')


# Example usage for Le18 function


