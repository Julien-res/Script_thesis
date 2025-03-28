import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
def compute_and_plot_correlation_matrix(data, band_limits, poc_column='POC'):
    """
    Calcule et affiche une matrice de corrélation R² entre les ratios de bandes Rrs et la variable POC.
    Sauvegarde la matrice et la figure si des chemins sont fournis.

    Parameters:
        data (pd.DataFrame): Le DataFrame contenant les colonnes Rrs et la colonne POC.
        band_limits (dict): Un dictionnaire contenant les noms des bandes et leurs limites, ex: {'B1': (412, 456)}.
        poc_column (str): Le nom de la colonne contenant les valeurs de POC.

    Returns:
        np.ndarray: La matrice de corrélation R².
    """
    # Extraire les colonnes Rrs (colonnes avec des noms numériques entre 400 et 800)
    rrs_columns = [col for col in data.columns if col.isdigit() and 400 <= int(col) <= 800 and col != poc_column]
    poc = data[poc_column]

    # Initialiser la matrice de corrélation
    n_bands = len(rrs_columns)
    correlation_matrix = np.zeros((n_bands, n_bands))

    # Calculer les corrélations
    for i, band_x in enumerate(rrs_columns):
        for j, band_y in enumerate(rrs_columns):
            if i < j:  # Ne calculer que pour la moitié supérieure
                with np.errstate(divide='ignore', invalid='ignore'):  # Suppress divide-by-zero warnings
                    ratio = data[band_x] / data[band_y]
                ratio = ratio.replace([np.inf, -np.inf], np.nan).dropna()  # Gérer les divisions par zéro
                valid_indices = ratio.index.intersection(poc.index)

                # Appliquer la transformation logarithmique
                log_ratio = np.log(ratio.loc[valid_indices])
                log_poc = np.log(poc.loc[valid_indices])

                # Filtrer les valeurs infinies ou NaN après la transformation logarithmique
                valid_mask = (~np.isnan(log_ratio)) & (~np.isinf(log_ratio)) & (~np.isnan(log_poc)) & (~np.isinf(log_poc))
                log_ratio = log_ratio[valid_mask]
                log_poc = log_poc[valid_mask]

                if len(log_ratio) > 0:  # Vérifier qu'il y a des données valides
                    # Régression linéaire de type II (approximation avec LinearRegression)
                    model = LinearRegression()
                    model.fit(log_ratio.values.reshape(-1, 1), log_poc.values)
                    predictions = model.predict(log_ratio.values.reshape(-1, 1))
                    r2 = r2_score(log_poc.values, predictions)
                    correlation_matrix[i, j] = r2

    # Visualiser la matrice de corrélation (moitié supérieure)
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))  # Masquer la moitié inférieure
    plt.imshow(np.ma.masked_array(correlation_matrix, ~mask), cmap='rainbow', origin='lower')
    cbar = plt.colorbar()
    cbar.set_label('Correlation with POC')
    cbar.ax.set_title('R²', pad=10)

    # Définir les ticks principaux (tous les 10 indices) et les sous-ticks
    major_ticks = [i for i in range(n_bands) if i % 10 == 0]
    minor_ticks = list(range(n_bands))

    plt.xticks(major_ticks, [rrs_columns[i] for i in major_ticks], rotation=90)
    plt.yticks(major_ticks, [rrs_columns[i] for i in major_ticks])
    plt.gca().set_xticks(minor_ticks, minor=True)
    plt.gca().set_yticks(minor_ticks, minor=True)

    # Ajouter du padding pour éloigner les labels des ticks des axes
    plt.gca().tick_params(axis='x', pad=10)  # Padding pour l'axe X
    plt.gca().tick_params(axis='y', pad=10)  # Padding pour l'axe Y

    # Ajouter les aires grises pour les bandes (seulement sur la moitié supérieure de la matrice)
    for band_name_x, (start_x, end_x) in band_limits.items():
        start_idx_x = next((i for i, col in enumerate(rrs_columns) if int(col) >= start_x), None)
        end_idx_x = next((i for i, col in enumerate(rrs_columns) if int(col) > end_x), None)
        if start_idx_x is not None and end_idx_x is not None:
            for band_name_y, (start_y, end_y) in band_limits.items():
                start_idx_y = next((i for i, col in enumerate(rrs_columns) if int(col) >= start_y), None)
                end_idx_y = next((i for i, col in enumerate(rrs_columns) if int(col) > end_y), None)
                if start_idx_y is not None and end_idx_y is not None and start_idx_y <= start_idx_x:
                    # Vérifier que le rectangle est dans la moitié supérieure
                    if start_idx_y <= start_idx_x and end_idx_y <= end_idx_x:
                        # Dessiner l'intérieur gris avec alpha léger
                        plt.gca().add_patch(plt.Rectangle(
                            (start_idx_x, start_idx_y),  # Coin inférieur gauche
                            end_idx_x - start_idx_x,    # Largeur
                            end_idx_y - start_idx_y,    # Hauteur
                            facecolor='gray', alpha=0.3, edgecolor='none'
                        ))
                        # Dessiner les bords en noir sans alpha
                        plt.gca().add_patch(plt.Rectangle(
                            (start_idx_x, start_idx_y),  # Coin inférieur gauche
                            end_idx_x - start_idx_x,    # Largeur
                            end_idx_y - start_idx_y,    # Hauteur
                            facecolor='none', edgecolor='black', linewidth=0.8
                        ))

    # Ajouter les noms des bandes sur les axes
    for band_name, (start, end) in band_limits.items():
        start_idx = next((i for i, col in enumerate(rrs_columns) if int(col) >= start), None)
        end_idx = next((i for i, col in enumerate(rrs_columns) if int(col) > end), None)
        if start_idx is not None and end_idx is not None:
            mid_idx = (start_idx + end_idx - 1) // 2
            plt.text(mid_idx, -3, band_name, ha='center', va='center', fontsize=10, rotation=90)  # Axe X (éloigné)
            plt.text(-3, mid_idx, band_name, ha='center', va='center', fontsize=10, rotation=0)   # Axe Y (éloigné)
    
    # Supprimer la grille pour les sous-ticks
    plt.grid(which='minor', visible=False)  # Désactiver la grille des sous-ticks

    # Modifier la couleur de la grille des ticks principaux
    plt.grid(which='major', color='lightgray', linestyle='-', linewidth=0.75, alpha=0.3)  # Ticks principaux en gris léger

    # # Ajouter une grille en pointillé pour les centaines
    # hundred_ticks = [i for i in range(n_bands) if i % 100 == 0]
    # for tick in hundred_ticks:
    #     plt.axhline(tick, color='blue', linestyle='--', linewidth=0.75)
    #     plt.axvline(tick, color='blue', linestyle='--', linewidth=0.75)

    plt.title('Correlation Matrix (R²) of Band Ratios with POC')
    plt.xlabel('Band X')
    plt.ylabel('Band Y')
    plt.tight_layout()

    # Retourner la figure
    fig = plt.gcf()
    return correlation_matrix, fig
