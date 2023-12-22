#!/bin/bash
shopt -s extglob
FILE=/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_THEIA/RAW/
SLASH=/
cd $FILE
liste=$(ls)
for year in ${liste[*]};do
	cd $FILE$year$SLASH
	listee=$(ls)
	for month in ${listee[*]};do
		cd $FILE$year$SLASH$month$SLASH
		listeee=$(ls -d -- !(*.bz2*))
		for file in  ${listeee[*]};do
			tar jcvf $file.bz2 $file --remove-files
		done
	done
done