#!/bin/bash
set -e
base64 -d <<<"H4sIAAAAAAAAA5VPMRLAIAjbfUXWTnyIu3yExzeAVNfqnYGYGAQA5tqoMwvg9GwBR7d0FcU7rCDUuzbUG+C2BeTo2hPkk1B1gkyUJd0yluDovhza7dk5qr35TIma2yYHExcNW3KeGcpnNpZH41Rcf7jIOS7K6Qv/13oBompMtmwBAAA=" | gunzip
# MODIFY DEPENDING YOUR INSTALLATION
source ~/anaconda3/etc/profile.d/conda.sh
conda activate polymer

ALLD="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/All_new_data_PEPS.csv" # location of the list of file location to download (use 'find' command in UNIX)
ALLDTMP="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/All_new_data_PEPS_tmp.csv" # At the first launch, shouldbe an exact copy of the list above
ALRDTT="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/Polymer_alr_tt.csv" # File where name out processed data will be stored
CREDENTIAL="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/credential" # Where .credential are stored (CALCULCO password in privateKey.credential and earthdata.credential)
CRD="cverpoorter@calculco.univ-littoral.fr" # account to ssh login
DOWNLOADED="/mnt/d/DATA/Polymer/DOWNLOADED" #Where to output downloaded datas
TREATED="/mnt/d/DATA/Polymer/TREATED" #Where to output treated datas
ANCILLARY="/mnt/d/DATA/Polymer/ANCILLARY/METEO" # where to output Ancillaries
PYTHON="/home/julien/anaconda3/envs/polymer/bin/python3" # Python path (type "which python" in UNIX shell)
CCLO="/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/New_data_Polymer_20m/" #output file on remote server
PROGRAM="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/Run_polymer.py" #Location of Run_polymer.py
#=======================================================
# AFTER THIS, HIC SVNT LEONES. MODIFY WITH CAUTION.

# Verify that files are all accessible
chmod 0777 $TREATED
chmod 0777 $ANCILLARY
chmod 0777 $DOWNLOADED
chmod 0600 $CREDENTIAL
chmod 0777 $PROGRAM
chmod 0777 $ALLD
chmod 0777 $ALLDTMP

# Ensure that the program can be run multiple times without reprocessing datas that are already processed
FIRST=$(wc -l < $ALLD)
SECOND=$(wc -l < $ALLDTMP)
if [ "$FIRST" -gt "$SECOND" ];then
	echo "Replacing Data list by a newer data list from past execution..."
	cp -f $ALLDTMP $ALLD
else
	echo "Using provided data list, no modification done since last execution..."
fi

# Start of the loop that read all line of provided data list
while IFS= read -r DDL; do
    echo "Text read from file: $DDL"
	BASDL=$(basename $DDL)

	echo "Downloading ..."
	echo ${BASDL}

	sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP $CRD:$DDL $DOWNLOADED
	FILE=$(ls $DOWNLOADED/$BASDL/GRANULE/)
	OUTPUT="${FILE}_polymer20m.nc"

	echo "Trying to reach NASA for ancillaries ..."
	touch ~/polymer-v4.17beta2/.netrc
	USERNAME=$(sed "1!d" $CREDENTIAL/earthdata.credential)
	PASSWORD=$(sed "2!d" $CREDENTIAL/earthdata.credential)
	USERNAME=$(echo $USERNAME| cut -c 1-30)
	echo "machine urs.earthdata.nasa.gov login ${USERNAME} password ${PASSWORD}" > ~/polymer-v4.17beta2/.netrc
	chmod 0600 ~/polymer-v4.17beta2/.netrc
	rm ~/polymer-v4.17beta2/.urs_cookies
	touch ~/polymer-v4.17beta2/.urs_cookies
	cd ~/polymer-v4.17beta2

	echo "Starting Process..."
	python3 $PROGRAM -i $DOWNLOADED/$BASDL -o $TREATED/ -a $ANCILLARY
	if mv $DOWNLOADED/$BASDL/GRANULE/$OUTPUT $TREATED/ ;then
		echo "Uploading ..."
	else
		echo "Error while processing data. Check connection with NASA"
		exit 3630
	fi
	chmod 0777 $TREATED/$OUTPUT
	sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP $TREATED/$OUTPUT $CRD:$CCLO --progress

	echo "Removing datas from local storage"
	rm -r $DOWNLOADED/$BASDL
	rm -r $TREATED/$OUTPUT
	rm -r $ANCILLARY/*

	#Log processed data
	echo ${DDL} >> $ALRDTT
	echo -e "$(sed '1d' $ALLDTMP)\n" > $ALLDTMP
	head -c -1 $ALLDTMP > $ALLDTMP
	truncate -s -1 $ALLDTMP

	
	echo "====================================================================================="
	echo "====================================================================================="
done < $ALLD
base64 -d <<<"H4sIAAAAAAAAA52SQQ6EMAhF9z0Fu9HETG8zqyadg3B4+R/amtjRiahY4EGhKmJSIXIr19gkeoYTVCard9tdY5OoyglOdC/eGXUs/XGPrxtWJeAG0NtqH6a0zfVQl1U4X4GjoEMpVMy2i0asG6byCvhLoI4Mn9IMC4PIHe1VUutpBY9kKnSmnGjt644p9RKAjgwcJzKKfMTuPNBehefJM8jsX4t/BHttQoP+zc8Gpsp7OAGMjDAQzAU91IZGQsw3E+95IpOf4D9hxV/7KXuaR57t5xXTDrnCV7OAAwAA" | gunzip
