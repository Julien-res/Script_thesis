#!/bin/bash
shopt -s extglob
FILE=/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/Landsat/RAW/
SLASH=/
liste=$(ls $FILE)
for year in ${liste[*]};do
	listee=$(ls $FILE$year$SLASH)
	for month in ${listee[*]};do
		listeee=$(ls $FILE$year$SLASH$month$SLASH -I "*.bz2*")
		for file in  ${listeee[*]};do
			tar jcvf $FILE$year$SLASH$month$SLASH$file.bz2 $FILE$year$SLASH$month$SLASH$file --remove-files
		done
	done
done
