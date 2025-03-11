import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr
from load_datas import load_data, load_srf_data, simulate_band
from plot_result import remove_nan_values


def calculate_statistics(observed, predicted):
    """Calculate statistics for Taylor diagram."""
    stddev = np.std(predicted)
    correlation = pearsonr(observed, predicted)[0]
    centered_rms = np.sqrt(np.mean((predicted - observed) ** 2))
    return stddev, correlation, centered_rms

def taylor_diagram(data, srf_path, bands, func, **kwargs):
    """Create a Taylor diagram."""
    datar = load_data(data)
    srf_data = load_srf_data(srf_path, kwargs.get('sensor', None))
    band_eq = {band: simulate_band(datar, srf_data[band]['Values'],
                                    int(srf_data[band]['Wavelengths'][0]), 
                                    int(srf_data[band]['Wavelengths'].values[-1])) for band in bands}
    poc = datar['POC_microg_L']
    results = func(*[band_eq[band] for band in bands], **kwargs)
    poc, results = remove_nan_values(poc, results)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, polar=True)
    # Reference point
    ref_stddev = np.std(poc)
    ax.plot([0], [ref_stddev], 'k*', markersize=12, label='Reference')

    for i, predicted in enumerate(results):
        stddev, correlation, _ = calculate_statistics(poc, results)
        angle = np.arccos(correlation)
        ax.plot(angle, stddev, 'o', label='Test {}'.format(i+1))

    # Add grid and labels
    ax.set_xlabel('Standard Deviation')
    ax.set_ylabel('Standard Deviation')
    ax.grid(True)
    ax.legend(loc='upper right')
    ax.set_title(title)
    return ax