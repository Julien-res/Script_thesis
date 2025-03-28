import os
import sys
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
from load_datas import load_data, load_srf_data, simulate_band
from scipy.stats import ttest_ind, linregress
import seaborn as sns
import matplotlib.colors as mcolors

def remove_nan_values(poc, results, classif=None):
    mask = ~np.isnan(results)
    if classif is not None:
        return poc[mask], results[mask], classif[mask]
    return poc[mask], results[mask]

def remove_outliers(poc, results, classif, outlier_threshold=1.5):
    q1 = np.percentile(results, 25)
    q3 = np.percentile(results, 75)
    iqr = q3 - q1
    lower_bound = q1 - outlier_threshold * iqr
    upper_bound = q3 + outlier_threshold * iqr
    mask = (results >= lower_bound) & (results <= upper_bound)
    if classif is not None:
        return poc[mask], results[mask], classif[mask]
    return poc[mask], results[mask]

def plot_scatter(ax, poc, results, classif=None):
    if classif is not None:
        # Definition of a discrete colormap
        cmap = mcolors.ListedColormap(plt.cm.viridis(np.linspace(0, 1, 6)))  
        norm = mcolors.BoundaryNorm(boundaries=np.arange(-0.5, 6.5, 1), ncolors=6)  

        scatter = ax.scatter(poc, results, c=classif, cmap=cmap, norm=norm)
        cbar = plt.colorbar(scatter, ax=ax)

        # Set the ticks and labels of the colorbar
        cbar.set_ticks(np.arange(6) - 0.5)
        cbar.set_ticklabels([str(i) for i in range(6)])  # Labels corrects
    else:
        sns.scatterplot(x=poc, y=results, ax=ax, label='Data points')

def plot_identity_line(ax, poc, results, logscale=True):
    min_val = min(poc.min(), results.min())
    max_val = max(poc.max(), results.max())
    x = np.logspace(np.log10(min_val), np.log10(max_val), 100) if logscale else np.linspace(min_val, max_val, 100)
    
    if logscale:
        extended_x = np.logspace(np.log10(min_val) - 1, np.log10(max_val) + 1, 100)
        sns.lineplot(x=extended_x, y=extended_x, ax=ax, color='black', linewidth=0.5)
        sns.lineplot(x=extended_x, y=2*extended_x, ax=ax, color='black', linestyle='--', linewidth=0.2)
        sns.lineplot(x=2*extended_x, y=extended_x, ax=ax, color='black', linestyle='--', linewidth=0.2)
    else:
        extended_x = np.linspace(min_val, max_val, 100)
        sns.lineplot(x=extended_x, y=extended_x, ax=ax, color='black', linewidth=0.5)
        sns.lineplot(x=extended_x, y=2*extended_x, ax=ax, color='black', linestyle='--', linewidth=0.2)
        sns.lineplot(x=2*extended_x, y=extended_x, ax=ax, color='black', linestyle='--', linewidth=0.2)

def calculate_log_symmetric_bias(poc, results):
    log_ratios = np.log10(results / poc)
    MdLQ = np.median(log_ratios)
    bias = 100 * np.sign(MdLQ) * (10 ** abs(MdLQ) - 1)
    return bias

def calculate_mdsr(poc, results):
    residuals = np.abs(results - poc)
    median_residual = np.median(residuals)
    mdsr = 100 * median_residual / np.median(poc)
    return mdsr

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
        sns.lineplot(x=poc_mask, y=predicted_log, ax=ax, color='r')
        slope_log, intercept_log, r_value, p_value, std_err = linregress(log_poc, log_results)
        ci_log = 1.96 * std_err
        ax.fill_between(poc_mask, 10 ** (log_predicted - ci_log), 10 ** (log_predicted + ci_log), color='red', alpha=0.1)
        ax.set_xscale('log')
        ax.set_yscale('log')
        r2_log = r2_score(log_results, log_predicted)
        rmsle_log = np.sqrt(mean_squared_error(log_results, log_predicted))
        sspb_log = calculate_log_symmetric_bias(poc_mask, results_mask)
        mdsr_log = calculate_mdsr(poc_mask, results_mask)
        _, p_value_log = ttest_ind(results_mask, poc_mask)
        slope_log = model_log.coef_[0]
        intercept_log = model_log.intercept_
        num_points_log = len(poc_mask)
        return r2_log, rmsle_log, sspb_log, mdsr_log, p_value_log, slope_log, intercept_log, num_points_log
    else:
        model_lin = LinearRegression()
        model_lin.fit(poc.values.reshape(-1, 1), results)
        predicted_lin = model_lin.predict(poc.values.reshape(-1, 1))
        sns.lineplot(x=poc, y=predicted_lin, ax=ax, color='r')
        slope_lin, intercept_lin, r_value, p_value, std_err = linregress(poc, results)
        ci_lin = 1.96 * std_err
        ax.fill_between(poc, predicted_lin - ci_lin, predicted_lin + ci_lin, color='red', alpha=0.1)
        r2_lin = r2_score(results, predicted_lin)
        rmsd_lin = np.sqrt(mean_squared_error(results, predicted_lin))
        mapd_lin = np.mean(np.abs((results - poc) / poc)) * 100
        sspb_lin = 100 * np.sum((poc - results) / ((poc + results) / 2)) / len(poc)
        mdsr_lin = calculate_mdsr(poc, results)
        _, p_value_lin = ttest_ind(results, poc)
        slope_lin = model_lin.coef_[0]
        intercept_lin = model_lin.intercept_
        num_points_lin = len(poc)
        return r2_lin, rmsd_lin, mapd_lin, sspb_lin, mdsr_lin, p_value_lin, slope_lin, intercept_lin, num_points_lin

def plot_results(poc, results, label, **kwargs):
    sns.set_theme(style="ticks")
    created_ax = False
    ax = kwargs.get('ax', None)
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
        created_ax = True
    classif = kwargs.get('classif', None)
    outl=kwargs.get('outlier',None)
    if classif is not None:
        poc, results, classif = remove_nan_values(poc, results, classif)
        if outl is not None:
            poc, results, classif = remove_outliers(poc, results, classif, outl)
        plot_scatter(ax, poc, results, classif)
    else:
        poc, results = remove_nan_values(poc, results)
        if kwargs.get('outlier',None) is not None:
            poc, results = remove_outliers(poc, results, outl)
        plot_scatter(ax, poc, results)
    plot_identity_line(ax, poc, results, kwargs.get('logscale', True))

    if kwargs.get('logscale', True):
        r2, rmsle, sspb, mdsr, p_value, slope, intercept, num_points = plot_regression(ax, poc, results, logscale=True)
        ax.text(0.05, 0.95, f'R² = {r2:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.92, f'RMSLE = {rmsle:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.89, f'SSPB = {sspb:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.86, f'MdSR = {mdsr:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.83, f't-test p-value = {p_value:.2e}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.80, f'y = {10 ** intercept:.2f} * x^{slope:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.77, f'Number of points = {num_points}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
    else:
        r2, rmsd, mapd, sspb, mdsr, p_value, slope, intercept, num_points = plot_regression(ax, poc, results, logscale=False)
        ax.text(0.05, 0.95, f'R² = {r2:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.92, f'RMSD = {rmsd:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.89, f'MAPD = {mapd:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.86, f'SSPB = {sspb:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.83, f'MdSR = {mdsr:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.80, f't-test p-value = {p_value:.2e}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.77, f'y = {slope:.2f}x + {intercept:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
        ax.text(0.05, 0.74, f'Number of points = {num_points}', transform=ax.transAxes, fontsize=12, verticalalignment='top')

    min_val = min(poc.min(), results.min())
    max_val = max(poc.max(), results.max())
    if kwargs.get('logscale', True):
        if min_val <= 0:
            min_val = min(poc[poc > 0].min(), results[results > 0].min())
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
        # legend = ax.legend(loc='lower right')
        # legend.get_frame().set_alpha(0.5)

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
        # if kwargs.get('sensor', None) == 'MERIS' or kwargs.get('sensor', None) == 'SEAWIFS':
        #     senso = 'MODIS'
        # elif kwargs.get('sensor', None) == 'S2A' or kwargs.get('sensor', None) == 'S2B':
        #     senso='MSI'
        # else:
        #     senso = kwargs.get('sensor', None)
        senso='MSI'
        sat='S2A'
        srf_data_c = load_srf_data(srf_path, sat)
        band_class = {band: simulate_band(datar, srf_data_c[band]['Values'],
                                            int(srf_data_c[band]['Wavelengths'][0]), 
                                            int(srf_data_c[band]['Wavelengths'].values[-1])) for band in SENSOR_BANDS[senso]}
        Rrs_class = np.array(list(band_class.values())).T
        classif = Chl_CONNECT(Rrs_class,method='logreg', sensor=senso,logRrsClassif=False,pTransform=False).Class

    def plot_mode(ax, mode=None):
        results = func(*[band_eq[band] for band in bands], mode=mode, **kwargs) if mode else func(*[band_eq[band] for band in bands], **kwargs)
        plot_results(poc=poc, results=results, label=func.__name__, ax=ax, classif=classif, **kwargs)
        if mode:
            ax.set_title(f'Mode: {mode}')
        else:
            ax.set_title(func.__name__ + ' algorithm using ' + kwargs.get('sensor', ''))
        ax.set_ylabel(r'POC ($\mu g.L^{-1}$) model')
        ax.set_xlabel(r'POC ($\mu g.L^{-1}$)')

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
        figure.savefig(save_path, dpi=500)
        print(f"Figure saved as {save_path}")
    else:
        plt.show()
        print("Figure displayed")
    