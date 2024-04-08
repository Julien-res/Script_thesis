#!/bin/sh

cd "$(dirname "$0")"

input="/nfs/home/log/jmasson/Script/EODAG/EODAG_Listing_DLmissing/1_Listing_disp/List_tiles_MKG.txt"

arr="/nfs/home/log/jmasson/Script/EODAG/EODAG_Listing_DLmissing/1_Listing_disp/year.txt"

while IFS=$' \t\r\n' read -r line ;do
  while IFS=$' \t\r\n' read -r year ;do
    python ./EODAG_listing_data_disp.py -y "$year" -d /nfs/home/log/jmasson/Script/EODAG/EODAG_Listing_DLmissing/Output/Listing_data_disp -c /nfs/home/log/jmasson/Script/EODAG/Credential -s peps -p S2_MSI_L1C -t "$line"
  done < "$arr"
done < "$input"