import streamlit as st
from pymongo import MongoClient
import folium
from streamlit_folium import st_folium
import os

# region Mongo DB
# Connessione a MongoDB
client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
db = client['Healthcare']
collection = db['Pediatri']

# Carica il CSS
css_path = os.path.join(os.getcwd(), 'static', 'style.css')
with open(css_path, 'r') as css_file:
    css_content = css_file.read()
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Carica il file JavaScript (se necessario)
js_path = os.path.join(os.getcwd(), 'static', 'script.js')
with open(js_path, 'r') as js_file:
    js_content = js_file.read()
st.markdown(f"<script>{js_content}</script>", unsafe_allow_html=True)

# Funzione principale per visualizzare i dati dei pediatri
def load_pediatri():
    query = st.text_input("Cerca Pediatra", "")
    
    if query:
        # Cerca nei campi nome, zona, e specializzazione
        pediatri = collection.find({
            "$or": [{"Name_med": {"$regex": query, "$options": "i"}},
                    {"Surname_med": {"$regex": query, "$options": "i"}},
                    {"Address": {"$regex": query, "$options": "i"}}]
        }).limit(10)  # Limita a 10 risultati
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

# Aggiungi mappa
st.subheader("Mappa dei Pediatri")

# region Mappa
# Inizializza la mappa
map_center = [45.4642, 9.16]  # Milano
mymap = folium.Map(location=map_center, zoom_start=12)

# Aggiungi un marker per ogni pediatra (se hai delle coordinate)
for pediatra in pediatri:
    folium.Marker([pediatra['Latitude'], pediatra['Longitude']], popup=pediatra['Name_med']).add_to(mymap)

# Visualizza la mappa in Streamlit
st_folium(mymap, width=700, height=500)
