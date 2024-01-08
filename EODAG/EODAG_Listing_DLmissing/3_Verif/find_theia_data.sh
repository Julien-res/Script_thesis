#!/bin/sh

cd /nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_THEIA/RAW
find /nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_THEIA/RAW -name 'SENTINEL2A*.bz2' -o -name 'SENTINEL2B*.bz2' > /nfs/home/log/jmasson/Script/List_data/theia_aft_DLMiss.csv
