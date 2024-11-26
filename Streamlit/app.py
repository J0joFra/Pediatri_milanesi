import streamlit as st
from pymongo import MongoClient
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import requests
import json
import os
import urllib.request
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pymongo

# Funzione per ottenere i dati meteo di Milano da OpenWeatherMap
def get_weather_data():
    api_key = "155d1ef020301577c38d5347ed538061"
    city = "Milan"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        weather_description = data['weather'][0]['description']
        return temperature, humidity, weather_description
    else:
        return None, None, None

# Funzione per caricare il dataset JSON dai dati online
def load_data(url):
    fileobj = urllib.request.urlopen(url)
    data = json.load(fileobj)
    return pd.DataFrame(data["result"]["records"])

# Funzione per capitalizzare le colonne e i valori stringa
def title_columns_and_values(df):
    df.columns = [col.capitalize() for col in df.columns]
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

# Funzione per calcolare l'età dal campo data di nascita
def calculate_age(df):
    today = datetime.today().date()
    df['Age'] = df['Age'].apply(lambda x: datetime.strptime(x.split("T")[0], '%Y-%m-%d').date() if pd.notna(x) else None)
    df['Age'] = df['Age'].apply(lambda birth_date: relativedelta(today, birth_date).years if birth_date else None)
    return df

# Funzione per creare la colonna combinata 'Address' 
def create_address_column(df):
    def create_address(row):
        parts = []
        if 'Via' in row and pd.notna(row['Via']):
            parts.append(row['Via'])
        if 'Civico' in row and pd.notna(row['Civico']):
            parts.append(row['Civico'])
        if 'L_ambul' in row and pd.notna(row['L_ambul']):
            parts.append(row['L_ambul'])
        return ', '.join(parts)
    df['Address'] = df.apply(create_address, axis=1).str.title()
    return df

# Funzione per eliminare colonne non necessarie
def drop_unnecessary_columns(df):
    columns_to_drop = ['_id', 'Via', 'Civico', 'L_ambul', 'Location']
    existing_columns = [col for col in columns_to_drop if col in df.columns]
    return df.drop(existing_columns, axis=1)

# Funzione per creare la colonna geometrica nel dataset
def create_geometry_column(df):
    geometry = [Point(xy) for xy in zip(df['Long'], df['Lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    return gdf.set_crs("EPSG:4326")

# Funzione per caricare il file GeoJSON con le aree di Milano
def load_geojson(path):
    return gpd.read_file(path).to_crs("EPSG:4326")

# Funzione per effettuare il join spaziale e aggiornare le zone
def spatial_join_update_zones(gdf_data, gdf_zones):
    gdf_joined = gpd.sjoin(gdf_data, gdf_zones, how="left", predicate="within")
    gdf_data['Zone'] = gdf_joined['name']
    return gdf_data

# Funzione per creare il database MongoDB
def create_mongo_db(dataframe):
    client = pymongo.MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
    db = client["Healthcare"]
    collection = db["Pediatri"]
    collection.delete_many({})
    data_dict = dataframe.to_dict("records")
    collection.insert_many(data_dict) 
    print(f"Inseriti {len(data_dict)} documenti nella collezione 'Pediatri'.")

# Funzione per caricare i pediatri da MongoDB
def load_pediatri(query="", selected_zone=None):
    client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
    db = client['Healthcare']
    collection = db['Pediatri']
    filter_criteria = {}
    if query:
        filter_criteria["$or"] = [
            {"Name_med": {"$regex": query, "$options": "i"}},
            {"Surname_med": {"$regex": query, "$options": "i"}},
            {"Address": {"$regex": query, "$options": "i"}}
        ]
    if selected_zone and selected_zone != "Tutte le Zone":
        filter_criteria["Zone"] = selected_zone
    pediatri = collection.find(filter_criteria)
    return list(pediatri)

# Recupera tutte le zone uniche dal database
def get_zones():
    client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
    db = client['Healthcare']
    collection = db['Pediatri']
    return sorted(collection.distinct("Zone"))

# Funzione per creare box colorati per le metriche
def metrics_html(label, value, color):
    return f"""
    <div style="background-color: {color}; padding: 10px; border-radius: 8px; box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1); text-align: center; color: white; margin-bottom: 2px;">
        <h4 style="margin: 0; font-size: 14px;">{label}</h4>
        <p style="margin: 0; font-size: 18px; font-weight: bold;">{value}</p>
    </div>
    """

# Recupera i dati meteo
temperature, humidity, weather_description = get_weather_data()

# Configura il layout di Streamlit
st.set_page_config(page_title="Healthcare - Pediatri Milano", page_icon="👶", layout="wide", initial_sidebar_state="expanded")

# Intestazione della pagina
st.title("👶 Healthcare: Pediatri a Milano")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(""" ... """)  # Insert your page description here

with col2:
    if temperature is not None:
        st.markdown(metrics_html("🌡️ Temperatura", f"{temperature} °C", "#829CBC"), unsafe_allow_html=True)
    if humidity is not None:
        st.markdown(metrics_html("💧 Umidità", f"{humidity}%", "#7796CB"), unsafe_allow_html=True)
    if weather_description is not None:
        st.markdown(metrics_html("☁️ Condizioni Meteo", weather_description.capitalize(), "#6798C0"), unsafe_allow_html=True)

# Input per query e selezione zona
st.sidebar.subheader("🔍 Ricerca")
query = st.sidebar.text_input("Cerca pediatra (Nome, Cognome, Indirizzo):", "")
zones = ["Tutte le Zone"] + get_zones()  
selected_zone = st.sidebar.selectbox("Seleziona Zona:", zones)

# Carica i pediatri in base alla ricerca e alla zona selezionata
pediatri = load_pediatri(query, selected_zone)

# Visualizza la mappa con i pediatri
milan_map = folium.Map(location=[45.4642, 9.1900], zoom_start=12)
for pediatra in pediatri:
    folium.Marker(
        location=[pediatra["Lat"], pediatra["Long"]],
        popup=f"Nome: {pediatra['Name_med']} {pediatra['Surname_med']}<br>Indirizzo: {pediatra['Address']}<br>Zona: {pediatra['Zone']}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(milan_map)
st_folium(milan_map, width=800, height=600)

# Statistiche sulla presenza dei pediatri nelle zone
zone_counts = pd.DataFrame(pediatri)['Zone'].value_counts()
no_pediatri_zones = [zone for zone in get_zones() if zone not in zone_counts.index]
st.sidebar.subheader("📊 Statistiche")
st.sidebar.write(f"**Pediatri per zona:**")
st.sidebar.write(zone_counts)
st.sidebar.write(f"**Zone senza pediatri:** {', '.join(no_pediatri_zones)}")

# Visualizza il download CSV
if len(pediatri) > 0:
    df = pd.DataFrame(pediatri)
    csv = df.to_csv(index=False)
    st.download_button("Scarica i dati in CSV", csv, "pediatri_milano.csv", "text/csv", key="download-csv")
