import numpy as np
from scipy.stats import chi2

def normalize_rrs(rrs):
    """Normalise un spectre Rrs par l’aire sous la courbe (trapèze)."""
    integral = np.trapz(rrs, dx=1)  # ou spécifier les λ si non réguliers
    return rrs / integral

def log_transform(rrs_norm):
    """Applique la transformation logarithmique avec gestion des zéros."""
    rrs_norm = np.clip(rrs_norm, 1e-8, None)
    return np.log(rrs_norm)

def mahalanobis_distance(x, mu, cov_inv):
    """Calcule la distance de Mahalanobis entre x et le centre mu."""
    diff = x - mu
    return float(diff.T @ cov_inv @ diff)

def classify_rrs_mahalanobis(rrs, class_means, class_covariances):
    """
    Classe un spectre Rrs dans l'une des 16 classes d'eau optiques selon Mélin & Vantrepotte (2015).
    
    Paramètres :
    - rrs : array de Rrs (longueur 6 pour les bandes SeaWiFS)
    - class_means : liste des centres (μ_i) des classes (log(rn))
    - class_covariances : liste des matrices de covariance (Σ_i)
    
    Retour :
    - memberships : liste des probabilités d’appartenance à chaque classe
    """
    rn = normalize_rrs(rrs)
    log_rn = log_transform(rn)
    
    memberships = []
    for mu_i, cov_i in zip(class_means, class_covariances):
        cov_inv = np.linalg.inv(cov_i)
        d2 = mahalanobis_distance(log_rn, mu_i, cov_inv)
        p = 1 - chi2.cdf(d2, df=len(rrs))
        memberships.append(p)
        
    return memberships  # ou np.argmax(memberships) pour la classe dominante


from sklearn.cluster import KMeans

def generate_optical_classes(rrs_dataset, n_classes=17):
    """
    Effectue un clustering de spectres Rrs Sentinel-2 et calcule les stats nécessaires pour classification.
    
    Paramètres :
    - rrs_dataset : array de forme (n_samples, n_bands) avec Rrs Sentinel-2 (ex : 443, 490, 560, 665, 705, 740)
    - n_classes : nombre de classes optiques à générer (par défaut 16)
    
    Retour :
    - class_means : liste de vecteurs log(rn) moyens pour chaque classe
    - class_covariances : liste des matrices de covariance log(rn) pour chaque classe
    - labels : labels de chaque spectre dans l’ensemble
    """
    # Étape 1 : Normalisation
    rrs_normalized = np.array([normalize_rrs(rrs) for rrs in rrs_dataset])
    
    # Étape 2 : Log-transform
    log_rn = np.array([log_transform(rrs) for rrs in rrs_normalized])
    
    # Étape 3 : Clustering
    kmeans = KMeans(n_clusters=n_classes, random_state=42)
    labels = kmeans.fit_predict(log_rn)
    
    # Étape 4 : Moyennes et matrices de covariance
    class_means = []
    class_covariances = []
    for i in range(n_classes):
        cluster_data = log_rn[labels == i]
        mu = np.mean(cluster_data, axis=0)
        sigma = np.cov(cluster_data, rowvar=False)
        class_means.append(mu)
        class_covariances.append(sigma)
        
    return class_means, class_covariances, labels
