import streamlit as st
from pymongo import MongoClient
import folium
from streamlit_folium import st_folium
import os

# Configura il layout di Streamlit
st.set_page_config(page_title="Healthcare - Pediatri Milano", 
                   page_icon="👶", 
                   layout="wide",
                   initial_sidebar_state="expanded")

# region Mongo DB
# Connessione a MongoDB
client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
db = client['Healthcare']
collection = db['Pediatri']

# Carica il CSS personalizzato
css_content = """
<style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f9f9f9;
        color: #333;
    }
    .main {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3 {
        color: #2b8a3e;
    }
    .stButton > button {
        background-color: #2b8a3e;
        color: white;
        border-radius: 5px;
        padding: 10px 15px;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #23732f;
    }
    .stTextInput input {
        border: 2px solid #2b8a3e;
        border-radius: 5px;
    }
    .dataframe {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }
</style>
"""
st.markdown(css_content, unsafe_allow_html=True)

# Funzione principale per visualizzare i dati dei pediatri
def load_pediatri(query="", selected_zone=None):
    filter_criteria = {}
    if query:
        # Cerca nei campi nome, cognome, e indirizzo
        filter_criteria["$or"] = [
            {"Name_med": {"$regex": query, "$options": "i"}},
            {"Surname_med": {"$regex": query, "$options": "i"}},
            {"Address": {"$regex": query, "$options": "i"}}
        ]
    if selected_zone and selected_zone != "Tutte le Zone":
        # Aggiungi filtro per la zona
        filter_criteria["Zone"] = selected_zone
    
    # Recupera i pediatri in base ai criteri
    pediatri = collection.find(filter_criteria).limit(10)
    return pediatri

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
query = st.sidebar.text_input("🔍 Cerca Pediatra", "Inserisci nome, cognome o indirizzo...")
zones = ["Tutte le Zone"] + get_zones()
selected_zone = st.sidebar.selectbox("📍 Seleziona una Zona", zones)

# Carica i pediatri e visualizzali
st.subheader("📋 Elenco Pediatri")
pediatri = load_pediatri(query, selected_zone)

# Crea la tabella in Streamlit
st.table([{
    'Codice': pediatra['Code_med'],
    'Nome': pediatra['Name_med'],
    'Cognome': pediatra['Surname_med'],
    'Indirizzo': pediatra['Address'],
    'Zona': pediatra['Zone']
} for pediatra in pediatri])

# Mappa interattiva
st.subheader("🗺️ Mappa dei Pediatri")

# Inizializza la mappa
map_center = [45.4642, 9.16]  # Milano
mymap = folium.Map(location=map_center, zoom_start=12)

# Aggiungi un marker per ogni pediatra (se hai delle coordinate)
for pediatra in pediatri:
    folium.Marker(
        [pediatra['Lat'], pediatra['Long']], 
        popup=f"<b>{pediatra['Name_med']} {pediatra['Surname_med']}</b><br>{pediatra['Address']}<br><i>{pediatra['Zone']}</i>"
    ).add_to(mymap)

# Visualizza la mappa in Streamlit
st_folium(mymap, width=900, height=500)

# Suggerimenti nella sidebar
st.sidebar.info("""
💡 **Suggerimenti di utilizzo:**  
- Usa il campo di ricerca per filtrare i pediatri per nome, cognome o indirizzo.  
- Seleziona una zona per visualizzare i pediatri di quell'area.  
- Clicca sui marker della mappa per ulteriori dettagli.
""")
