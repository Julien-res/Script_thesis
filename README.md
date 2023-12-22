# Script Thesis
## Introduction
### Pep-talk
This repository is here to share the code that I have done during my thesis and help people that want to reuse it. 
All codes available here were made during my thesis between october 2023 and octobe 2026. Some parts can be outdated as it will never be updated.
It is written with the scope that people have already read [CALCULCO differents tutorial pages](https://www-calculco.univ-littoral.fr/), and are a bit comfortable with UNIX (bash,sh), and python.
| File | Utility |
|-----:|-----------|
|Compress| Bash program to compress, search, etc... differents datas|
|EODAG| Python program to Download, compare already downloaded data with online disponibility, etc... for S2_PEPS, S2_THEIA, Google earth engine, Landsat. (More can be used, but need some coding in order to work)|
|Polymer|Run polymer|
|Old_code|File used for storage of old code|

### Python
In order to use python code (Eg : EODAG, Polymer, ...) Python need to be installed (localy or remotely).
It is highly recommended to use [anaconda](http://anaconda.org), as it will automatically manage versions of packages and differents environments.
On CALCULCO, Conda is already downloaded and useable. In order to create your first python environment named 'envpyth', write :

```bash
cd ~
module load conda
conda create --name envpyth
```
To load the environment :

```bash
cd ~
source /nfs/opt/env/env.sh
module load conda
source activate envpyth
```

## EODAG
### Startup
[EODAG](https://eodag.readthedocs.io/en/stable/index.html) and all its dependencies can be installed with the command in bash when a conda environement have been already set-up:
```bash
  conda install -c conda-forge eodag
```
EODAG require credential in order to work. They need to be stored in /Script_thesis/EODAG/Credential/ with the format (`servicename.txt`):

```txt
USERNAMEOREMAIL
PASSWORD
```
For example, if I want to use peps, the file will be named `peps.txt` with my email in the first line, and my password in the other line. Dont forget to 'chmod 0600' your credential to secure them when working on CALCULCO.
### Different usage of EODAG
There are differents usage of EODAG in provided code. Everytime, there will be 3 different files (or more) that goes together: a .py file, a .sh (or bash) file, and an .oar file (see [CALCULCO politics of use](https://www-calculco.univ-littoral.fr/utilisation/lancer-un-calcul)).

- **EODAG_DL** Download year by year or month by month datas from PEPS, THEIA, LANDSAT, or EARTH_SEARCH_GCS (google earth engine). To modify year, month or download path, check `EODAG_DL.sh`
- **EODAG_Listing_DL_missing** that aim to download data that are not already downloaded on specified file. It work with multiple stages:
  - **1st** Listing of available datas online. List of tiles and year that are checked are within `List_tiles_MKG.txt` and `year.txt`
  - **2nd** Downloading of missing datas (use an already set-up database for local datas. Check `/Script_thesis/List_data/peps.csv` for an example (output of `find 'pattern' > service.csv`)
  - **3rd** Retry to download missed datas. Use a database created at the end of **2nd** step. Check `/Script_Thesis/EODAG/EODAG_Listing_DLmissing/2_DL_missing/find_peps_data.sh` to see how it is created if you want to skip **2nd** step. This step take up to 60 min to download one image. It is more robust, but WAY longer that **2nd** step.
  - **4th** Sort output datas. Recursive `mkdir` need to be done beforehand. (2015=> 01 02 ... 12 // 2016=> 01 ...)

## Polymer
```bash
  conda create -n polymer -c conda-forge mamba
  conda activate polymer
  mamba env update -f environment.yml
```

