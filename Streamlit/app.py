import streamlit as st
from pymongo import MongoClient
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import json
import os

# Configura il layout di Streamlit
st.set_page_config(page_title="Healthcare - Pediatri Milano", 
                   page_icon="👶", 
                   layout="wide",
                   initial_sidebar_state="expanded")

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
st.write("""
Benvenuti nel portale di ricerca pediatri a Milano. Qui puoi trovare informazioni sui pediatri freelance attivi nella tua zona, 
visualizzarli su una mappa interattiva e accedere ai dettagli degli indirizzi.
""")

# Filtri di ricerca
st.sidebar.title("🔧 Filtri di Ricerca")
query = st.sidebar.text_input("🔍 Cerca Pediatra", "")
zones = ["Tutte le Zone"] + get_zones()
selected_zone = st.sidebar.selectbox("📍 Seleziona una Zona", zones)

# Carica i pediatri in base alla ricerca e alla zona selezionata
pediatri = load_pediatri(query, selected_zone)

# Mappa interattiva e Elenco Pediatri in colonne
col1, col2 = st.columns([2, 1])  # La mappa prende 2/3 dello spazio

# Inizializza la mappa con Milano come centro
map_center = [45.4642, 9.16]  # Milano
mymap = folium.Map(location=map_center, zoom_start=12)

# Carica il file GeoJSON
geojson_path = "MilanCity.geojson"
if os.path.exists(geojson_path):
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)

    # Evidenzia le zone sulla mappa
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
    st.error("Il file GeoJSON non è stato trovato.")

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

# Visualizza la mappa
with col1:
    st.subheader("🗺️ Mappa dei Pediatri")
    st_folium(mymap, width=900, height=500)

# Elenco pediatri
with col2:
    st.subheader("📋 Elenco Pediatri")
    if pediatri:
        st.table([{
            'Codice': pediatra['Code_med'],
            'Nome': pediatra['Name_med'],
            'Cognome': pediatra['Surname_med'],
            'Indirizzo': pediatra['Address'],
            'Zona': pediatra['Zone']
        } for pediatra in pediatri])
    else:
        st.write("Nessun pediatra trovato con i criteri selezionati.")

# Statistiche sui pediatri
if pediatri:
    pediatri_df = pd.DataFrame(pediatri)
    zona_counts = pediatri_df['Zone'].value_counts().reset_index()
    zona_counts.columns = ['Zona', 'Numero Pediatri']

    st.sidebar.subheader("📊 Statistiche")
    fig = px.bar(zona_counts, x='Zona', y='Numero Pediatri', 
                 title="Numero di Pediatri per Zona", 
                 color='Zona', height=400)
    st.sidebar.plotly_chart(fig)

# Leggenda interattiva
legend_html = """
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 150px; height: 90px; 
    background-color: white; z-index: 1000; font-size: 14px;
    border:2px solid grey; padding: 10px; border-radius: 8px;">
    <b>Legenda:</b><br>
    <i style="background: #00B4D8; width: 10px; height: 10px; display: inline-block; margin-right: 5px;"></i> Zone<br>
    <i style="background: black; width: 10px; height: 10px; display: inline-block; margin-right: 5px;"></i> Confini
</div>
"""
mymap.get_root().html.add_child(folium.Element(legend_html))

# Suggerimenti
st.sidebar.info(""" 
💡 **Suggerimenti di utilizzo:**  
- Usa il campo di ricerca per filtrare i pediatri per nome, cognome o indirizzo.  
- Seleziona una zona per visualizzare i pediatri di quell'area.  
- Clicca sui marker della mappa per ulteriori dettagli.
""")
