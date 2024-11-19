import streamlit as st
from pymongo import MongoClient

# Connessione a MongoDB
client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
db = client['Healthcare']
collection = db['Pediatri']

# Impostazione della pagina Streamlit
st.title('Ricerca Pediatri Freelance')

# Barra di ricerca
query = st.text_input('Cerca pediatra per nome, zona o specializzazione')

# Risultati della ricerca
if query:
    pediatri = collection.find({
        "$or": [{"Name_med": {"$regex": query, "$options": "i"}},
                {"Surname_med": {"$regex": query, "$options": "i"}},
                {"Address": {"$regex": query, "$options": "i"}}]
    })
else:
    pediatri = collection.find()

# Visualizzazione dei risultati
if pediatri.count() > 0:
    for pediatra in pediatri:
        st.subheader(f"{pediatra['Name_med']} {pediatra['Surname_med']}")
        st.write(f"Zona: {pediatra['Address']}")
        st.write(f"Specializzazione: {pediatra.get('Specialization', 'Non specificata')}")
        st.write("---")
else:
    st.write("Nessun pediatra trovato per la tua ricerca.")
