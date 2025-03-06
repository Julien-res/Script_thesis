#!/bin/bash
set -e
source ~/anaconda3/etc/profile.d/conda.sh
conda activate EODAG
base64 -d <<<"H4sIAAAAAAAAA5WQMQ7AIAwDd17hsUz5UCQ+ksc3iUkFoh2aoTocC7sAGJwD8LJqwMUTlAD0BECxK+Fxv4XsWyF0WII67kp46M9sB+OXQJvf2kvxST9CO/wJ7JNK9Z9ZH/cXGDR+pPqMIbqkO0j2j9xrKRbvM99KCvoEgUkGqz2rhn/TbrczqAiwAQAA" | gunzip
#=======================================================
cd /mnt/c/Travail/Script/Script_thesis/1_Download/EODAG/EODAG_local/1_Listing
LOCAL="/mnt/d/DATA/S2A_L1C"
CREDENTIAL="/mnt/c/Travail/Script/Script_thesis/1_Download/EODAG/Credential"
TOTP="834166" #TOTP code from OTP auth App
#=======================================================

# AFTER THIS, HIC SVNT LEONES. MODIFY WITH CAUTION.

while IFY=$' \t\r\n' read -r year ;do
  	while IFT=$' \t\r\n' read -r tiles ;do
		python3 ./Main_EODAG.py -c "$CREDENTIAL" -p S2_MSI_L1C -s creodias -t $tiles -y $year -l $LOCAL -o $TOTP
		echo "====================================================================================="
		echo "====================================================================================="
		sleep 1m
	done < ./Tiles_List.data
	
done < ./Year_List.data

base64 -d <<<"H4sIAAAAAAAAA52SQQ6EMAhF9z0Fu9HETG8zqyadg3B4+R/amtjRiahY4EGhKmJSIXIr19gkeoYTVCard9tdY5OoyglOdC/eGXUs/XGPrxtWJeAG0NtqH6a0zfVQl1U4X4GjoEMpVMy2i0asG6byCvhLoI4Mn9IMC4PIHe1VUutpBY9kKnSmnGjt644p9RKAjgwcJzKKfMTuPNBehefJM8jsX4t/BHttQoP+zc8Gpsp7OAGMjDAQzAU91IZGQsw3E+95IpOf4D9hxV/7KXuaR57t5xXTDrnCV7OAAwAA" | gunzip
