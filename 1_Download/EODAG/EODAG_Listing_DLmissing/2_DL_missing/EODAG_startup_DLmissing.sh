#!/bin/sh

cd "$(dirname "$0")"
source ~/anaconda3/etc/profile.d/conda.sh
conda activate EODAG
python3 ./EODAG_DL_missing.py -e /mnt/c/Travail/Script/Script_thesis/EODAG/EODAG_local/2_DL_missing/ -l /mnt/c/Travail/Script/Script_thesis/EODAG/EODAG_local/Data_disp_HDF -c /mnt/c/Travail/Script/Script_thesis/EODAG/Credential -d mnt/d/DATA/S2A_L1C -s peps



