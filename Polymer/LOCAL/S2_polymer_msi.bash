#!/bin/bash
set -e
# MODIFY DEPENDING YOUR INSTALLATION
source ~/anaconda3/etc/profile.d/conda.sh
conda activate polymer
ALLD="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/All_new_data_PEPS.csv"
while IFS= read -r DDL; do
    echo "Text read from file: $DDL"
    # MODIFY DEPENDING YOUR INSTALLATION
	CREDENTIAL="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/credential" # Where .credential are stored (CALCULCO password in privateKey.credential and earthdata.credential)
	DOWNLOADED="/mnt/d/DATA/Polymer/DOWNLOADED" #Where to output downloaded datas
	TREATED="/mnt/d/DATA/Polymer/TREATED" #Where to output treated datas
	ANCILLARY="/mnt/d/DATA/Polymer/ANCILLARY/METEO" # where to output Ancillaries
	PYTHON="/home/julien/anaconda3/envs/polymer/bin/python3" # Python path (type "which python" in UNIX shell)


	#=======================================================

	chmod 0777 $TREATED
	chmod 0777 $ANCILLARY
	chmod 0777 $DOWNLOADED
	chmod 0600 $CREDENTIAL

	BASDL=$(basename $DDL)
	echo "Downloading ..."
	echo ${BASDL}
	sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP cverpoorter@calculco.univ-littoral.fr:$DDL $DOWNLOADED

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
	python3 /mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/Run_polymer.py -i $DOWNLOADED/$BASDL -o $TREATED/ -a $ANCILLARY

	mv $DOWNLOADED/$BASDL/GRANULE/$OUTPUT $TREATED/
	chmod 0777 $TREATED/$OUTPUT
	echo "Uploading ..."
	sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP $TREATED/$OUTPUT cverpoorter@calculco.univ-littoral.fr:/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/New_data_Polymer_20m/ --progress

	echo "Removing datas from local storage"
	rm -r $DOWNLOADED/$BASDL
	rm -r $TREATED/$OUTPUT
	rm -r $ANCILLARY/*

done < $ALLD
echo "All Done! See you space cowboy!"
