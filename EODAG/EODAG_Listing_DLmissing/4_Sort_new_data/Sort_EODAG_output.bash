#!/bin/bash
shopt -s extglob

FILE=/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/S2_PEPS_L1C/New_data/
SLASH=/
liste=$(ls $FILE)
for cddirect in ${liste[*]};do
	if [[ $cddirect == 'S2'* ]]; then
		cd $FILE$cddirect$SLASH
		listee=$(ls)
		for string in ${listee[*]};do
			year=$(echo $string | cut -c 12-15)
			month=$(echo $string | cut -c 16-17)
			mv $FILE$cddirect$SLASH$string $FILE$year$SLASH$month$SLASH
			rmdir $FILE$cddirect
		done
	fi
done