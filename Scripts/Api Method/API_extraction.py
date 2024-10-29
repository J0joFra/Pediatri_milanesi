import urllib.request
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# URL del dataset
url = 'https://dati.comune.milano.it/api/3/action/datastore_search?resource_id=22b05e1f-c5d2-4468-90e5-c098977856ef&limit=5'
fileobj = urllib.request.urlopen(url)
data = json.load(fileobj)
records = data["result"]["records"]

# Crea il DataFrame
df = pd.DataFrame(records)

# Capitalizza i titoli delle colonne e i valori stringa
df.columns = [col.capitalize() for col in df.columns]
df = df.applymap(lambda x: x.capitalize() if isinstance(x, str) else x)

# Rinomina le colonne
df = df.rename(columns={
    "Idmedico": "ID_med",
    "Nomemedico": "Name_med",
    "Cognomemedico": "Surname_med",
    "Nil": "Zone",
    "Long_x_4326": "Long",
    "Lat_y_4326": "Lat",
    "Codice_regionale_medico": "Code_med",
    'DataNascita': "Age",
    "Tipomedico": "Type_med",
    "Attivo": "Open",
    "Ambulatorioprincipale": "Main_amb",
    "Luogo_ambulatorio": "L_ambul"
})

# Crea la colonna combinata 'Address' con 'Via', 'Civico' e 'Luogo_ambulatorio'
def create_address(row):
    parts = []
    if pd.notna(row['Via']) and row['Via']:
        parts.append(row['Via'])
    if pd.notna(row['Civico']) and row['Civico']:
        parts.append(row['Civico'])
    if pd.notna(row['L_ambul']) and row['L_ambul']:
        parts.append(row['L_ambul'])
    return ', '.join(parts)

df['Address'] = df.apply(create_address, axis=1).str.title()

# Elimina colonne non necessarie
df = df.drop(['_id', 'Via', 'Civico', 'L_ambul', 'Location'], axis=1)

# Carica il file GeoJSON con le aree di Milano
geojson_path = "Datasets/MilanCity.geojson"
gdf_zones = gpd.read_file(geojson_path)

# Crea una colonna di geometria nel dataset basata sulle coordinate
geometry = [Point(xy) for xy in zip(df['Long'], df['Lat'])]
gdf_data = gpd.GeoDataFrame(df, geometry=geometry)

# Imposta il sistema di riferimento (assicurati che sia corretto per entrambi i file)
gdf_data = gdf_data.set_crs("EPSG:4326")  # Imposta il CRS a WGS84
gdf_zones = gdf_zones.to_crs("EPSG:4326")  # Stesso CRS per il GeoJSON

# Effettua un join spaziale per trovare la zona per ogni punto in base al file GeoJSON
gdf_joined = gpd.sjoin(gdf_data, gdf_zones, how="left", op="within")

# Aggiorna le zone del dataset con i nomi derivati dal GeoJSON
df['Zone'] = gdf_joined['nome_zona_geojson'] 

# Visualizza i dati aggiornati
print(df[['ID_med', 'Name_med', 'Surname_med', 'Zone', 'Address', 'Long', 'Lat']])
