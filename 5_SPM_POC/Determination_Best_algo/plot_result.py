import numpy as np
import sys
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
from load_datas import load_data, load_srf_data, simulate_band
from scipy.stats import ttest_ind
import seaborn as sns

def plot_results(poc, results, label, **kwargs):
    """
    Plots the results of an algorithm against POC (Particulate Organic Carbon).

    Parameters:
    - poc: array-like, POC values
    - results: array-like, results from the algorithm
    - label: str, label for the y-axis
    - kwargs: additional keyword arguments for customization
    """
    sns.set_theme(style="ticks")
    created_ax = False
    ax = kwargs.get('ax', None)
    if ax is None:
        fig, ax = plt.subplots(figsize=(6,6))
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
        sns.scatterplot(x=poc, y=results, ax=ax, label='Data points')

    # Plot the x=y line
    min_val = min(poc.min(), results.min())
    max_val = max(poc.max(), results.max())
    x = np.logspace(np.log10(min_val), np.log10(max_val), 100) if kwargs.get('logscale', True) else np.linspace(min_val, max_val, 100)
    sns.lineplot(x=x, y=x, ax=ax, color='red', linestyle='--', alpha=0.5, label='x=y')
    if kwargs.get('logscale', True):
        # Remove zero or negative values for log transformation
        positive_mask = (poc > 0) & (results > 0)
        poc_mask = poc[positive_mask]
        results_mask = results[positive_mask]

        # Calculate and plot the linear regression line in log-log space
        log_poc = np.log10(poc_mask)
        log_results = np.log10(results_mask)
        model_log = LinearRegression()
        model_log.fit(log_poc.values.reshape(-1, 1), log_results)
        log_predicted = model_log.predict(log_poc.values.reshape(-1, 1))
        predicted_log = 10**log_predicted
        sns.lineplot(x=poc_mask, y=predicted_log, ax=ax, label='Linear fit (log-log)', color='g')

        # Set logarithmic scale for x and y axes
        ax.set_xscale('log')
        ax.set_yscale('log')

        # Calculate R² in log space
        r2_log = r2_score(log_results, log_predicted)
        ax.text(0.05, 0.95, f'R² = {r2_log:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Calculate RMSD in log space
        rmsd_log = np.sqrt(mean_squared_error(results_mask, poc_mask))
        ax.text(0.05, 0.90, f'RMSD = {rmsd_log:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Calculate MLAE (Mean Absolute Percentage Deviation) in linear space
        mlae_log = np.mean(np.abs((log_predicted - log_poc) / log_poc)) * 100
        ax.text(0.05, 0.85, f'MLAE = {mlae_log:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top')


        # Perform Student's t-test in log space
        _, p_value_log = ttest_ind(results_mask, poc_mask)
        ax.text(0.05, 0.80, f't-test p-value = {p_value_log:.2e}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Display linear regression equation in log space
        slope_log = model_log.coef_[0]
        intercept_log = model_log.intercept_
        ax.text(0.05, 0.75, f'y = {10**intercept_log:.2f} * x^{slope_log:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Display number of points in log space
        num_points_log = len(poc_mask)
        ax.text(0.05, 0.70, f'Number of points = {num_points_log}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
    else:
        # Calculate and plot the linear regression line in linear space
        model_lin = LinearRegression()
        model_lin.fit(poc.values.reshape(-1, 1), results)
        predicted_lin = model_lin.predict(poc.values.reshape(-1, 1))
        sns.lineplot(x=poc, y=predicted_lin, ax=ax, label='Linear fit (linear)', color='g')

        # Calculate R² in linear space
        r2_lin = r2_score(results, predicted_lin)
        ax.text(0.05, 0.95, f'R² = {r2_lin:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Calculate RMSD in linear space
        rmsd_lin = np.sqrt(mean_squared_error(results, predicted_lin))
        ax.text(0.05, 0.90, f'RMSD = {rmsd_lin:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Calculate MAPD (Mean Absolute Percentage Deviation) in linear space
        mapd_lin = np.mean(np.abs((results - poc) / poc)) * 100
        ax.text(0.05, 0.85, f'MAPD = {mapd_lin:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Perform Student's t-test in linear space
        t_stat_lin, p_value_lin = ttest_ind(results, poc)
        ax.text(0.05, 0.80, f't-test p-value = {p_value_lin:.2e}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Display linear regression equation in linear space
        slope_lin = model_lin.coef_[0]
        intercept_lin = model_lin.intercept_
        ax.text(0.05, 0.75, f'y = {slope_lin:.2f}x + {intercept_lin:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

        # Display number of points in linear space
        num_points_lin = len(poc)
        ax.text(0.05, 0.70, f'Number of points = {num_points_lin}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

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
        legend = ax.legend(loc='lower right')
        legend.get_frame().set_alpha(0.5)  # Set the legend background to be slightly transparent

    # Remove top and right spines
    sns.despine(ax=ax)

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
