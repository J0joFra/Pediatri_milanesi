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
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data["result"]["records"])
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

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

# Recupera i dati meteo
temperature, humidity, weather_description = get_weather_data()

# Funzione per creare box colorati per le metriche
def metrics_html(label, value, color):
    return f"""
    <div style="
        background-color: {color};
        padding: 10px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
        text-align: center;
        color: white;
        margin-bottom: 2px;
    ">
        <h4 style="margin: 0; font-size: 14px;">{label}</h4>
        <p style="margin: 0; font-size: 18px; font-weight: bold;">{value}</p>
    </div>
    """

# Intestazione della pagina
st.title("👶 Healthcare: Pediatri a Milano")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    Questo strumento è stato progettato per fornire informazioni dettagliate sui pediatri freelance disponibili nelle diverse zone della città, aiutandoti a identificare rapidamente i professionisti più vicini alle tue esigenze.
    Grazie a un'interfaccia intuitiva e funzionalità avanzate, puoi:  
    - 🔍 **Cercare pediatri** in base al nome, cognome, indirizzo o zona di appartenenza.  
    - 🗺️ **Visualizzare i pediatri su una mappa interattiva**, con dettagli sui luoghi e zone di servizio.  
    - 📋 **Consultare un elenco aggiornato** con informazioni chiave come indirizzo, zona e disponibilità.  
    - 📊 **Esplorare statistiche** sulla distribuzione dei pediatri nelle diverse aree urbane, incluse le zone meno coperte.  
    - 📥 **Scaricare i dati in formato CSV**, per un utilizzo più approfondito e personalizzato.  
    Grazie a questo strumento, trovare il pediatra giusto non è mai stato così semplice e veloce. Inizia la tua ricerca e scopri il professionista che si prenderà cura del benessere dei tuoi piccoli!  
    """)

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

# Spazio tra le metriche e la mappa
st.markdown("<br>", unsafe_allow_html=True)

# Bottone per aggiornare i dati
if st.button("🔄 Ricarica Dati"):
    # Funzione per ricaricare e aggiornare il dataset
    st.write("🚀 Ricaricamento in corso...")
    
    # Ottieni nuovamente i dati meteo
    temperature, humidity, weather_description = get_weather_data()
    
    # Carica i nuovi dati
    url = "https://url-del-dataset.json"  # Aggiorna con l'URL del dataset
    df = load_data(url)
    
    # Applica tutte le trasformazioni al dataframe
    df = title_columns_and_values(df)
    df = rename_columns(df)
    df = calculate_age(df)
    df = create_address_column(df)
    df = drop_unnecessary_columns(df)
    gdf = create_geometry_column(df)
    
    # Aggiorna le zone con il file GeoJSON
    geojson_path = "Datasets/MilanCity.geojson"  # Aggiorna con il path corretto
    if os.path.exists(geojson_path):
        gdf_zones = load_geojson(geojson_path)
        gdf = spatial_join_update_zones(gdf, gdf_zones)

    # Carica i dati in MongoDB
    create_mongo_db(gdf)
    
    # Ricarica i pediatri dal MongoDB
    pediatri = load_pediatri(query, selected_zone)
    
    # Mostra messaggio di successo
    st.success("✅ Dati ricaricati con successo!")

# Aggiorna la visualizzazione della mappa, tabella e statistiche
st.subheader("🗺️ Mappa dei Pediatri")
map_center = [45.4642, 9.16]  # Milano
mymap = folium.Map(location=map_center, zoom_start=12)

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

# Visualizza la mappa
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
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

st.download_button(
    label="📥 Scarica come CSV",
    data=pediatri_df.to_csv(index=False).encode('utf-8'),
    file_name='pediatri_milano.csv',
    mime='text/csv'
)

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

    # Funzione per creare box colorati con HTML
    def colored_box(label, value, color):
        box_html = f"""
        <div style="
            background-color: {color};
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            text-align: center;
            color: black;">
            <h4 style="margin: 0; font-size: 18px;">{label}</h4>
            <p style="margin: 0; font-size: 24px; font-weight: bold;">{value}</p>
        </div>
        """
        return box_html

    # Layout delle metriche con box colorati
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(colored_box("🏥 Totale Pediatri", len(pediatri_df), "#E1E5F2"), unsafe_allow_html=True)

    with col2:
        st.markdown(colored_box("📍 Zone Coperte", len(pediatri_per_zone), "#D6EADF"), unsafe_allow_html=True)

    with col3:
        st.markdown(colored_box("🚫 Zone Senza Pediatri", zones_no_pediatri, "#BEE9E8"), unsafe_allow_html=True)

    with col2:
        fig_pie = px.pie(
            names=stats.keys(),
            values=stats.values(),
            title="<b>Distribuzione Zone</b>",
            color_discrete_sequence=px.colors.sequential.Teal
        )

        # Configurazione per centrare titolo, grafico e legenda
        fig_pie.update_traces(
            textinfo='percent',
            textfont_size=20,
            marker=dict(
                line=dict(color='#012A4A', width=1.5)
            )
        )
        fig_pie.update_layout(
            title=dict(
                text="<b>Distribuzione Zone</b>",
                font=dict(size=20),
                x=0.5,  # Centra il titolo orizzontalmente
                xanchor='center'
            ),
            legend=dict(
                font=dict(size=14), 
                orientation="h",  # Legenda orizzontale
                x=0.5,  # Centra la legenda
                xanchor='center',
                y=-0.2  # Posiziona la legenda più in basso per allineamento estetico
            ),
            margin=dict(t=50, b=50, l=50, r=50),  # Margini del grafico per un centraggio migliore
            plot_bgcolor='rgba(0,0,0,0)',  # Rende lo sfondo trasparente
            paper_bgcolor='rgba(0,0,0,0)'  # Rende il contorno trasparente
        )
        fig_pie.update_layout(
            annotations=[
                dict(
                    text='',  # Testo aggiuntivo opzionale
                    showarrow=False,
                    x=0.5,  # Centro orizzontale
                    y=0.5,  # Centro verticale
                    font=dict(size=14)
                )
            ]
        )   
        st.plotly_chart(fig_pie, use_container_width=True)
