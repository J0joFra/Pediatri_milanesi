import streamlit as st
from pymongo import MongoClient
import folium
from streamlit_folium import st_folium
import json
import requests

# Connessione al database MongoDB
client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
db = client['Healthcare']
collection = db['Pediatri']

# Funzione per caricare i pediatri (come nel codice originale)
def load_pediatri():
    query = st.text_input("Cerca Pediatra", "")
    
    if query:
        # Cerca nei campi nome, zona, e specializzazione
        pediatri = collection.find({
            "$or": [{"Name_med": {"$regex": query, "$options": "i"}},
                    {"Surname_med": {"$regex": query, "$options": "i"}},
                    {"Address": {"$regex": query, "$options": "i"}}]
        }).limit(10)
    else:
        # Se non ci sono filtri, prendi solo i primi 10 pediatri
        pediatri = collection.find().limit(10)
    
    return pediatri

# Carica i pediatri e visualizzali
pediatri = load_pediatri()

# Crea la tabella in Streamlit
st.table([{
    'Codice': pediatra['Code_med'],
    'Nome': pediatra['Name_med'],
    'Cognome': pediatra['Surname_med'],
    'Indirizzo': pediatra['Address']
} for pediatra in pediatri])

# Carica il file GeoJSON della mappa di Milano da GitHub
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/J0joFra/Map-GeoJson/refs/heads/main/MilanCity.geojson"
    response = requests.get(url)
    return response.json()

geojson_data = load_geojson()

# Crea la mappa con Folium
st.subheader("Mappa delle Zone di Milano")

# Inizializza la mappa
map_center = [45.4642, 9.16]  # Milano
mymap = folium.Map(location=map_center, zoom_start=12)

# Funzione per visualizzare i marker dei pediatri
def show_pediatri_on_map(zone_name):
    zone_pediatri = collection.find({"Address": {"$regex": zone_name, "$options": "i"}})
    
    for pediatra in zone_pediatri:
        folium.Marker(
            [pediatra['Latitude'], pediatra['Longitude']],
            popup=f"{pediatra['Name_med']} {pediatra['Surname_med']}<br>{pediatra['Address']}"
        ).add_to(mymap)

# Aggiungi GeoJSON sulla mappa
def add_geojson_to_map(geojson_data):
    geojson = folium.GeoJson(geojson_data, name='geojson')
    
    # Funzione per gestire il click su una zona
    def on_zone_click(event):
        zone_name = event['layer']['feature']['properties']['name']
        st.write(f"Selezionata la zona: {zone_name}")
        show_pediatri_on_map(zone_name)
    
    geojson.add_to(mymap)
    
    # Aggiungi un evento di click sulle zone del GeoJSON
    geojson.on('click', on_zone_click)

add_geojson_to_map(geojson_data)

# Mostra la mappa con Streamlit
st_folium(mymap, width=700, height=500)
