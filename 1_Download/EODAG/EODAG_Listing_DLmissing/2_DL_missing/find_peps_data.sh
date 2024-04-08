#!/bin/sh

cd /nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/S2_PEPS_L1C
find /nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/S2_PEPS_L1C/ -name 'S2A_MSIL1C_*.SAFE' -o -name 'S2A_MSIL1C_*.SAFE.bz2' > /nfs/home/log/jmasson/Script/List_data/S2A_PEPS_L1C_aft_DLMiss.csv
find /nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/S2_PEPS_L1C/ -name 'S2B_MSIL1C_*.SAFE' -o -name 'S2B_MSIL1C_*.SAFE.bz2' > /nfs/home/log/jmasson/Script/List_data/S2B_PEPS_L1C_aft_DLMiss.csv
cat /nfs/home/log/jmasson/Script/List_data/S2*_aft_DLMiss.csv > /nfs/home/log/jmasson/Script/List_data/peps_aft_DLMiss.csv