import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from load_datas import load_data, load_srf_data, simulate_band

def plot_results(poc, results, label, ax=None, outlier_threshold=1.5, log_scale=True):
    created_ax = False
    if ax is None:
        fig, ax = plt.subplots()
        created_ax = True

    # Remove NaN values
    mask = ~np.isnan(results)
    results = results[mask]
    poc = poc[mask]

    # Remove outliers
    q1 = np.percentile(results, 25)
    q3 = np.percentile(results, 75)
    iqr = q3 - q1
    lower_bound = q1 - outlier_threshold * iqr
    upper_bound = q3 + outlier_threshold * iqr
    outlier_mask = (results >= lower_bound) & (results <= upper_bound)
    results = results[outlier_mask]
    poc = poc[outlier_mask]

    # Plot the results
    ax.plot(poc, results, 'o', label='Data points')

    # Plot the x=y line
    x = np.linspace(min(poc), max(poc), 100)
    ax.plot(x, x, 'r--', alpha=0.5, label='x=y')

    if log_scale:
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
    if log_scale:
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
        ax.set_ylabel(label)
        legend = ax.legend()
        legend.get_frame().set_alpha(0.5)  # Set the legend background to be slightly transparent

    return ax

def process_and_plot(data, srf_path, sensor, bands, func, ax=None, outlier=1.5, logscale=True, **kwargs):
    datar = load_data(data)
    band_eq = {}
    srf_data = load_srf_data(srf_path, sensor)
    for band in bands:
        bandr = srf_data[band]
        bandr['Wavelengths'] = bandr['Wavelengths'].round().astype(int)
        bandr = bandr.groupby('Wavelengths', as_index=False).mean()
        band_eq[band] = simulate_band(datar, bandr['Values'], int(bandr['Wavelengths'][0]), int(bandr['Wavelengths'].values[-1]))
    results = func(*[band_eq[band] for band in bands], **kwargs)
    poc = datar['POC_microg_L']
    plot_results(poc, results, func.__name__, ax, outlier, logscale)

# Define a function to process and plot for different modes
def process_and_plot_modes(data, srf_path, sensor, bands, func, modes, title, outlier, logscale):
    figure, axis = plt.subplots(2, 2, figsize=(12, 12))  # Set the figure size to ensure rectangular plots
    for i, (ax, mode) in enumerate(zip(axis.flatten(), modes)):
        process_and_plot(
            data=data,
            srf_path=srf_path,
            sensor=sensor,
            bands=bands,
            func=func,
            ax=ax,
            mode=mode,
            outlier=outlier,
            logscale=logscale
        )
        ax.set_title(f'Mode: {mode}')
        
        # Remove Y labels for plots in the second column
        if i % 2 == 1:
            ax.set_yticklabels([])
        
        # Remove X labels for plots in the first row
        if i < 2:
            ax.set_xticklabels([])
    
    # Add global legend below the figures
    handles, labels = axis[0, 0].get_legend_handles_labels()
    figure.legend(handles, labels, loc='lower center', ncol=3)
    # Add global title
    figure.suptitle(title)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

