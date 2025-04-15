def plot_results_Band_ratio_outlier(Y, X, **kwargs):
    # Import necessary libraries
    import os
    import sys
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score, mean_squared_error
    import matplotlib.pyplot as plt
    from scipy.stats import ttest_ind, linregress
    import seaborn as sns
    from statsmodels.api import OLS, add_constant
    import matplotlib.colors as mcolors

    # Set seaborn theme for plots
    sns.set_theme(style="ticks")
    ax = kwargs.get('ax', None)  # Get the axis object if provided
    outliers = kwargs.get('remove_outlier', False)  # Check if outliers should be removed
    print(outliers)
    df = Y  # Copy the input dataframe
    Y = Y['POC_µg_L']  # Extract the target variable

    classif = kwargs.get('classif', None)  # Get classification data if provided
    mask = ~np.isnan(X) & ~np.isnan(Y)  # Mask to filter out NaN values
    if classif is not None:
        mask &= ~np.isnan(classif)  # Include classification mask if applicable
        classif = classif[mask]
    X = X[mask]
    Y = Y[mask]
    df = df[mask]

    # Create a new plot if no axis is provided
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))

    # Plot data points with classification if provided
    if classif is not None:
        cmap = mcolors.ListedColormap(plt.cm.viridis(np.linspace(0, 1, 6)))
        norm = mcolors.BoundaryNorm(boundaries=np.arange(-0.5, 6.5, 1), ncolors=6)
        scatter = ax.scatter(X, Y, c=classif, cmap=cmap, norm=norm)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_ticks(np.arange(6) - 0.5)
        cbar.set_ticklabels([str(i) for i in range(6)])
    else:
        sns.scatterplot(x=X, y=Y, ax=ax, label='Data points')

    # Filter positive values for log transformation
    positive_mask = (X > 0) & (Y > 0)
    X = X[positive_mask]
    Y = Y[positive_mask]
    df = df[positive_mask]

    # Perform log transformation
    log_X = np.log10(X)
    log_Y = np.log10(Y)

    # Fit a linear regression model on log-transformed data
    model_log = LinearRegression()
    model_log.fit(log_X.values.reshape(-1, 1), log_Y)
    log_predicted = model_log.predict(log_X.values.reshape(-1, 1))
    predicted_log = 10 ** log_predicted

    # Calculate residuals and identify outliers
    residuals_log = np.abs(log_Y - log_predicted)
    threshold_log = kwargs.get('outlier_threshold', 2.5 * np.std(residuals_log))  # Default threshold is 2.5 standard deviations
    outlier_indices = Y.index[residuals_log > threshold_log]

    # Handle outliers based on the 'remove_outlier' flag
    if outliers:
        Y = Y[~Y.index.isin(outlier_indices)]
        X = X[~X.index.isin(outlier_indices)]
        if classif is not None:
            classif = classif[~classif.index.isin(outlier_indices)]
    else:
        # Calculate statistics without outliers
        X_no_outliers = X[~X.index.isin(outlier_indices)]
        Y_no_outliers = Y[~Y.index.isin(outlier_indices)]
        log_X_no_outliers = np.log10(X_no_outliers)
        log_Y_no_outliers = np.log10(Y_no_outliers)
        model_no_outliers = LinearRegression()
        model_no_outliers.fit(log_X_no_outliers.values.reshape(-1, 1), log_Y_no_outliers)
        log_predicted_no_outliers = model_no_outliers.predict(log_X_no_outliers.values.reshape(-1, 1))
        r2_no_outliers = r2_score(log_Y_no_outliers, log_predicted_no_outliers)
        rmsle_no_outliers = np.sqrt(mean_squared_error(log_Y_no_outliers, log_predicted_no_outliers))
        slope_no_outliers = model_no_outliers.coef_[0]
        intercept_no_outliers = model_no_outliers.intercept_

    # Filter positive values again for further processing
    df = df.loc[outlier_indices]
    positive_mask = (X > 0) & (Y > 0)
    X = X[positive_mask]
    Y = Y[positive_mask]
    log_X = np.log10(X)
    log_Y = np.log10(Y)

    # Refit the model on log-transformed data
    model_log = LinearRegression()
    model_log.fit(log_X.values.reshape(-1, 1), log_Y)
    log_predicted = model_log.predict(log_X.values.reshape(-1, 1))
    predicted_log = 10 ** log_predicted

    # Calculate regression statistics
    slope_log, intercept_log, r_value, p_value, std_err = linregress(log_X, log_Y)
    ci_log = 1.96 * std_err

    # Plot regression line with outliers
    sns.lineplot(x=X, y=predicted_log, ax=ax, color='darkblue', label='Regression with outliers')
    sorted_indices = np.argsort(X)
    sorted_X = X.iloc[sorted_indices]
    sorted_lower_bound = 10 ** (log_predicted[sorted_indices] - ci_log)
    sorted_upper_bound = 10 ** (log_predicted[sorted_indices] + ci_log)
    ax.fill_between(sorted_X, sorted_lower_bound, sorted_upper_bound, color='darkblue', alpha=0.2)

    # Plot regression line without outliers if applicable
    if not outliers:
        ci_log_no_outliers = 1.96 * std_err
        sns.lineplot(x=X_no_outliers, y=10 ** log_predicted_no_outliers, ax=ax, color='darkred', label='Regression without outliers')
        sorted_indices = np.argsort(X_no_outliers)
        sorted_X_no_outliers = X_no_outliers.iloc[sorted_indices]
        sorted_lower_bound = 10 ** (log_predicted_no_outliers[sorted_indices] - ci_log_no_outliers)
        sorted_upper_bound = 10 ** (log_predicted_no_outliers[sorted_indices] + ci_log_no_outliers)
        ax.fill_between(sorted_X_no_outliers, sorted_lower_bound, sorted_upper_bound, color='darkred', alpha=0.2)

    # Set log scale for axes
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Calculate additional statistics
    r2_log = r2_score(log_Y, log_predicted)
    rmsle_log = np.sqrt(mean_squared_error(log_Y, log_predicted))
    log_ratios = np.log10(Y / X)
    MdLQ = np.median(log_ratios)
    sspb_log = 100 * np.sign(MdLQ) * (10 ** abs(MdLQ) - 1)
    residuals = np.abs(Y - X)
    median_residual = np.median(residuals)
    mdsr_log = 100 * median_residual / np.median(X)
    _, p_value_log = ttest_ind(Y, X)
    slope_log = model_log.coef_[0]
    intercept_log = model_log.intercept_
    num_points_log = len(X)

    # Add text annotations to the plot
    if outliers:
        ax.text(0.05, 0.95, f'R² = {r2_log:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='k')
        ax.text(0.05, 0.92, f'RMSLE = {rmsle_log:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='k')
        ax.text(0.05, 0.89, f'SSPB = {sspb_log:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='k')
        ax.text(0.05, 0.86, f'MdSR = {mdsr_log:.2f}%', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='k')
        ax.text(0.05, 0.83, f't-test p-value = {p_value_log:.2e}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='k')
        ax.text(0.05, 0.80, f'y = {10 ** intercept_log:.2f} * x^{slope_log:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='k')
        ax.text(0.05, 0.77, f'Number of points = {num_points_log}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='k')
    else:
        ax.text(0.05, 0.95, f'Number of points = {num_points_log}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='k')
        ax.text(0.05, 0.92, f'Number of outliers = {len(df)}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='darkred')
        ax.text(0.05, 0.89, f'R² = {r2_log:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='darkblue')
        ax.text(0.05, 0.86, f'R² = {r2_no_outliers:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='darkred')
        ax.text(0.05, 0.83, f'RMSLE = {rmsle_log:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='darkblue')
        ax.text(0.05, 0.80, f'RMSLE = {rmsle_no_outliers:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='darkred')
        ax.text(0.05, 0.77, f'y = {10 ** intercept_log:.2f} × xⁿ ({slope_log:.2f})', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='darkblue')
        ax.text(0.05, 0.74, f'y = {10 ** intercept_no_outliers:.2f} × xⁿ ({slope_no_outliers:.2f})', transform=ax.transAxes, fontsize=12, verticalalignment='top', color='darkred')

    # Highlight outliers on the plot
    if 'outlier_indices' in locals() and len(outlier_indices) > 0 and not outliers:
        ax.scatter(X[outlier_indices], Y[outlier_indices], color='red', label='Outliers', zorder=2)

    # Set axis limits with padding
    min_val_x = np.nanmin(X[np.isfinite(X)])
    max_val_x = np.nanmax(X[np.isfinite(X)])
    min_val_y = np.nanmin(Y[np.isfinite(Y)])
    max_val_y = np.nanmax(Y[np.isfinite(Y)])

    if not np.isfinite(min_val_x) or not np.isfinite(max_val_x) or not np.isfinite(min_val_y) or not np.isfinite(max_val_y):
        raise ValueError("Invalid axis limits: min_val or max_val is NaN or Inf.")

    if min_val_x <= 0:
        min_val_x = np.nanmin(X[X > 0])
    if min_val_y <= 0:
        min_val_y = np.nanmin(Y[Y > 0])
    padding_x = 0.1 * (np.log10(max_val_x) - np.log10(min_val_x))
    padding_y = 0.1 * (np.log10(max_val_y) - np.log10(min_val_y))
    ax.set_xlim([10 ** (np.log10(min_val_x) - padding_x), 10 ** (np.log10(max_val_x) + padding_x)])
    ax.set_ylim([10 ** (np.log10(min_val_y) - padding_y), 10 ** (np.log10(max_val_y) + padding_y)])

    # Set axis labels
    if kwargs.get('labelx', None) is not None:
        ax.set_xlabel(kwargs['labelx'])
    else:
        ax.set_xlabel('Band Ratio')
    if kwargs.get('labely', None) is not None:
        ax.set_ylabel(kwargs['labely'])
    else:
        ax.set_ylabel('POC (microg/L)')

    # Set plot title if sensor information is provided
    sensor = kwargs.get('sensor', None)
    if sensor is not None:
        ax.set_title(kwargs.get('title', None))

    # Customize tick parameters and grid
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.grid(True, which='both', linestyle='--', linewidth=0.3, color='gray', alpha=0.7)
    sns.despine(ax=ax)

    # Return the axis object and the dataframe of outliers
    if not outliers:
        return ax, df, intercept_log, slope_log,intercept_no_outliers, slope_no_outliers
    else:
        return ax, df, intercept_log, slope_log, None, None
