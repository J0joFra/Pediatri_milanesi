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
                   layout="wide",
                   initial_sidebar_state="expanded")

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
# Recupera i dati meteo
temperature, humidity, weather_description = get_weather_data()
col1, col2, col3 = st.columns(3)

with col1:
    if temperature is not None:
        st.metric(label="🌡️ Temperatura", value=f"{temperature} °C")
    else:
        st.warning("Impossibile ottenere i dati meteo. Riprova più tardi.")

with col2:
    if humidity is not None:
        st.metric(label="💧 Umidità", value=f"{humidity}%")

with col3:
    if weather_description is not None:
        st.metric(label="☁️ Condizioni Meteo", value=weather_description.capitalize())

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
        icon = folium.Icon(color='blue', icon='user-md', prefix='fa')
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
    
    st.dataframe(pediatri_df, use_container_width=True)
else:
    st.write("Nessun pediatra trovato con i criteri selezionati.")

# Statistiche sui pediatri con una mini-dashboard
if pediatri:
    st.subheader("📊 Statistiche sui Pediatri")
    
    total_zones = 85  # Numero totale delle zone da GeoJSON
    pediatri_per_zone = pediatri_df['Zona'].value_counts()
    zones_no_pediatri = total_zones - len(pediatri_per_zone)

    stats = {
        '1 Pediatra': (pediatri_per_zone == 1).sum(),
        '2 Pediatri': (pediatri_per_zone == 2).sum(),
        '2 o più Pediatri': (pediatri_per_zone > 2).sum(),
        'Senza Pediatri': zones_no_pediatri
    }

    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="🏥 Totale Pediatri", value=len(pediatri_df))
        st.metric(label="📍 Zone Coperte", value=len(pediatri_per_zone))
        st.metric(label="🚫 Zone Senza Pediatri", value=zones_no_pediatri)

    with col2:
        fig_pie = px.pie(
            names=stats.keys(),
            values=stats.values(),
            title="<b>Distribuzione Zone per Pediatri</b>",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Aggrnyl
        )
        fig_pie.update_traces(
            textinfo='percent',
            textfont_size=20,
            marker=dict(
                line=dict(color='#000000', width=1.5)
            )
        )
        fig_pie.update_layout(
            title=dict(
                font_size=20,
                x=0.2  # Centra il titolo
            ),
            legend=dict(
                font=dict(size=14), 
                orientation="h",
                x=0.2,
                xanchor='center',
                y=-0.1
            ),
            margin=dict(t=50, b=30, l=10, r=10) 
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.download_button(
    label="📥 Scarica come CSV",
    data=pediatri_df.to_csv(index=False).encode('utf-8'),
    file_name='pediatri_milano.csv',
    mime='text/csv'
)
