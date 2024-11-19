import streamlit as st
import pandas as pd
import folium
from pymongo import MongoClient
from streamlit_folium import st_folium

# Connessione a MongoDB
client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
db = client['Healthcare']
collection = db['Pediatri']

# Recupera i dati
pediatri = collection.find()
df = pd.DataFrame(pediatri)

# Titolo della pagina
st.title("Medici Pediatrici Attivi a Milano")
st.write("Trova pediatri attivi nella tua zona e visualizza le loro informazioni.")

# Aggiungi la ricerca
query = st.text_input("Cerca per Nome, Cognome o Indirizzo")

if query:
    pediatri = collection.find({
        "$or": [{"Name_med": {"$regex": query, "$options": "i"}},
                {"Surname_med": {"$regex": query, "$options": "i"}},
                {"Address": {"$regex": query, "$options": "i"}}]
    })
    df = pd.DataFrame(pediatri)

# Visualizza la tabella dei pediatri
st.subheader("Lista dei Pediatri")
st.dataframe(df[['Code_med', 'Name_med', 'Surname_med', 'Address']])

# Includi il file CSS
with open("Streamlit/static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Crea la mappa
m = folium.Map(location=[45.4642, 9.16], zoom_start=12)

# Aggiungi marker per ogni pediatra
for _, pediatra in df.iterrows():
    folium.Marker([45.4642, 9.16], popup=f"{pediatra['Name_med']} {pediatra['Surname_med']}").add_to(m)

# Mostra la mappa
st.subheader("Mappa dei Pediatri")
st_folium(m, width=700, height=500)

# Includi il file JavaScript (se necessario)
with open("Streamlit/static/script.js") as f:
    st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)
