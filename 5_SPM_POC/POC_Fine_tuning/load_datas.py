import os
import sys
import pandas as pd
import numpy as np

def load_data(file_path):
    try:
        data = pd.read_csv(file_path,low_memory=False)
        return data
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        sys.exit(1)

def load_srf_data(srf_path, sensor):
    add = 'SRF/SRF_{}.csv'.format(sensor)
    srf = load_data(os.path.join(srf_path, add))
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
    indices_used = data_band.index.tolist()
    return weighted_sum / np.sum(srf_band), list(indices_used)
