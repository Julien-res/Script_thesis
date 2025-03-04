#!/bin/bash 
set -e
# MODIFY DEPENDING YOUR INSTALLATION
BLUE='\033[1;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[1;32m'
WHITE='\033[47m'
NC='\033[0m'
base64 -d <<<"H4sIAAAAAAAAA7WVwQ3DMAhF75G6gzfwPbMgeRGrs9cQwBhIaqlqDq3L9+fVQJJS5Gp4leT6WXgduqyAnxAtvwuTUs8T8B8EEwpptn1BKUM5Ky28B848Gzo2BaEIpNVY6RxDuTYFpggkr3SGIceucFEUctObmI0cY+OeQBQDyXsTKq0Bj8kFpHiI9kaGPlTaBGBHGBQ+Ywu9oQUklV4C9M1ljsLleB19/OhZb3jqgYWZzQY4GyYo3fVkOphiTqK94c0aACNIQDZ0TNb9KdQxKkaxbAAWYQQA69pQoEWrfkMJGHZg9+FqWZwyI8RHQroh6YlOMm22AyA5VWgpRDY4h58JuSs5Fu+Xu2eYxaz/IvRkUuTosTpfMe93cjzbE0O5b8FXTHY879Anf6jwYkpfPI+YxTHfYqHCVkjoz5jVYd7IocJqepqyLYeh/PE6Pg94QOzDCAAA" | gunzip

echo -e "${BLUE}Based on Ngoc et al. (2019)"
echo -e "Code by : Julien Masson - LOG UMR CNRS 8187"
echo -e "Require a working SNAP installation (SNAP 11.01 or higher)${NC}"
# Initialize conda
eval "$(conda shell.bash hook)"
# Activate the SNAP environment
conda activate SNAP


INPUT="/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/Match_up/1_RAW/"
OUTPUT="/work/users/cverpoorter/VolTransMESKONG/Data/S2_PEPS/Match_up/2_1_WIPE/"
METHOD="Other"
PROGRAM="/work/users/cverpoorter/VolTransMESKONG/Code/Code_WiPE/WiPE_personal/Python_Dev/" # Location of main.py
RESOLUTION=10 #Resolution required for output (10 20 or 60m)
#=======================================================
# AFTER THIS, HIC SVNT LEONES. MODIFY WITH CAUTION.

# Verify that files are all accessible
chmod 0777 $INPUT
chmod 0777 $OUTPUT
chmod 0777 $PROGRAM

cd $PROGRAM



if [ ! -d "$INPUT" ]; then
  echo -e "${RED}Le dossier INPUT spécifié n'existe pas : $INPUT ${NC}"
  exit 1
fi

# Rechercher les dossiers dans le dossier INPUT commençant par "S2A" ou "S2B" et ne contenant pas ".zip"
SAFE_FILES=($(find "$INPUT" -type d \( -name "S2A*" -o -name "S2B*" \) ! -path "*.zip"))
if [ ${#SAFE_FILES[@]} -eq 0 ]; then
  echo -e "${RED}Aucun dossier .SAFE commençant par S2A ou S2B trouvé dans le répertoire $INPUT. ${NC}"
  exit 1
fi

# Parcourir chaque fichier .SAFE trouvé
for SAFE_PATH in "${SAFE_FILES[@]}"; do
  # Extraire le nom du fichier sans l'extension
  SAFE_NAME=$(basename "$SAFE_PATH" .SAFE)
  
  # Lancer la commande Python avec l'argument -n pour le nom
  echo -e "${YELLOW}Lancement de WiPE pour $SAFE_NAME...${NC}"
  python main.py -i "$SAFE_PATH" -o "$OUTPUT" -m "$METHOD" -r "$RESOLUTION" -n "$SAFE_NAME"
done

echo -e "${GREEN}Toutes les commandes ont été exécutées. ${NC}"
