import os
import sys
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
from load_datas import load_data, load_srf_data, simulate_band
from scipy.stats import ttest_ind, linregress
import seaborn as sns

def remove_nan_values(poc, results):
    mask = ~np.isnan(results)
    return poc[mask], results[mask]

def remove_outliers(poc, results, outlier_threshold=1.5):
    q1 = np.percentile(results, 25)
    q3 = np.percentile(results, 75)
    iqr = q3 - q1
    lower_bound = q1 - outlier_threshold * iqr
    upper_bound = q3 + outlier_threshold * iqr
    mask = (results >= lower_bound) & (results <= upper_bound)
    return poc[mask], results[mask]

def plot_scatter(ax, poc, results, classif=None):
    if classif is not None:
        scatter = ax.scatter(poc, results, c=classif, cmap='viridis', label='Data points')
        plt.colorbar(scatter, ax=ax, label='Classification')
    else:
        sns.scatterplot(x=poc, y=results, ax=ax, label='Data points')

def plot_identity_line(ax, poc, results, logscale=True, ci=0.95):
    min_val = min(poc.min(), results.min())
    max_val = max(poc.max(), results.max())
    x = np.logspace(np.log10(min_val), np.log10(max_val), 100) if logscale else np.linspace(min_val, max_val, 100)
    if logscale:
        extended_x = np.logspace(np.log10(min_val) - 1, np.log10(max_val) + 1, 100)
        ax.plot(extended_x, 10 ** (np.log10(extended_x) + 1), color='black', linestyle='--', alpha=0.5, linewidth=0.5)
        ax.plot(10 ** (np.log10(extended_x) + 1), extended_x, color='black', linestyle='--', alpha=0.5, linewidth=0.5)
        sns.lineplot(x=extended_x, y=extended_x, ax=ax, color='black', linewidth=0.5)
    else:
        extended_x = np.linspace(min_val, max_val, 100)
        sns.lineplot(x=extended_x, y=extended_x, ax=ax, color='black', linewidth=0.5)
        ax.plot(extended_x, extended_x + (max_val - min_val) * 0.1, color='black', linestyle='--', alpha=0.5, linewidth=0.5)
        ax.plot(extended_x + (max_val - min_val) * 0.1, extended_x, color='black', linestyle='--', alpha=0.5, linewidth=0.5)

def plot_regression(ax, poc, results, logscale=True):
    if logscale:
        positive_mask = (poc > 0) & (results > 0)
        poc_mask = poc[positive_mask]
        results_mask = results[positive_mask]
        log_poc = np.log10(poc_mask)
        log_results = np.log10(results_mask)
        model_log = LinearRegression()
        model_log.fit(log_poc.values.reshape(-1, 1), log_results)
        log_predicted = model_log.predict(log_poc.values.reshape(-1, 1))
        predicted_log = 10 ** log_predicted
        sns.lineplot(x=poc_mask, y=predicted_log, ax=ax, label='Linear fit (log-log)', color='g')
        slope_log, intercept_log, r_value, p_value, std_err = linregress(log_poc, log_results)
        ci_log = 1.96 * std_err
        ax.fill_between(poc_mask, 10 ** (log_predicted - ci_log), 10 ** (log_predicted + ci_log), color='red', alpha=0.1)
        ax.set_xscale('log')
        ax.set_yscale('log')
        r2_log = r2_score(log_results, log_predicted)
        rmsd_log = np.sqrt(mean_squared_error(results_mask, poc_mask))
        mlae_log = np.mean(np.abs((log_predicted - log_poc) / log_poc)) * 100
        _, p_value_log = ttest_ind(results_mask, poc_mask)
        slope_log = model_log.coef_[0]
        intercept_log = model_log.intercept_
        num_points_log = len(poc_mask)
        return r2_log, rmsd_log, mlae_log, p_value_log, slope_log, intercept_log, num_points_log
    else:
        model_lin = LinearRegression()
        model_lin.fit(poc.values.reshape(-1, 1), results)
        predicted_lin = model_lin.predict(poc.values.reshape(-1, 1))
        sns.lineplot(x=poc, y=predicted_lin, ax=ax, label='Linear fit (linear)', color='g')
        slope_lin, intercept_lin, r_value, p_value, std_err = linregress(poc, results)
        ci_lin = 1.96 * std_err
        ax.fill_between(poc, predicted_lin - ci_lin, predicted_lin + ci_lin, color='red', alpha=0.1)
        r2_lin = r2_score(results, predicted_lin)
        rmsd_lin = np.sqrt(mean_squared_error(results, predicted_lin))
        mapd_lin = np.mean(np.abs((results - poc) / poc)) * 100
        _, p_value_lin = ttest_ind(results, poc)
        slope_lin = model_lin.coef_[0]
        intercept_lin = model_lin.intercept_
        num_points_lin = len(poc)
        return r2_lin, rmsd_lin, mapd_lin, p_value_lin, slope_lin, intercept_lin, num_points_lin
    
def plot_results(poc, results, label, **kwargs):
    sns.set_theme(style="ticks")
    created_ax = False
    ax = kwargs.get('ax', None)
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
        created_ax = True

    poc, results = remove_nan_values(poc, results)
    poc, results = remove_outliers(poc, results, kwargs.get('outlier', 1.5))
    plot_scatter(ax, poc, results, kwargs.get('classif', None))
    plot_identity_line(ax, poc, results, kwargs.get('logscale', True), kwargs.get('ci', 0.95))

    if kwargs.get('logscale', True):
        r2, rmsd, mlae, p_value, slope, intercept, num_points = plot_regression(ax, poc, results, logscale=True)
        ax.text(0.05, 0.95, f'R² = {r2:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.92, f'RMSD = {rmsd:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.89, f'MLAE = {mlae:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.86, f't-test p-value = {p_value:.2e}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.83, f'y = {10 ** intercept:.2f} * x^{slope:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.80, f'Number of points = {num_points}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
    else:
        r2, rmsd, mapd, p_value, slope, intercept, num_points = plot_regression(ax, poc, results, logscale=False)
        ax.text(0.05, 0.95, f'R² = {r2:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.92, f'RMSD = {rmsd:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.89, f'MAPD = {mapd:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.86, f't-test p-value = {p_value:.2e}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.83, f'y = {slope:.2f}x + {intercept:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.80, f'Number of points = {num_points}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

    min_val = min(poc.min(), results.min())
    max_val = max(poc.max(), results.max())
    if kwargs.get('logscale', True):
        padding = 0.1 * (np.log10(max_val) - np.log10(min_val))
        ax.set_xlim([10 ** (np.log10(min_val) - padding), 10 ** (np.log10(max_val) + padding)])
        ax.set_ylim([10 ** (np.log10(min_val) - padding), 10 ** (np.log10(max_val) + padding)])
    else:
        padding = 0.1 * (max_val - min_val)
        ax.set_xlim([0, max_val + padding])
        ax.set_ylim([0, max_val + padding])

    if created_ax:
        ax.set_ylabel('POC (microg/L) model')
        ax.set_xlabel('POC (microg/L)')
        sensor = kwargs.get('sensor', None)
        if sensor is not None:
            ax.set_title(label + ' on ' + sensor)
        else:
            ax.set_title(label)
        legend = ax.legend(loc='lower right')
        legend.get_frame().set_alpha(0.5)

    ax.grid(True, which='both', linestyle='--', linewidth=0.3, color='gray', alpha=0.7)  # Adjusted linewidth
    sns.despine(ax=ax)

    return ax


def process_and_plot(data, srf_path, bands, func, **kwargs):
    datar = load_data(data)
    srf_data = load_srf_data(srf_path, kwargs.get('sensor', None))
    band_eq = {band: simulate_band(datar, srf_data[band]['Values'],
                                    int(srf_data[band]['Wavelengths'][0]), 
                                    int(srf_data[band]['Wavelengths'].values[-1])) for band in bands}
    poc = datar['POC_microg_L']

    classif = None
    if 'pathmeta' in kwargs:
        sys.path.append(kwargs.get('pathmeta', None))
        from Dict import SENSOR_BANDS
        from common.Chl_CONNECT import Chl_CONNECT
        senso = 'MODIS' if kwargs.get('sensor', None) == 'MERIS' else kwargs.get('sensor', None)
        band_class = {band: simulate_band(datar, srf_data[band]['Values'],
                                            int(srf_data[band]['Wavelengths'][0]), 
                                            int(srf_data[band]['Wavelengths'].values[-1])) for band in SENSOR_BANDS[senso]}
        Rrs_class = np.array(list(band_class.values())).T
        Chl_NN_mc = Chl_CONNECT(Rrs_class, senso)
        classif = Chl_NN_mc.Class

    def plot_mode(ax, mode=None):
        results = func(*[band_eq[band] for band in bands], mode=mode, **kwargs) if mode else func(*[band_eq[band] for band in bands], **kwargs)
        plot_results(poc=poc, results=results, label=func.__name__, ax=ax, classif=classif, **kwargs)
        if mode:
            ax.set_title(f'Mode: {mode}')
        else:
            ax.set_title(func.__name__ + ' algorithm using ' + kwargs.get('sensor', ''))
        ax.set_ylabel('POC (microg/L) model')
        ax.set_xlabel('POC (microg/L)')

    if 'modes' in kwargs:
        figure, axis = plt.subplots(2, 2, figsize=(12, 12))
        for i, (ax, mode) in enumerate(zip(axis.flatten(), kwargs.pop('modes'))):
            plot_mode(ax, mode)
            if i % 2 == 1:
                ax.set_ylabel('')
            if i < 2:
                ax.set_xlabel('')
        handles, labels = axis[0, 0].get_legend_handles_labels()
        figure.legend(handles, labels, loc='lower center', ncol=3)
        figure.suptitle(func.__name__ + ' algorithm for different modes using ' + kwargs.get('sensor', ''), fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    else:
        figure, ax = plt.subplots(figsize=(6, 6))
        plot_mode(ax)
        plt.tight_layout()
    save_result = kwargs.get('save_result', None)
    if save_result:
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, save_result)
        figure.savefig(save_path)
        print(f"Figure saved as {save_path}")
    else:
        plt.show()
        print("Figure displayed")
