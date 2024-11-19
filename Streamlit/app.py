import streamlit as st
from pymongo import MongoClient

# Connessione a MongoDB
client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
db = client['Healthcare']
collection = db['Pediatri']

# Carica il CSS
st.markdown(
    f'<link href="static/style.css" rel="stylesheet">',
    unsafe_allow_html=True
)

# Carica il file JavaScript (se necessario)
st.markdown(
    f'<script src="static/script.js"></script>',
    unsafe_allow_html=True
)

# Funzione principale per visualizzare i dati dei pediatri
def load_pediatri():
    query = st.text_input("Cerca Pediatra", "")
    
    if query:
        # Cerca nei campi nome, zona, e specializzazione
        pediatri = collection.find({
            "$or": [{"Name_med": {"$regex": query, "$options": "i"}},
                    {"Surname_med": {"$regex": query, "$options": "i"}},
                    {"Address": {"$regex": query, "$options": "i"}}]
        })
    else:
        pediatri = collection.find()

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

# Includi una mappa tramite Folium o altro metodo di visualizzazione
# Esempio per mappa con Folium (se hai bisogno di una mappa interattiva)
import folium
from streamlit_folium import st_folium

# Inizializza la mappa
map_center = [45.4642, 9.16]  # Milano
mymap = folium.Map(location=map_center, zoom_start=12)

# Aggiungi un marker per ogni pediatra (se hai delle coordinate)
for pediatra in pediatri:
    folium.Marker([pediatra['Latitude'], pediatra['Longitude']], popup=pediatra['Name_med']).add_to(mymap)

# Visualizza la mappa in Streamlit
st_folium(mymap, width=700, height=500)
