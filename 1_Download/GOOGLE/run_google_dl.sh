#!/bin/sh
# Path and other things need to be modified by the user

# Read the list of tiles from the external text file
tiles=$(cat List_tiles_MKG.txt)

# Loop through the years 2016 to 2024
for year in 2016 2017 2018 2019 2020 2021 2022 2023 2024; do
  # Loop through each tile in the list
  for tile in $tiles; do
    # Run the Python program with the specified year and tile
    python Main_GOOGLE.py -y $year -t $tile -c /nfs/home/log/jmasson/Script/GOOGLE/Credential/pure-lantern-405110-43589b6d4cac.json -o /nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/S2_PEPS_L1C/New_data/ -d /nfs/home/log/jmasson/Script/GOOGLE/data_DL.csv
  done
done
