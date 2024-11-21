import streamlit as st
from pymongo import MongoClient
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import requests
import json
import os

# Configura il layout di Streamlit
st.set_page_config(page_title="Healthcare - Pediatri Milano", 
                   page_icon="👶", 
                   layout="wide",  # Cambiato da "centered" a "wide"
                   initial_sidebar_state="expanded")

# Funzione per ottenere i dati meteo di Milano da OpenWeatherMap
def get_weather_data():
    api_key = "YOUR_API_KEY"  # Sostituisci con la tua chiave API
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

# Recupera i dati meteo
temperature, humidity, weather_description = get_weather_data()

# Aggiungi le metriche in tempo reale (se i dati sono disponibili)
if temperature is not None:
    st.metric(label="Temperatura", value=f"{temperature} °C", delta="1.2 °C")
    st.metric(label="Umidità", value=f"{humidity}%", delta="5%")
    st.metric(label="Condizioni Meteo", value=weather_description.capitalize())
else:
    st.warning("Impossibile ottenere i dati meteo. Riprova più tardi.")

# Il resto del tuo codice
# Connessione a MongoDB
client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
db = client['Healthcare']
collection = db['Pediatri']

# Funzione per visualizzare i dati dei pediatri
def load_pediatri(query="", selected_zone=None):
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
    return sorted(collection.distinct("Zone"))

# Intestazione della pagina
st.title("👶 Healthcare: Pediatri a Milano")
st.markdown("""
Benvenuti nel portale di ricerca pediatri a Milano. Qui puoi trovare informazioni sui pediatri freelance attivi nella tua zona, 
visualizzarli su una mappa interattiva e accedere ai dettagli degli indirizzi.
""")

# Filtri di ricerca
with st.sidebar:
    st.title("🔧 Filtri di Ricerca")
    query = st.text_input("🔍 Cerca Pediatra", "")
    zones = ["Tutte le Zone"] + get_zones()
    selected_zone = st.selectbox("📍 Seleziona una Zona", zones)

# Carica i pediatri in base alla ricerca e alla zona selezionata
pediatri = load_pediatri(query, selected_zone)

# Layout principale: Mappa
st.subheader("🗺️ Mappa dei Pediatri")
st.metric(label="Temperature", value="31 °C", delta="1.2 °C")
map_center = [45.4642, 9.16]  # Milano
mymap = folium.Map(location=map_center, zoom_start=12)

# Carica il file GeoJSON
geojson_path = "Datasets/MilanCity.geojson"
geojson_data = None
if os.path.exists(geojson_path):
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
        for feature in geojson_data['features']:
            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    'fillColor': '#00B4D8',
                    'fillOpacity': 0.3,
                    'weight': 0.5,
                    'color': 'black'
                }
            ).add_to(mymap)
else:
    st.warning("Il file GeoJSON non è stato trovato. La mappa sarà caricata senza zone evidenziate.")

# Aggiungi marker per i pediatri
for pediatra in pediatri:
    lat = pediatra.get('Lat')
    long = pediatra.get('Long')
    if lat and long:
        icon = folium.Icon(color='blue', icon='user-md', prefix='fa')  # Icona personalizzata
        folium.Marker(
            [lat, long], 
            popup=f"<b>{pediatra['Name_med']} {pediatra['Surname_med']}</b><br>{pediatra['Address']}<br><i>{pediatra['Zone']}</i>",
            icon=icon
        ).add_to(mymap)

st_folium(mymap, width=1000, height=700)

# Tabella pediatri
st.subheader("📋 Elenco Pediatri")
if pediatri:
    pediatri_df = pd.DataFrame([{
        'Codice': pediatra.get('Code_med'),
        'Nome': pediatra.get('Name_med'),
        'Cognome': pediatra.get('Surname_med'),
        'Indirizzo': pediatra.get('Address'),
        'Zona': pediatra.get('Zone')
    } for pediatra in pediatri])

    pediatri_df = pediatri_df.dropna()
    
    st.markdown("""
        <style>
        .dataframe-table {
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.dataframe(pediatri_df, use_container_width=True)
else:
    st.write("Nessun pediatra trovato con i criteri selezionati.")

# Statistiche sui pediatri
if pediatri:
    st.subheader("📊 Statistiche")
    zona_counts = pediatri_df['Zona'].value_counts().reset_index()
    zona_counts.columns = ['Zona', 'Numero Pediatri']
    fig = px.bar(zona_counts, x='Zona', y='Numero Pediatri', 
                 title="Numero di Pediatri per Zona", 
                 color='Zona', height=500)
    st.plotly_chart(fig)

# Suggerimenti
with st.sidebar:
    st.info(""" 
    💡 **Suggerimenti di utilizzo:**  
    - Usa il campo di ricerca per filtrare i pediatri per nome, cognome o indirizzo.  
    - Seleziona una zona per visualizzare i pediatri di quell'area.  
    - Clicca sui marker della mappa per ulteriori dettagli.
    """)
