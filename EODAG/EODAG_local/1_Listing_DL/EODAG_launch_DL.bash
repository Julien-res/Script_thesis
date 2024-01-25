#!/bin/bash
set -e
source ~/anaconda3/etc/profile.d/conda.sh
conda activate EODAG
base64 -d <<<"H4sIAAAAAAAAA5WQMQ7AIAwDd17hsUz5UCQ+ksc3iUkFoh2aoTocC7sAGJwD8LJqwMUTlAD0BECxK+Fxv4XsWyF0WII67kp46M9sB+OXQJvf2kvxST9CO/wJ7JNK9Z9ZH/cXGDR+pPqMIbqkO0j2j9xrKRbvM99KCvoEgUkGqz2rhn/TbrczqAiwAQAA" | gunzip
#=======================================================
# original program was working on a remote directory. Remove if directory is REALLY local
sudo mkdir -p /mnt/share
if sudo mount -t drvfs "//195.83.35.9/home" /mnt/share;then
	echo "Output file mounted boss!"
else
	echo "Check if OpenVPN is running."
	exit 3630
fi
#=======================================================
cd /mnt/c/Travail/Script/Script_thesis/EODAG/EODAG_local/1_Listing_DL
OUTPUT="/mnt/share/DATA/S2_PEPS_L1C/New_data"
CREDENTIAL="/mnt/c/Travail/Script/Script_thesis/EODAG/Credential"
#=======================================================

# AFTER THIS, HIC SVNT LEONES. MODIFY WITH CAUTION.

while IFS=$' \t\r\n' read -r year ;do
  	while IFS=$' \t\r\n' read -r tiles ;do
		python3 ./Main_EODAG.py -c "$CREDENTIAL" -p S2_MSI_LC -s peps -t $tiles -y $year -d $OUTPUT
		echo "====================================================================================="
		echo "====================================================================================="
	done < ./Tiles_List.data
done < ./Year_List.data

base64 -d <<<"H4sIAAAAAAAAA52SQQ6EMAhF9z0Fu9HETG8zqyadg3B4+R/amtjRiahY4EGhKmJSIXIr19gkeoYTVCard9tdY5OoyglOdC/eGXUs/XGPrxtWJeAG0NtqH6a0zfVQl1U4X4GjoEMpVMy2i0asG6byCvhLoI4Mn9IMC4PIHe1VUutpBY9kKnSmnGjt644p9RKAjgwcJzKKfMTuPNBehefJM8jsX4t/BHttQoP+zc8Gpsp7OAGMjDAQzAU91IZGQsw3E+95IpOf4D9hxV/7KXuaR57t5xXTDrnCV7OAAwAA" | gunzip
