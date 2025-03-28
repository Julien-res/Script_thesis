import pandas as pd
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from tqdm import tqdm  # Importer tqdm pour la barre de progression

# Charger le fichier Excel
file_path = "/mnt/c/Travail/DATA_AGGREGATION/DATA__LIGHT.xlsx"  # Remplacez par le chemin réel de votre fichier
data = pd.read_excel(file_path)

# Initialiser TimezoneFinder
tf = TimezoneFinder()

# Fonction pour convertir en UTC en fonction des coordonnées
def convert_to_utc(row):
    try:
        if pd.isna(row['Hour']):  # Vérifier si l'heure est manquante
            return None
        lat, lon = row['Lat'], row['Lon']
        local_tz_name = tf.timezone_at(lng=lon, lat=lat)
        if not local_tz_name:
            return None
        local_tz = pytz.timezone(local_tz_name)
        local_datetime = datetime.combine(row['Date'], datetime.strptime(row['Hour'], "%H:%M:%S").time())
        local_datetime = local_tz.localize(local_datetime)
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime.time()  # Retourner uniquement l'heure UTC
    except Exception as e:
        return None

def convert_to_utc_day(row):
    try:
        if pd.isna(row['Hour']):  # Vérifier si l'heure est manquante
            return None
        lat, lon = row['Lat'], row['Lon']
        local_tz_name = tf.timezone_at(lng=lon, lat=lat)
        if not local_tz_name:
            return None
        local_tz = pytz.timezone(local_tz_name)
        local_datetime = datetime.combine(row['Date'], datetime.strptime(row['Hour'], "%H:%M:%S").time())
        local_datetime = local_tz.localize(local_datetime)
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime.date()  # Retourner uniquement la date UTC
    except Exception as e:
        return None

# Ajouter une barre de progression
tqdm.pandas(desc="Conversion en UTC")  # Initialiser tqdm avec une description
data['UTC Time'] = data.progress_apply(convert_to_utc, axis=1)
data['Day_UTC'] = data.progress_apply(convert_to_utc_day, axis=1)

# Sauvegarder dans un nouveau fichier
output_file = file_path.replace(".xlsx", "_UTC.csv")
data.to_csv(output_file, index=False)

print(f"Conversion terminée. Fichier sauvegardé sous : {output_file}")
