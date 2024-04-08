#!/bin/bash
set -e
source ~/anaconda3/etc/profile.d/conda.sh
conda activate polymer


ANCILLARY="/mnt/c/Travail/Script/Script_thesis/Ancillary/ANCILLARY/" # where to output Ancillaries
CREDENTIAL="/mnt/c/Travail/Script/Script_thesis/Polymer/LOCAL/credential" # Where .credential are stored (CALCULCO password in privateKey.credential and earthdata.credential)
ALLD="/mnt/c/Travail/Script/Script_thesis/Ancillary/xml_list.data" #Path of the .xml list
TMP="/mnt/c/Travail/Script/Script_thesis/Ancillary/TMP"  # Where to output downloaded datas
MAINPY="/mnt/c/Travail/Script/Script_thesis/Ancillary"
CRD="cverpoorter@calculco.univ-littoral.fr" # Account to ssh login
cd $MAINPY
#=======================================================
# AFTER THIS, HIC SVNT LEONES. MODIFY WITH CAUTION.

chmod 0777 $ANCILLARY
chmod 0600 $CREDENTIAL
chmod 0777 $ALLD
chmod 0777 $TMP
chmod 0777 $MAINPY

BLUE='\033[1;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
WHITE='\033[47m'
GREEN='\033[0;32m'
NC='\033[0m'


PRCC=${ALLD%"$(basename $ALLD)"}
PRCC+="Ancillary_alr_ddl.data"

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
chmod 0777 $ANCILLARY

echo -e "${RED}Trying to reach NASA for ancillaries ...${NC}"
touch $MAINPY/.netrc
USERNAME=$(sed "1!d" $CREDENTIAL/earthdata.credential)
PASSWORD=$(sed "2!d" $CREDENTIAL/earthdata.credential)
USERNAME=$(echo $USERNAME| cut -c 1-30)
echo "machine urs.earthdata.nasa.gov login ${USERNAME} password ${PASSWORD}" > $MAINPY/.netrc
chmod 0600 $MAINPY/.netrc
echo -e "${RED}OK!${NC}"

# Start of the loop that read all line of provided data list
sleep 5s
while IFS= read -r path; do

	echo -e "${YELLOW}Text read from file: $path ${NC}"
	sleep 1s
	pathmin=$(echo $path | cut -d'/' -f13-)
	pathmin=$(echo $pathmin | rev | cut -d'/' -f2- | rev)
	TMPA="/mnt/c/Travail/Script/Script_thesis/Ancillary/TMP/${pathmin}/"
	mkdir -p $TMPA

	rm $MAINPY/.urs_cookies
	touch $MAINPY/.urs_cookies
	cd $MAINPY

	echo -e "${BLUE}Downloading .xml ... ${NC}"
	sshpass -f $CREDENTIAL/privateKey.credential rsync -aquzP $CRD:$path $TMPA

	number=$(echo "$pathmin" | cut -c12-15)

	if [ "$number" -gt 2022 ];then
		echo -e "${RED}Year after 2022. The program won't use AURAOMI or TOMSOMI ... ${NC}"
		cp $MAINPY/ancillary_2023.py $MAINPY/ancillary.py
	else
		echo -e "${GREEN}Year before 2022. The program will use AURAOMI or TOMSOMI if possible ... ${NC}"
		cp $MAINPY/ancillary_bf2023.py $MAINPY/ancillary.py
	fi

	python3 $MAINPY/Main.py -i $TMPA -o $ANCILLARY

	echo -e "${BLUE}Removing datas from local storage${NC}"
	rm -r $TMP/*

	sleep 1s
	#Log processed data
	echo ${path} >> $PRCC
	touch "$FOO.tmp"
	tail -n +2 "$FOO" > "$FOO.tmp" && mv "$FOO.tmp" "$FOO"
	echo -e "${WHITE}=====================================================================================${NC}"
done < $ALLD



rm -r $FOO
cp $PRCC $ALLD
rm -r $PRCC

base64 -d <<<"H4sIAAAAAAAAA52SQQ6EMAhF9z0Fu9HETG8zqyadg3B4+R/amtjRiahY4EGhKmJSIXIr19gkeoYTVCard9tdY5OoyglOdC/eGXUs/XGPrxtWJeAG0NtqH6a0zfVQl1U4X4GjoEMpVMy2i0asG6byCvhLoI4Mn9IMC4PIHe1VUutpBY9kKnSmnGjt644p9RKAjgwcJzKKfMTuPNBehefJM8jsX4t/BHttQoP+zc8Gpsp7OAGMjDAQzAU91IZGQsw3E+95IpOf4D9hxV/7KXuaR57t5xXTDrnCV7OAAwAA" | gunzip
