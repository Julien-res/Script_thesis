import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns  # Importer Seaborn
from scipy.stats import norm  # Importer pour ajuster une distribution normale

def plot_frequency_distribution(df, column_name):
    """
    Génère un diagramme de fréquence de distribution pour une colonne donnée d'un DataFrame.
    L'échelle des x est en log, et la médiane est indiquée sur le graphique.
    Une courbe de densité est ajoutée pour vérifier la normalité.
    Un deuxième axe x est ajouté pour la densité.

    :param df: pandas DataFrame
    :param column_name: Nom de la colonne pour laquelle générer le diagramme
    :return: matplotlib.figure.Figure
    """
    if column_name not in df.columns:
        raise ValueError(f"La colonne '{column_name}' n'existe pas dans le DataFrame.")
    
    # Extraire les données de la colonne et supprimer les valeurs manquantes
    data = df[column_name].dropna()

    # Calculer la médiane
    median_value = np.median(data)

    # Calculer le nombre total de valeurs
    total_values = len(data)

    # Configurer le style de Seaborn
    sns.set(style="whitegrid")

    # Créer le diagramme de fréquence
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Définir les bins en échelle logarithmique
    min_data = data.min()
    max_data = data.max()
    padding_factor = 2  # Facteur pour ajouter du padding autour de la médiane
    log_min = np.log10(median_value) - padding_factor
    log_max = np.log10(median_value) + padding_factor
    bins = np.logspace(log_min, log_max, num=30)  # 30 bins en échelle log

    # Histogramme
    ax1.hist(data, bins=bins, edgecolor='black', log=False, density=False, alpha=0.6, label='Histogramme')
    ax1.set_xscale('log')
    ax1.set_xlabel(column_name + ' (échelle log)')
    ax1.set_ylabel('Fréquence', color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    # Ajouter une ligne verticale pour la médiane
    ax1.axvline(median_value, color='red', linestyle='--', label=f'Médiane: {median_value:.2f}')
    ax1.legend(loc='upper left')

    # Ajouter un deuxième axe pour la densité
    ax2 = ax1.twinx()
    sns.kdeplot(data, ax=ax2, color='blue', label='KDE', linewidth=2)
    # Ajuster une distribution normale sur les données en échelle logarithmique
    log_data = np.log10(data)
    mean, std = norm.fit(log_data)
    x = np.logspace(log_min, log_max, 1000)
    log_x = np.log10(x)
    pdf = norm.pdf(log_x, mean, std)
    ax2.plot(x, pdf, color='green', linestyle='--', label=f'Normale ajustée\n(µ={mean:.2f}, σ={std:.2f})')
    ax2.set_ylabel('Densité', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.grid(False)

    # Ajouter une légende pour le deuxième axe
    ax2.legend(loc='upper right')

    # Ajouter des labels et un titre
    plt.title(f'Diagramme de fréquence et densité de POC Concentration ($\mu$g.L$^{-1}$)\n'
              f'Nombre total de valeurs: {total_values}, Bins: {len(bins)}')
    fig.tight_layout()

    # Retourner la figure
    return fig
