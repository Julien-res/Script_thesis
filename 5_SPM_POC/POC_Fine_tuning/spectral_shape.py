import numpy as np
import pandas as pd  # Required for DataFrame operations
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm  # Removed unused Normalize import

def plot_rrs_spectra_interactive(df, variable):
    import plotly.graph_objects as go  # Ensure Plotly is installed: pip install plotly
    """
    Plots interactive Rrs spectra from a dataframe and colors them based on a variable.

    Parameters:
    - df: pandas DataFrame, where each row contains Rrs spectra and a column for the variable.
    - variable: str, the name of the column to use for coloring the spectra.
    """
    if variable not in df.columns:
        raise ValueError(f"The variable '{variable}' is not in the dataframe.")

    # Extract wavelengths (assuming Rrs columns are named like "Rrs665", "Rrs666", ...)
    rrs_columns = [col for col in df.columns if col.isdigit() and col != variable]
    wavelengths = [float(col) for col in rrs_columns]

    # Normalize the variable for coloring
    norm = plt.Normalize(df[variable].min(), df[variable].max())
    cmap = plt.cm.viridis

    # Create the interactive plot
    fig = go.Figure()

    for _, row in df.iterrows():
        color = cmap(norm(row[variable]))
        hex_color = f"rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, {color[3]})"
        fig.add_trace(go.Scatter(
            x=wavelengths,
            y=row[rrs_columns],
            mode='lines',
            line=dict(width=2, color=hex_color),
            hoverinfo='text',
            text=f"{variable}: {row[variable]}"
        ))

    # Add colorbar for the variable with log scale
    fig.update_layout(
        title=f"Rrs Spectra Colored by {variable} (Rows: {len(df)})",
        xaxis_title="Wavelength (nm)",
        yaxis_title="Rrs",
        template="plotly",
        hovermode="closest",
        coloraxis_colorbar=dict(
            title=variable,
            tickvals=np.logspace(np.log10(df[variable].min()), np.log10(df[variable].max()), num=5),
            ticktext=[f"{val:.2e}" for val in np.logspace(np.log10(df[variable].min()), np.log10(df[variable].max()), num=5)]
        )
    )

    # Set log scale for color axis
    fig.update_traces(marker=dict(colorbar=dict(tickmode="array", tickvals=np.logspace(np.log10(df[variable].min()), np.log10(df[variable].max()), num=5))))
    fig.show()


def plot_rrs_spectra(df, variable):
    """
    Plots Rrs spectra from a dataframe and colors them based on a variable.

    Parameters:
    - df: pandas DataFrame, where each row contains Rrs spectra and a column for the variable.
    - variable: str, the name of the column to use for coloring the spectra.
    """
    if variable not in df.columns:
        raise ValueError(f"The variable '{variable}' is not in the dataframe.")

    # Extract wavelengths (assuming Rrs columns are named like "Rrs665", "Rrs666", ...)
    rrs_columns = [col for col in df.columns if col.isdigit() and col != variable]
    wavelengths = [float(col) for col in rrs_columns]

    # Normalize the variable for coloring with log scale and limit to 10^1 and 10^4
    norm = LogNorm(vmin=10**1, vmax=10**4)
    cmap = plt.cm.plasma

    # Create the figure with a white background for the plot area
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('white')  # Set the figure background to white
    ax.set_facecolor('black')  # Set the plot area background to black

    for _, row in df.iterrows():
        color = cmap(norm(row[variable]))
        ax.plot(wavelengths, row[rrs_columns].values, color=color, alpha=0.7)  # Increase transparency

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Add a colorbar
    cbar = plt.colorbar(sm, ax=ax)
    cbar.ax.set_yscale('log')  # Set colorbar scale to log
    cbar.ax.tick_params(colors='black')  # Set tick colors to black
    cbar.set_label("POC Concentration", color='black')  # Set label to "POC Concentration"
    cbar.ax.set_title(r"$\mu$g.L$^{-1}$", color='black', pad=10)

    # Set axis labels and title
    ax.set_xlabel("Wavelength (nm)", color='black')
    ax.set_ylabel("Rrs (sr$^{-1}$)", color='black')
    ax.set_title(f"Rrs Spectra colored by POC Concentration ({df[variable].count()} values)", color='black')

    # Set axis limits and grid
    ax.set_xlim(400, 900)  # Set x-axis limits
    ax.set_ylim(0, 0.07)  # Set y-axis limits
    ax.grid(True, color='gray', linestyle='--', linewidth=0.5)  # Adjust grid for better visibility

    # Set tick colors
    ax.tick_params(colors='black')

    # Add subticks for the x-axis
    ax.xaxis.set_minor_locator(plt.MultipleLocator(10))  # Subticks every 10 nm
    ax.tick_params(axis='x', which='minor', length=4, color='black')  # Customize subticks

    return fig

def plot_rrs_spectra_class(df, variable):
    """
    Plots Rrs spectra from a dataframe and colors them based on a categorical variable (class).

    Parameters:
    - df: pandas DataFrame, where each row contains Rrs spectra and a column for the variable.
    - variable: str, the name of the column to use for coloring the spectra.
    """
    if variable not in df.columns:
        raise ValueError(f"The variable '{variable}' is not in the dataframe.")

    # Extract wavelengths (assuming Rrs columns are named like "Rrs665", "Rrs666", ...)
    rrs_columns = [col for col in df.columns if col.isdigit() and col != variable]
    wavelengths = [float(col) for col in rrs_columns]

    # Define discrete colormap for 5 classes
    colors = ['purple', 'blue', 'green', 'orange', 'red']
    cmap = plt.cm.colors.ListedColormap(colors)
    bounds = [0, 1, 2, 3, 4, 5]
    norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)

    # Create the figure with a white background for the plot area
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('white')  # Set the figure background to white
    ax.set_facecolor('black')  # Set the plot area background to black

    for _, row in df.iterrows():
        color = cmap(norm(row[variable]))
        ax.plot(wavelengths, row[rrs_columns].values, color=color, alpha=0.3)  # Increase transparency

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Add a colorbar
    cbar = plt.colorbar(sm, ax=ax, ticks=[0.5, 1.5, 2.5, 3.5, 4.5])
    cbar.ax.set_yticklabels(['1', '2', '3', '4', '5'])  # Set discrete labels
    cbar.ax.tick_params(colors='black')  # Set tick colors to black
    cbar.set_label("Class", color='black')  # Set label to "Class"
    cbar.ax.set_title("Category", color='black', pad=10)

    # Set axis labels and title
    ax.set_xlabel("Wavelength (nm)", color='black')
    ax.set_ylabel("Rrs (sr$^{-1}$)", color='black')
    ax.set_title(f"Rrs Spectra colored by Class ({df[variable].count()} values)", color='black')

    # Set axis limits and grid
    ax.set_xlim(400, 900)  # Set x-axis limits
    ax.set_ylim(0, 0.07)  # Set y-axis limits
    ax.grid(True, color='gray', linestyle='--', linewidth=0.5)  # Adjust grid for better visibility

    # Set tick colors
    ax.tick_params(colors='black')

    # Add subticks for the x-axis
    ax.xaxis.set_minor_locator(plt.MultipleLocator(10))  # Subticks every 10 nm
    ax.tick_params(axis='x', which='minor', length=4, color='black')  # Customize subticks

    return fig
