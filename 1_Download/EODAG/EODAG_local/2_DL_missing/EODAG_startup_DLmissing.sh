#!/bin/sh

cd "$(dirname "$0")"

python ./EODAG_DL_missing.py -e /nfs/home/log/jmasson/Script/List_data/ -l /nfs/home/log/jmasson/Script/EODAG/EODAG_Listing_DLmissing/Output/Listing_data_disp -c /nfs/home/log/jmasson/Script/EODAG/Credential -d /nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/S2_PEPS_L1C/New_data/ -s peps



