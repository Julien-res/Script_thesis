#!/bin/bash
set -e


base64 -d <<<"H4sIAAAAAAAAA5VPMRLAIAjbfUXWTnyIu3yExzeAVNfqnYGYGAQA5tqoMwvg9GwBR7d0FcU7rCDUuzbUG+C2BeTo2hPkk1B1gkyUJd0yluDovhza7dk5qr35TIma2yYHExcNW3KeGcpnNpZH41Rcf7jIOS7K6Qv/13oBompMtmwBAAA=" | gunzip
# MODIFY DEPENDING YOUR INSTALLATION
source ~/anaconda3/etc/profile.d/conda.sh
conda activate polymer

ALLD="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/All_new_data_PEPS.data" # Location of the list of file location to download (use 'find' command in UNIX)
CREDENTIAL="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/credential" # Where .credential are stored (CALCULCO password in privateKey.credential and earthdata.credential)
CRD="cverpoorter@calculco.univ-littoral.fr" # Account to ssh login
DOWNLOADED="/mnt/d/DATA/Polymer/DOWNLOADED" # Where to output downloaded datas
TREATED="/mnt/d/DATA/Polymer/TREATED" # Where to output treated datas
ANCILLARY="/mnt/d/DATA/Polymer/ANCILLARY/METEO" # where to output Ancillaries
ANCILLARD="/mnt/c/Travail/Script/Script_thesis/Ancillary/ANCILLARY/METEO" # Location of Ancillary data if already downloaded DB
PYTHON="/home/julien/anaconda3/envs/polymer/bin/python3" # Python path (type "which python" in UNIX shell)
CCLO="/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/New_data_Polymer_20m/" # Output file on remote server
PROGRAM="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/Run_polymer.py" # Location of Run_polymer.py
#=======================================================
# AFTER THIS, HIC SVNT LEONES. MODIFY WITH CAUTION.


# Verify that files are all accessible
chmod 0777 $TREATED
chmod 0777 $ANCILLARY

if [ -d "$ANCILLARD" ]; then
	chmod 0777 $ANCILLARD
fi
chmod 0777 $DOWNLOADED
chmod 0600 $CREDENTIAL
chmod 0777 $PROGRAM
chmod 0777 $ALLD


# Ensure that the program can be run multiple times without reprocessing datas that are already processed

BLUE='\033[1;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
WHITE='\033[47m'
NC='\033[0m'

PRCC=${ALLD%"$(basename $ALLD)"}
PRCC+="Polymer_alr_prc.data"

if test -f $PRCC;then
	echo -e "${YELLOW}Program already launched once... Welcome back, boss! Unfinished business?${NC}"
else
	echo -e "${YELLOW}First launch, Welcome!${NC}"
	touch $PRCC
fi


FOO=${ALLD%".data"}
FOO+=".new"

if test -f "$FOO";then
	echo "Tmp files OK"
	FIRST=$(wc -l < $ALLD)
	SECOND=$(wc -l < $FOO)
	if [ "$FIRST" -gt "$SECOND" ];then
		echo -e "${YELLOW}Replacing Data list by a newer data list from past unfinished execution...${NC}"
		cp $FOO $ALLD
	else
		echo -e "${YELLOW}Using provided data list, no modification done since last execution...${NC}"
	fi
else
	echo "Creating Tmp files in ${ALLD%"$(basename $ALLD)"}"
	cp $ALLD $FOO
fi

echo -e "${RED}Trying to reach NASA for ancillaries ...${NC}"
touch ~/polymer-v4.17beta2/.netrc
USERNAME=$(sed "1!d" $CREDENTIAL/earthdata.credential)
PASSWORD=$(sed "2!d" $CREDENTIAL/earthdata.credential)
USERNAME=$(echo $USERNAME| cut -c 1-30)
echo "machine urs.earthdata.nasa.gov login ${USERNAME} password ${PASSWORD}" > ~/polymer-v4.17beta2/.netrc
chmod 0600 ~/polymer-v4.17beta2/.netrc

# Start of the loop that read all line of provided data list
while IFS= read -r DDL; do
    echo "Text read from file: $DDL"
	BASDL=$(basename $DDL)

	echo -e "${BLUE}Downloading ...${NC}"
	echo -e "${YELLOW} ${BASDL} ${NC}"

	sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP $CRD:$DDL $DOWNLOADED
	FILE=$(ls $DOWNLOADED/$BASDL/GRANULE/)
	OUTPUT="${FILE}_polymer20m.nc"

	rm ~/polymer-v4.17beta2/.urs_cookies
	touch ~/polymer-v4.17beta2/.urs_cookies
	cd ~/polymer-v4.17beta2

	echo -e "${BLUE}Starting Process...${NC}"

	if [ -d "$ANCILLARD" ]; then
		python3 $PROGRAM -i $DOWNLOADED/$BASDL -o $TREATED/ -a $ANCILLARD
		echo -e "${YELLOW}Ancillary already downloaded, process done!${NC}"
	else
		python3 $PROGRAM -i $DOWNLOADED/$BASDL -o $TREATED/ -a $ANCILLARY
	fi

	if mv $DOWNLOADED/$BASDL/GRANULE/$OUTPUT $TREATED/ ;then
		echo -e "${BLUE}Uploading ...${NC}"
	else
		echo -e "${RED}Error while processing data. Check connection with NASA or ancillaries database${NC}"
		exit 3630
	fi
	chmod 0777 $TREATED/$OUTPUT
	sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP $TREATED/$OUTPUT $CRD:$CCLO --progress

	echo -e "${BLUE}Removing datas from local storage${NC}"
	rm -r $DOWNLOADED/$BASDL
	rm -r $TREATED/$OUTPUT
	
	if [ -d "$ANCILLARD" ]; then
		echo -e "${YELLOW}Ancillary ok!${NC}"
	else
		rm -r $ANCILLARY/*
	fi

	#Log processed data
	echo ${DDL} >> $PRCC
	touch "$FOO.tmp"
	tail -n +2 "$FOO" > "$FOO.tmp" && mv "$FOO.tmp" "$FOO"

	echo -e "${WHITE}=====================================================================================${NC}"
done < $ALLD

rm -r $FOO
cp $PRCC $ALLD
rm -r $PRCC

base64 -d <<<"H4sIAAAAAAAAA52SQQ6EMAhF9z0Fu9HETG8zqyadg3B4+R/amtjRiahY4EGhKmJSIXIr19gkeoYTVCard9tdY5OoyglOdC/eGXUs/XGPrxtWJeAG0NtqH6a0zfVQl1U4X4GjoEMpVMy2i0asG6byCvhLoI4Mn9IMC4PIHe1VUutpBY9kKnSmnGjt644p9RKAjgwcJzKKfMTuPNBehefJM8jsX4t/BHttQoP+zc8Gpsp7OAGMjDAQzAU91IZGQsw3E+95IpOf4D9hxV/7KXuaR57t5xXTDrnCV7OAAwAA" | gunzip

