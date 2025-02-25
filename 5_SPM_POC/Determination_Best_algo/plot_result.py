import numpy as np
import sys
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from load_datas import load_data, load_srf_data, simulate_band

def plot_results(poc, results, label, **kwargs):
    """
    Plots the results of an algorithm against POC (Particulate Organic Carbon).

    Parameters:
    - poc: array-like, POC values
    - results: array-like, results from the algorithm
    - label: str, label for the y-axis
    - kwargs: additional keyword arguments for customization
    """
    created_ax = False
    ax = kwargs.get('ax', None)
    if ax is None:
        fig, ax = plt.subplots()
        created_ax = True

    # Remove NaN values
    mask = ~np.isnan(results)
    results = results[mask]
    poc = poc[mask]

    # Remove outliers using the IQR method
    q1 = np.percentile(results, 25)
    q3 = np.percentile(results, 75)
    iqr = q3 - q1
    outlier_threshold = kwargs.get('outlier', 1.5)
    lower_bound = q1 - outlier_threshold * iqr
    upper_bound = q3 + outlier_threshold * iqr
    outlier_mask = (results >= lower_bound) & (results <= upper_bound)
    results = results[outlier_mask]
    poc = poc[outlier_mask]

    # Plot the results
    classif = kwargs.get('classif', None)
    if classif is not None:
        classif = np.array(classif)[mask][outlier_mask]
        scatter = ax.scatter(poc, results, c=classif, cmap='viridis', label='Data points')
        plt.colorbar(scatter, ax=ax, label='Classification')
    else:
        ax.plot(poc, results, 'o', label='Data points')

    # Plot the x=y line
    x = np.linspace(min(poc), max(poc), 100)
    ax.plot(x, x, 'r--', alpha=0.5, label='x=y')

    if kwargs.get('logscale', True):
        # Remove zero or negative values for log transformation
        positive_mask = (poc > 0) & (results > 0)
        poc = poc[positive_mask]
        results = results[positive_mask]

        # Calculate and plot the linear regression line in log-log space
        log_poc = np.log10(poc)
        log_results = np.log10(results)
        model = LinearRegression()
        model.fit(log_poc.values.reshape(-1, 1), log_results)
        log_predicted = model.predict(log_poc.values.reshape(-1, 1))
        predicted = 10**log_predicted
        ax.plot(poc, predicted, 'b-', label='Linear fit')

        # Calculate R² in log-log space
        r2 = r2_score(log_results, log_predicted)
        ax.text(0.05, 0.95, f'R² = {r2:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Set logarithmic scale for x and y axes
        ax.set_xscale('log')
        ax.set_yscale('log')
    else:
        # Calculate and plot the linear regression line in linear space
        model = LinearRegression()
        model.fit(poc.values.reshape(-1, 1), results)
        predicted = model.predict(poc.values.reshape(-1, 1))
        ax.plot(poc, predicted, 'b-', label='Linear fit')

        # Calculate R² in linear space
        r2 = r2_score(poc, results)
        ax.text(0.05, 0.95, f'R² = {r2:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

    # Set equal scaling for x and y axes with some padding
    min_val = min(poc.min(), results.min())
    max_val = max(poc.max(), results.max())
    if kwargs.get('logscale', True):
        padding = 0.1 * (np.log10(max_val) - np.log10(min_val))
        ax.set_xlim([10**(np.log10(min_val) - padding), 10**(np.log10(max_val) + padding)])
        ax.set_ylim([10**(np.log10(min_val) - padding), 10**(np.log10(max_val) + padding)])
    else:
        padding = 0.1 * (max_val - min_val)
        ax.set_xlim([min_val - padding, max_val + padding])
        ax.set_ylim([min_val - padding, max_val + padding])

    if created_ax:
        # Add labels and legend
        ax.set_xlabel('POC (microg/L)')
        sensor = kwargs.get('sensor', None)
        if sensor is not None:
            ax.set_ylabel(label + ' on ' + sensor)
        else:
            ax.set_ylabel(label)
        legend = ax.legend()
        legend.get_frame().set_alpha(0.5)  # Set the legend background to be slightly transparent

    return ax

def process_and_plot(data, srf_path, bands, func, **kwargs):
    """
    Processes the data and plots the results of the given function.

    Parameters:
    - data: path to the data file
    - srf_path: path to the SRF (Spectral Response Function) data
    - bands: list of bands to simulate
    - func: function to apply to the data
    - kwargs: additional keyword arguments for customization
    """
    datar = load_data(data)
    band_eq = {}
    srf_data = load_srf_data(srf_path, kwargs.get('sensor', None))
    for band in bands:  # Simulate bands
        bandr = srf_data[band]
        bandr['Wavelengths'] = bandr['Wavelengths'].round().astype(int)
        bandr = bandr.groupby('Wavelengths', as_index=False).mean()
        band_eq[band] = simulate_band(datar, bandr['Values'], int(bandr['Wavelengths'][0]), int(bandr['Wavelengths'].values[-1]))
    poc = datar['POC_microg_L']
    if 'pathmeta' in kwargs:  # Manh T Duy classification to color points if called
        sys.path.append(kwargs.get('pathmeta', None))
        from Dict import SENSOR_BANDS
        from common.Chl_CONNECT import Chl_CONNECT
        if kwargs.get('sensor', None) == 'MERIS':
            senso = 'MODIS'
        else:
            senso = kwargs.get('sensor', None)
        bandmeta = SENSOR_BANDS[senso]
        band_class = {}
        Rrs_class = []
        for band in bandmeta:
            bandr = srf_data[band]
            bandr['Wavelengths'] = bandr['Wavelengths'].round().astype(int)
            bandr = bandr.groupby('Wavelengths', as_index=False).mean()
            band_class[band] = simulate_band(datar, bandr['Values'], int(bandr['Wavelengths'][0]), int(bandr['Wavelengths'].values[-1]))
            Rrs_class.append(band_class[band])
        Rrs_class = np.array(Rrs_class).T
        Chl_NN_mc = Chl_CONNECT(Rrs_class,senso)
        classif = Chl_NN_mc.Class
    if 'modes' in kwargs:
        figure, axis = plt.subplots(2, 2, figsize=(12, 12))
        for i, (ax, mode) in enumerate(zip(axis.flatten(), kwargs.pop('modes'))):
            results = func(*[band_eq[band] for band in bands], mode=mode, **kwargs)
            if 'pathmeta' in kwargs:
                plot_results(poc=poc, results=results, label=func.__name__, ax=ax, mode=mode, classif=classif, **kwargs)
            else:
                plot_results(poc=poc, results=results, label=func.__name__, ax=ax, mode=mode, **kwargs)
            ax.set_title(f'Mode: {mode}')
            if i % 2 == 1:
                ax.set_yticklabels([])
            if i < 2:
                ax.set_xticklabels([])
        handles, labels = axis[0, 0].get_legend_handles_labels()
        figure.legend(handles, labels, loc='lower center', ncol=3)
        figure.suptitle(func.__name__ + ' algorithm for different modes', fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
    else:
        results = func(*[band_eq[band] for band in bands], **kwargs)
        if 'pathmeta' in kwargs:
            plot_results(poc=poc, results=results, label=func.__name__, classif=classif, **kwargs)
        else:
            plot_results(poc=poc, results=results, label=func.__name__, **kwargs)
