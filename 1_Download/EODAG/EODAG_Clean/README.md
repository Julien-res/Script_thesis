# README.md

# EODAG Sentinel-2 Downloader

Ce projet permet de télécharger des images Sentinel-2 en utilisant le module EODAG. Il prend en charge geodes (prendra en charge d'autres fournisseurs dans le futur) et permet de spécifier des paramètres tels que l'année, le mois, les tuiles, etc.

## Prérequis

- Python 3.x
- EODAG
- Les bibliothèques Python suivantes : `os`, `sys`, `calendar`, `argparse`, `glob`, `re`, `datetime`, `shapely`

## Installation

1. Clonez ce dépôt :
    ```sh
    git clone <URL_DU_DEPOT>
    cd <NOM_DU_DEPOT>
    ```

2. Installez les dépendances :
    ```sh
    pip install -r requirements.txt
    ```

## Utilisation

### Arguments

- `-y`, `--year` (int, requis) : Année de l'image.
- `-t`, `--tile` (str, requis) : Tuile(s) désirée(s) à télécharger (par exemple, 31TFJ).
- `-c`, `--credential` (str, requis) : Chemin vers le fichier de crédential (si aucun fournisseur n'est spécifié, `geodes` est utilisé par défaut).
- `-o`, `--output` (str) : Chemin où les fichiers téléchargés seront stockés (par défaut : stdout).
- `-s`, `--service` (str) : Fournisseur de données pour le téléchargement (par défaut : `geodes`).
- `-m`, `--month` (int) : Mois de l'image.
- `-k`, `--check` (str) : Chemin optionnel pour vérifier les fichiers déjà téléchargés.
- `-r`, `--recursive` (bool) : Recherche récursive dans les sous-répertoires (par défaut : True).

### Exemple de commande

```sh
python main_eodag.py -y 2023 -t 31TFJ -c /path/to/credentials -o /path/to/output -s peps -m 6 -k /path/to/check -r true
```

## Structure du projet

- 'main_eodag.py' : Script principal pour lancer le téléchargement.
- 'create_yaml.py' : Script pour créer le fichier de configuration YAML pour EODAG.
- 'EODAG_search.py' : Script pour effectuer la recherche des produits Sentinel-2 via EODAG.
## Fonctionnalités

Recherche de fichiers Sentinel-2 : Recherche des fichiers Sentinel-2 dans un répertoire donné.
Création de fichiers YAML : Génère un fichier de configuration YAML pour EODAG en fonction des paramètres spécifiés.
Téléchargement d'images Sentinel-2 : Télécharge les images Sentinel-2 en utilisant l'API EODAG.
## Auteur
Julien Masson

## Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.