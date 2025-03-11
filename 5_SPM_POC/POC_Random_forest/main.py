import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/POC_Random_forest')
os.chdir('/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/POC_Random_forest')
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score , mean_absolute_error, mean_squared_log_error
from load_datas import load_data, load_srf_data, simulate_band
import seaborn as sns
path='/mnt/c/Travail/Script/Script_thesis/5_SPM_POC/Determination_Best_algo'
data = os.path.join(path, 'Data_RRS_In_Situ.csv')
bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']
datar = load_data(data)
srf_data = load_srf_data(path,'S2A')
band_eq = {band: simulate_band(datar, srf_data[band]['Values'],
                                int(srf_data[band]['Wavelengths'][0]), 
                                int(srf_data[band]['Wavelengths'].values[-1])) for band in bands}
poc = datar['POC_microg_L']

# Create a DataFrame to facilitate the removal of NaNs
datadf = pd.DataFrame(band_eq)
datadf['POC'] = poc

# Remove rows containing NaNs
datadf.dropna(inplace=True)

# The columns 'B1', 'B2', ... are the explanatory variables
# And 'POC' is the target variable
X = datadf.filter(like="B")  # Automatically select Rrs columns
y = datadf["POC"]  # Target variable

# Split the data into train (80%) and test (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)

# Create and train the Random Forest model
rf = RandomForestRegressor(n_estimators=1000, random_state=100)
rf.fit(X_train, y_train)

# Predictions
y_pred = rf.predict(X_test)

# Model evaluation
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"RMSE: {rmse:.3f}")
print(f"R²: {r2:.3f}")

# Importance of variables (Rrs bands)
importances = pd.Series(rf.feature_importances_, index=X.columns)
importances.sort_values(ascending=False).plot(kind="bar", title="Importance of Rrs bands")
plt.ylabel("Importance")
plt.tight_layout()
plt.savefig('Importance_Rrs_bands.png')
plt.show()
#==============================================================================
from sklearn.linear_model import Lasso
from sklearn.model_selection import cross_val_score

# Tester différentes valeurs de régularisation
alphas = [0.001, 0.01, 0.1, 1, 10]
for alpha in alphas:
    lasso = Lasso(alpha=alpha, max_iter=10000)
    scores = cross_val_score(lasso, X, y, cv=5, scoring='r2')
    print(f"Alpha: {alpha:.3f} | R² moyen: {np.mean(scores):.3f}")

print("Coefficients du modèle Lasso :")

# %%
from sklearn.linear_model import Ridge

ridge = Ridge(alpha=0.1)
ridge.fit(X, y)
print("R² du modèle Ridge :", ridge.score(X, y))

# %%
from sklearn.linear_model import LinearRegression

lin_reg = LinearRegression()
lin_reg.fit(X, y)
print("R² du modèle linéaire :", lin_reg.score(X, y))

equation = f"POC = {lin_reg.intercept_:.3f}"
for i, band in enumerate(X.columns):
    equation += f" + ({lin_reg.coef_[i]:.3f} * {band})"

print("Équation obtenue :")
print(equation)

y_pred = lin_reg.predict(X)

# Afficher le graphique
sns.set_theme(style="ticks")
fig, ax = plt.subplots(figsize=(6, 6))
sns.scatterplot(x=y, y=y_pred, ax=ax)

# Tracer les lignes x=y, 2x=y et x=2y
min_val = min(y.min(), y_pred.min())
max_val = max(y.max(), y_pred.max())

padding = 0.1 * (max_val - min_val)
ax.set_xlim([min_val - padding, max_val + padding])
ax.set_ylim([min_val - padding, max_val + padding])

extended_x = np.linspace(min_val, max_val, 100)

sns.lineplot(x=extended_x, y=extended_x, color='black', linewidth=0.5, linestyle='--', ax=ax)  # Ligne parfaite y = x
sns.lineplot(x=extended_x, y=2*extended_x, color='black', linewidth=0.2, linestyle='--', ax=ax)  # Ligne 2x = y
sns.lineplot(x=2*extended_x, y=extended_x, color='black', linewidth=0.2, linestyle='--', ax=ax)  # Ligne x = 2y

ax.set_xlabel("POC réel")
ax.set_ylabel("POC prédit")
ax.set_title("Régression linéaire : POC observé vs prédit")
ax.grid(True, which='both', linestyle='--', linewidth=0.3, color='gray', alpha=0.7)
sns.despine(ax=ax)

plt.tight_layout()
plt.savefig('POC_observed_vs_predicted.png')
plt.show()

# %%

# Filtrer les valeurs négatives ou nulles
mask = y > 0
y_filtered = y[mask]
X_filtered = X[mask]

# Appliquer la transformation logarithmique
y_log = np.log(y_filtered)

# Ajuster un nouveau modèle de régression linéaire sur les données transformées en logarithme
lin_reg_log = LinearRegression()
lin_reg_log.fit(X_filtered, y_log)
y_pred_log = lin_reg_log.predict(X_filtered)

# Calcul des statistiques
r2_log = lin_reg_log.score(X_filtered, y_log)
mae_log = mean_absolute_error(y_log, y_pred_log)
rmsle_log = np.sqrt(mean_squared_log_error(y_filtered, np.exp(y_pred_log)))

print(f"R² (log): {r2_log:.3f}")
print(f"MAE (log): {mae_log:.3f}")
print(f"RMSLE: {rmsle_log:.3f}")

# Obtenir les coefficients de la droite de régression
equation_log = f"Log(POC) = {lin_reg_log.intercept_:.3f}"
for i, band in enumerate(X.columns):
    equation_log += f" + ({lin_reg_log.coef_[i]:.3f} * {band})"

print("Équation obtenue (log) :")
print(equation_log)

# Afficher le graphique
sns.set_theme(style="ticks")
fig, ax = plt.subplots(figsize=(6, 6))
sns.scatterplot(x=y_log, y=y_pred_log, ax=ax)

# Tracer les lignes x=y, 2x=y et x=2y
min_val = min(y_log.min(), y_pred_log.min())
max_val = max(y_log.max(), y_pred_log.max())

# Ajuster les limites des axes en fonction de l'échelle logarithmique
if min_val <= 0:
    min_val = min(y_log[y_log > 0].min(), y_pred_log[y_pred_log > 0].min())
padding = 0.1 * (np.log10(max_val) - np.log10(min_val))
ax.set_xlim([10 ** (np.log10(min_val) - padding), 10 ** (np.log10(max_val) + padding)])
ax.set_ylim([10 ** (np.log10(min_val) - padding), 10 ** (np.log10(max_val) + padding)])

extended_x = np.logspace(np.log10(min_val), np.log10(max_val), 100)

sns.lineplot(x=extended_x, y=extended_x, color='black', linewidth=0.5, linestyle='--', ax=ax)  # Ligne parfaite y = x
sns.lineplot(x=extended_x, y=2*extended_x, color='black', linewidth=0.2, linestyle='--', ax=ax)  # Ligne 2x = y
sns.lineplot(x=2*extended_x, y=extended_x, color='black', linewidth=0.2, linestyle='--', ax=ax)  # Ligne x = 2y

ax.set_xlabel("Log(POC réel)")
ax.set_ylabel("Log(POC prédit)")
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_title("Régression linéaire : Log(POC) observé vs prédit")
ax.grid(True, which='both', linestyle='--', linewidth=0.3, color='gray', alpha=0.7)
sns.despine(ax=ax)

plt.tight_layout()
plt.savefig('Poct_observed_vs_predicted_log.png')
plt.show()
