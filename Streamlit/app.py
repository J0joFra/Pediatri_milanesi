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

# Crea la tabella in HTML
table_html = '''
<div class="container">
    <div class="table-container">
        <table id="myTable">
            <thead>
                <tr class="header">
                    <th>Codice</th>
                    <th>Nome</th>
                    <th>Cognome</th>
                    <th>Indirizzo</th>
                </tr>
            </thead>
            <tbody>
'''

# Aggiungi ogni pediatra alla tabella
for pediatra in pediatri:
    table_html += f'''
                <tr>
                    <td>{pediatra['Code_med']}</td>
                    <td>{pediatra['Name_med']}</td>
                    <td>{pediatra['Surname_med']}</td>
                    <td>{pediatra['Address']}</td>
                </tr>
    '''

# Concludi la tabella
table_html += '''
            </tbody>
        </table>
    </div>
    <div id="map" class="map-container"></div>
</div>
'''

# Visualizza la tabella
st.markdown(table_html, unsafe_allow_html=True)

# Aggiungi mappa
st.subheader("Mappa dei Pediatri")

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
