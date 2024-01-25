#!/bin/bash

export PATH=~/snap/bin:$PATH
gptPath=~/snap/bin/gpt
graphXmlPath=~/Script/C2RCC/Graph_C2RCC.xml # path to the graph xml
parameterFilePath= # path to a parameter file
sourceDirectory=/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/S2_PEPS_L1C/New_data/2015 # path to source products
targetDirectory=/nfs/data/unprotected/log/cverpoorter/VolTransMESKONG/S2_PEPS/New_data_C2RCC_MSI_20m/ # path to target products
targetFilesuffix="C2RCC_20m" # a file prefix for the target product name, typically indicating the type of processing
ancillaryPath="/nfs/home/log/jmasson/Script/Ancillary" # path where are stored ancillary data from NCEP/TOMSOMI/AURAOMI retrieved on NASA server
#====================================================================

# HIC SVNT LEONES. MODIFY WITH CAUTION.

removeExtension() {
    file="$1"
    echo "$(echo "$file" | sed -r 's/\.[^\.]*$//')"
}

# Create the target directory
mkdir -p "${targetDirectory}"

for F in $(find "${sourceDirectory}" -name "S2*.SAFE"); do
  sourceFile="$(realpath "$F")"
  targetFile="${targetDirectory}/$(removeExtension "$(basename ${F})")_${targetFilesuffix}.tif"
  if [ ! -f "$targetFile" ];then
    ${gptPath} ${graphXmlPath} -e -t ${targetFile} -p ${ancillaryPath} -f 'GeoTIFF' ${sourceFile}
  fi
done