import pandas as pd
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# Charger le fichier Excel
file_path = "/mnt/c/Users/Julien Masson/Downloads/heure_to_utc_2.xlsx"  # Remplacez par le chemin réel de votre fichier
data = pd.read_excel(file_path)
# Initialiser TimezoneFinder
tf = TimezoneFinder()

# Définir le fuseau horaire local (Eastern Time)
eastern_tz = pytz.timezone('US/Eastern')
# Fonction pour convertir en UTC
# Fonction pour convertir en UTC en fonction des coordonnées
def convert_to_utc(row):
    try:
        # Récupérer les coordonnées
        lat, lon = row['Lat'], row['Lon']
        # Obtenir le fuseau horaire local en fonction des coordonnées
        local_tz_name = tf.timezone_at(lng=lon, lat=lat)
        if not local_tz_name:
            return "Fuseau horaire non trouvé"
        # Charger le fuseau horaire
        local_tz = pytz.timezone(local_tz_name)
        # Créer une date et heure locale
        local_datetime = datetime.combine(row['Date'], row['Hour'])
        local_datetime = local_tz.localize(local_datetime)  # Localiser dans le fuseau horaire local
        # Convertir en UTC
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime.time()
    except Exception as e:
        return f"Erreur: {e}"

def convert_to_utc_day(row):
    try:
        # Récupérer les coordonnées
        lat, lon = row['Lat'], row['Lon']
        # Obtenir le fuseau horaire local en fonction des coordonnées
        local_tz_name = tf.timezone_at(lng=lon, lat=lat)
        if not local_tz_name:
            return "Fuseau horaire non trouvé"
        # Charger le fuseau horaire
        local_tz = pytz.timezone(local_tz_name)
        # Créer une date et heure locale
        local_datetime = datetime.combine(row['Date'], row['Hour'])
        local_datetime = local_tz.localize(local_datetime)  # Localiser dans le fuseau horaire local
        # Convertir en UTC
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime.date()
    except Exception as e:
        return f"Erreur: {e}"

# Appliquer la conversion
data['UTC Time'] = data.apply(convert_to_utc, axis=1)
data['Day_UTC'] = data.apply(convert_to_utc_day, axis=1)
# Sauvegarder dans un nouveau fichier
output_file = "/mnt/c/Users/Julien Masson/Downloads/test_heure_to_utc_converted_2.xlsx"
data.to_excel(output_file, index=False)

print(f"Conversion terminée. Fichier sauvegardé sous : {output_file}")
