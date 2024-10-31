import urllib.request
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime
import pymongo

# Funzione per caricare il dataset JSON dai dati online
def load_data(url):
    fileobj = urllib.request.urlopen(url)
    data = json.load(fileobj)
    return pd.DataFrame(data["result"]["records"])

# Funzione per capitalizzare le colonne e i valori stringa
def title_columns_and_values(df):
    df.columns = [col.title() for col in df.columns]
    df = df.applymap(lambda x: x.title() if isinstance(x, str) else x)
    return df

# Funzione per rinominare le colonne
def rename_columns(df):
    return df.rename(columns={
        "Idmedico": "ID_med",
        "Nomemedico": "Name_med",
        "Cognomemedico": "Surname_med",
        "Nil": "Zone",
        "Long_x_4326": "Long",
        "Lat_y_4326": "Lat",
        "Codice_regionale_medico": "Code_med",
        'Datanascita': "Age",
        "Tipomedico": "Type_med",
        "Attivo": "Open",
        "Ambulatorioprincipale": "Main_amb",
        "Luogo_ambulatorio": "L_ambul"
    })

# Funzione per creare la colonna 'Age' calcolata dalla data di nascita
def calculate_age(df):
    today = datetime.today()
    df['Age'] = df['Age'].apply(lambda x: today.year - datetime.strptime(x.split("t")[0], '%Y-%m-%d').year - 
                                 ((today.month, today.day) < (datetime.strptime(x.split("t")[0], '%Y-%m-%d').month,
                                                              datetime.strptime(x.split("t")[0], '%Y-%m-%d').day)) 
                                 if pd.notna(x) else None)
    return df

# Funzione per creare la colonna combinata 'Address'
def create_address_column(df):
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
    return df

# Funzione per eliminare le colonne non necessarie
def drop_unnecessary_columns(df):
    return df.drop(['_id', 'Via', 'Civico', 'L_ambul', 'Location'], axis=1)

# Funzione per creare la colonna geometrica nel dataset
def create_geometry_column(df):
    geometry = [Point(xy) for xy in zip(df['Long'], df['Lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    return gdf.set_crs("EPSG:4326")

# Funzione per caricare il file GeoJSON con le aree di Milano
def load_geojson(path):
    return gpd.read_file(path).to_crs("EPSG:4326")

# Funzione per ottenere i valori unici della colonna 'name' dal GeoJSON
def get_unique_zone_names(gdf_zones):
    unique_names = gdf_zones['name'].unique()
    print("Valori unici della colonna 'name':")
    print(unique_names)
    return unique_names

# Funzione per effettuare il join spaziale e aggiornare le zone
def spatial_join_update_zones(gdf_data, gdf_zones):
    gdf_joined = gpd.sjoin(gdf_data, gdf_zones, how="left", predicate="within")
    gdf_data['Zone'] = gdf_joined['name']
    return gdf_data

# Funzione per creare un database MongoDB e inserire il dataframe
def create_mongo_db(dataframe):
    # Connessione al server MongoDB
    client = pymongo.MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
    
    # Creazione di un database chiamato "Healthcare"
    db = client["Healthcare"]
    collection = db["Pediatri"]
    
    # Svuota la collezione se esiste
    collection.delete_many({})
    
    # Converti il dataframe in un dizionario e inserisci nel database
    data_dict = dataframe.to_dict("records")
    collection.insert_many(data_dict) 
    print(f"Inseriti {len(data_dict)} documenti nella collezione 'Pediatri'.")
    
# Funzione principale per eseguire tutte le operazioni
def main():
    url = 'https://dati.comune.milano.it/api/3/action/datastore_search?resource_id=22b05e1f-c5d2-4468-90e5-c098977856ef'
    geojson_path = "Datasets/MilanCity.geojson"
    
    # Carica il dataset
    df = load_data(url)
    
    # Preprocessa il dataset
    df = title_columns_and_values(df)
    df = rename_columns(df)
    df = calculate_age(df)
    df = create_address_column(df)
    df = drop_unnecessary_columns(df)
    
    # Crea la colonna geometrica e imposta il CRS
    gdf_data = create_geometry_column(df)
    
    # Carica il file GeoJSON e ottieni i valori unici delle zone
    gdf_zones = load_geojson(geojson_path)
    get_unique_zone_names(gdf_zones)
    
    # Effettua il join spaziale e aggiorna le zone
    gdf_data = spatial_join_update_zones(gdf_data, gdf_zones)
    
    dataframe = df
    create_mongo_db(dataframe)

# Esegui la funzione principale
main()

