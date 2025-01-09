# Script Thesis
## Introduction
### Pep-talk
This repository is here to share the code that I have done during my thesis and help people that want to reuse it.  <br />
All codes available here were made during my thesis between October 2023 and October 2026. Some parts can be outdated as it will never be updated.
It is written with the scope that people have already read [CALCULCO differents tutorial pages](https://www-calculco.univ-littoral.fr/), and are a bit comfortable with UNIX (bash,sh), and python. <br />
**The various parts of code are intended to be launched from .oar file. Check for paths that needs to be modified in .oar, .sh or .bash depending your installation.**
| File | Utility |
|-----:|-----------|
|Compress| Bash program to compress, search, etc... differents datas|
|EODAG| Python program to Download, compare already downloaded data with online disponibility, etc... for S2_PEPS, S2_THEIA, Google earth engine, Landsat. (More can be used, but need some coding in order to work)|
|Polymer|Run polymer|
|Old_code|File used for storage of old code|

### Python
In order to use python code (Eg : EODAG, Polymer, ...) Python need to be installed (localy or remotely). <br />
It is highly recommended to use [anaconda](http://anaconda.org), as it will automatically manage versions of packages and differents environments. <br />
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
### Start-up
Polymer can be tricky to use, especially on CALCULCO. <br />
In order to start using polymer, we need to download Polymer from [Hygeos](https://www.hygeos.com/polymer) (require an account and admin validation). Unzip tar.gz obtained. <br />
The file `environment.yml` can be used to install the dependencies, either in the current anaconda environment, or in a new one. <br />
To create a new anaconda environment with Polymer dependencies:
```bash
  conda create -n polymer
  conda activate polymer
  conda install python=3.10.13
  conda config --add channels conda-forge
  conda install -n polymer mamba
  conda update -n polymer --all
  cd polymer-v4.16.1
  mamba env update -f environment.yml
  mamba install h5py
  make all

```

As peps, theia, landsat, etc... Polymer need credential to download ancillary datas. You need an account from [EARTHDATA](https://urs.earthdata.nasa.gov) as well explained [here](https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+cURL+And+Wget)
Then store those credential in a new file named `earthdata.credential` in `Script_thesis/Polymer/` (All the work to request server for coockies, etc... is done in the .oar file.)

Now you have two choice: if you work on the server where the datas are stored (CALCULCO for eg) use my CALCULCO part of script, if you work locally with remote data, use LOCAL.
Both need little modification at the start of the .bash or .oar to be functional (modify path depending installation).

## Acolite
### Start-up

```bash
conda create -n acolite -c conda-forge python=3
conda activate acolite
conda install -n acolite mamba
conda update -n acolite --all
mamba install numpy matplotlib scipy gdal pyproj scikit-image pyhdf pyresample netcdf4 h5py requests pygrib  cartopy
export CONDA_ENV_HOME=nfs/home/laboratory/username/.conda/envs
cd $CONDA_ENV_HOME/acolite/lib/python3.12/site-packages
git clone --depth 1 --branch main https://github.com/acolite/acolite.git
cd acolite
#git reset --hard e7cb944
```
Acolite also need earthdata credential. The procedure is the same as Polymer.


## Sen2Cor
### Start-up

```bash
cd ~
curl -O https://download.esa.int/step/snap/11.0/installers/esa-snap_all_linux-11.0.0.sh && chmod 755 esa-snap_all_linux-11.0.0.sh && bash esa-snap_all_linux-11.0.0.sh -c && rm esa-snap_all_linux-11.0.0.sh
    [o, Enter]
    [1, Enter]
    [Enter]
    [Enter]
    [n, Enter]
    [n, Enter]
    [n, Enter]
echo "export SNAP_HOME=/nfs/home/laboratory/username/snap" >> ~/.bashrc
export SNAP_HOME=/nfs/home/laboratory/username/snap
$SNAP_HOME/bin/snap --nosplash --nogui --modules --update-all
$SNAP_HOME/bin/snap --nosplash --nogui --modules --install org.esa.snap.idepix.core org.esa.snap.idepix.probav org.esa.snap.idepix.modis org.esa.snap.idepix.spotvgt org.esa.snap.idepix.landsat8 org.esa.snap.idepix.viirs org.esa.snap.idepix.olci org.esa.snap.idepix.seawifs org.esa.snap.idepix.meris org.esa.snap.idepix.s2msi
echo "#SNAP configuration 's3tbx'" >> ~/.snap/etc/s3tbx.properties
echo "#Fri Mar 27 12:55:00 CET 2020" >> ~/.snap/etc/s3tbx.properties
echo "s3tbx.reader.olci.pixelGeoCoding=true" >> ~/.snap/etc/s3tbx.properties
echo "s3tbx.reader.meris.pixelGeoCoding=true" >> ~/.snap/etc/s3tbx.properties
echo "s3tbx.reader.slstrl1b.pixelGeoCodings=true" >> ~/.snap/etc/s3tbx.properties
```
## C2RCC
### Start-up

In order to use C2RCC, we need to create a GPF graph using GPT tool of SNAP.
```bash
cd ~
~/snap/bin/gpt -h
```
It will show information that will help you to create GPF graph (.xml). Both tutorials from SNAP can be useful too:
https://senbox.atlassian.net/wiki/spaces/SNAP/pages/70503590/Creating+a+GPF+Graph
https://senbox.atlassian.net/wiki/spaces/SNAP/pages/70503475/Bulk+Processing+with+GPT
Here a GPF graph is already created for C2RCC process, but it can bu usefull to understand how to add part process.


## WiPE

Install X-Server Windows

https://sourceforge.net/projects/vcxsrv/
Set Display forward in WSL Distro

Configure Display:

    If you running WSL1:

export LIBGL_ALWAYS_INDIRECT=1
export DISPLAY=localhost:0

    If you running WSL2:

export LIBGL_ALWAYS_INDIRECT=1
export DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0

    (If you have disabled resolv.conf use this definition: https://stackoverflow.com/a/63092879/11473934)

and then (install x11-apps):

sudo apt update
sudo apt install x11-apps

Start XLaunch on Windows

    Multiple Windows
    Start no client
    disable Native opengl
    enable Disable access control

Test it

In wsl: enter xcalc - Calculator should open in Windows10
If everything worked

And you want to persist the settings in your wsl distro. Store them in your ~/.bashrc.

sudo nano ~/.bashrc

Copy the two lines (from Set Display forward in WSL Distro - Configure Display) to the end and save it.
Add it to autostart

    Run Dialog see Start XLaunch on Windows
    Save configuration
    Press Windows + R
    Enter: shell:startup
    Copy saved configuration: *.launch (Generated in step 2) to this folder (step 4)

Now the XServer will be started with windows startup.
