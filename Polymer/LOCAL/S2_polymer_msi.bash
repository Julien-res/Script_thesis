#!/bin/bash
set -e
DDL='/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/S2_PEPS_L1C/New_data/2018/12/S2B_MSIL1C_20181204T031109_N0207_R075_T48PYQ_20181204T064156.SAFE'

CREDENTIAL='/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/credential'

DOWNLOADED='/mnt/d/DATA/Polymer/DOWNLOADED'
TREATED='/mnt/d/DATA/Polymer/TREATED'
ANCILLARY='/mnt/d/DATA/Polymer/ANCILLARY/METEO'

BASDL=$(basename $DDL)

echo 'Downloading ...'
echo ${BASDL}
sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP cverpoorter@calculco.univ-littoral.fr:$DDL $DOWNLOADED

FILE=$(ls $DOWNLOADED/$BASDL/GRANULE/)
OUTPUT='${FILE}_polymer20m.nc'


echo 'Trying to reach NASA for ancillaries ...'

touch ~/.netrc
USERNAME=$(sed '1!d' $CREDENTIAL/earthdata.credential)
PASSWORD=$(sed '2!d' $CREDENTIAL/earthdata.credential)
USERNAME=$(echo $USERNAME| cut -c 1-30)
echo "machine urs.earthdata.nasa.gov login ${USERNAME} password ${PASSWORD}" > ~/.netrc
chmod 0600 .netrc

rm ~/.urs_cookies
touch ~/.urs_cookies

conda activate polymer
cd ~/polymer-v4.17beta2

echo 'Starting Process...'
python3 /mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/Run_polymer.py -i $DOWNLOADED/$BASDL -o $TREATED -a $ANCILLARY

echo 'Uploading ...'
sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP $TREATED/$OUTPUT cverpoorter@calculco.univ-littoral.fr:/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/New_data_Polymer_20m/

echo 'Removing datas from local storage'
rm $DOWNLOADED/$BASDL
rm $TREATED/$OUTPUT


echo 'All Done! See you space cowboy!'