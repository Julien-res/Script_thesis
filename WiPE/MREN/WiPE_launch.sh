#!/bin/bash
set -e
shopt -s globstar

base64 -d <<<"H4sIAAAAAAAAA3WOwQ2AUAhD73+KHvXEQiZdpMNLi19PlpAGeBAAkHjFLmhhjFjdvToeFQ6e2bk0jEwMUs4OCmJjsR6GMFJwlgdZrpg28d0IIbdy4/kjyNzoAcUh5lNt4l/rBjwToz/uAAAA" | gunzip
# MODIFY DEPENDING YOUR INSTALLATION

ALLD="/work/users/cverpoorter/VolTransMESKONG/Code/wipesen/Script/All_new_data_PEPS.data" # Location of the list of file location to download (use 'find' command in UNIX)
CREDENTIAL="/work/users/cverpoorter/VolTransMESKONG/Code/wipesen/Script/credential" # Where .credential are stored (CALCULCO password in privateKey.credential and earthdata.credential)
CRD="cverpoorter@calculco.univ-littoral.fr" # Account to ssh login
DOWNLOADED="/work/users/cverpoorter/VolTransMESKONG/Code/wipesen/DOWNLOADED" # Where to output downloaded datas
TREATED="/work/users/cverpoorter/VolTransMESKONG/Code/wipesen/TREATED" # Where to output treated datas
PROGRAM="/work/users/cverpoorter/VolTransMESKONG/Code/wipesen" # Location of Run_polymer.py
#=======================================================
# AFTER THIS, HIC SVNT LEONES. MODIFY WITH CAUTION.


# Verify that files are all accessible
chmod 0777 $TREATED
chmod 0777 $DOWNLOADED
chmod 0777 $CREDENTIAL
chmod 0777 $PROGRAM
chmod 0777 $ALLD

# Ensure that the program can be run multiple times without reprocessing datas that are already processed

BLUE='\033[1;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
WHITE='\033[47m'
NC='\033[0m'

PRCC=${ALLD%"$(basename $ALLD)"}
PRCC+="WiPE_alr_prc.data"

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

# Start of the loop that read all line of provided data list
while IFS= read -r DDL; do
    echo "Text read from file: $DDL"
	BASDL=$(basename $DDL)

	echo -e "${BLUE}Downloading ...${NC}"
	echo -e "${YELLOW} ${BASDL} ${NC}"

	sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP $CRD:$DDL $DOWNLOADED
	FILE=$(ls $DOWNLOADED/$BASDL/GRANULE/)

	echo -e "${BLUE}Starting Process...${NC}"
	cd $PROGRAM
	./wipesen -f $DOWNLOADED/$BASDL/GRANULE/$FILE/MTD_TL.xml

	if mv $DOWNLOADED/$BASDL/GRANULE/$FILE/IMG_DATA/*.TIF $TREATED/ ;then
		echo -e "${BLUE}Moving datas to TREATED files ...${NC}"
	else
		echo -e "${RED}Error while processing data.${NC}"
		exit 3630
	fi

	echo "${BLUE}Removing datas from local storage${NC}"
	rm -r $DOWNLOADED/$BASDL


	#Log processed data
	echo ${DDL} >> $PRCC
	touch "$FOO.tmp"
	tail -n +2 "$FOO" > "$FOO.tmp" && mv "$FOO.tmp" "$FOO"

	echo "${WHITE}=====================================================================================${NC}"
done < $ALLD

rm -r $FOO
cp $PRCC $ALLD
rm -r $PRCC

base64 -d <<<"H4sIAAAAAAAAA52SQQ6EMAhF9z0Fu9HETG8zqyadg3B4+R/amtjRiahY4EGhKmJSIXIr19gkeoYTVCard9tdY5OoyglOdC/eGXUs/XGPrxtWJeAG0NtqH6a0zfVQl1U4X4GjoEMpVMy2i0asG6byCvhLoI4Mn9IMC4PIHe1VUutpBY9kKnSmnGjt644p9RKAjgwcJzKKfMTuPNBehefJM8jsX4t/BHttQoP+zc8Gpsp7OAGMjDAQzAU91IZGQsw3E+95IpOf4D9hxV/7KXuaR57t5xXTDrnCV7OAAwAA" | gunzip

