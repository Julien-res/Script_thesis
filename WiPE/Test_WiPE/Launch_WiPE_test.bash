#!/bin/bash

set -e
shopt -s globstar
base64 -d <<<"H4sIAAAAAAAAA3WOwQ2AUAhD73+KHvXEQiZdpMNLi19PlpAGeBAAkHjFLmhhjFjdvToeFQ6e2bk0jEwMUs4OCmJjsR6GMFJwlgdZrpg28d0IIbdy4/kjyNzoAcUh5lNt4l/rBjwToz/uAAAA" | gunzip

# MODIFY DEPENDING YOUR INSTALLATION
#=======================================================
ALLD="/mnt/c/Travail/TEST/Test_WiPE/2017/Datatotread.data" # Location of the list of file location (use 'find' command in UNIX) (required to be a text format with .data at the end of name)
#eg : in an interactive console, launch this command before this bash : "find /nfs/data/path -name 'S2A_*.SAFE' -o -name 'S2B_*.SAFE' > /nfs/data/path/Datatotread.data" to create the specific list
PROGRAM="/mnt/c/Travail/Script/WiPE/wipesen_2024_03/" # Location of wipesen program
TREATED="/mnt/c/Travail/TEST/Test_WiPE/2017/NEW/" # Where to output treated datas
#=======================================================
# AFTER THIS, HIC SVNT LEONES. MODIFY WITH CAUTION.

# Color to be used for different messages
BLUE='\033[1;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
WHITE='\033[47m'
NC='\033[0m'


# Ensure that the program can be run multiple times without reprocessing datas that are already processed

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

	echo -e "${BLUE}Starting Process...${NC}"
	cd $PROGRAM
    
	./wipesen -f $DDL

    DIRECT=$(dirname $DDL)

	if mv $DIRECT/IMG_DATA/*_water.TIF $TREATED ;then
		echo -e "${BLUE}Moving datas to TREATED files ...${NC}"
	else
		echo -e "${RED}Error while processing data.${NC}"
		exit 3630
	fi

	echo -e "${BLUE}Removing RC datas from local storage${NC}"
	rm -r $DIRECT/IMG_DATA/*.TIF


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
