#!/bin/sh

# Read the list of tiles from the external text file
tiles=$(cat List_tiles_MKG.txt)

# Loop through the years 2016 to 2024
for year in {2016..2024}; do
  # Loop through each tile in the list
  for tile in $tiles; do
    # Run the Python program with the specified year and tile
    python main_eodag.py -y $year -t $tile -c /mnt/c/Travail/Script/Script_thesis/1_Download/EODAG/Credential/ -o /mnt/c/Travail/Script/Script_thesis/1_Download/EODAG/TEST/
  done
done
