import streamlit as st
import pymongo
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
import requests
import json
import os
import urllib.request
from datetime import datetime
from dateutil.relativedelta import relativedelta
import geopandas as gpd
from shapely.geometry import Point

# MongoDB Connection and Streamlit Setup
client = pymongo.MongoClient("mongodb+srv://your_connection_string")
db = client["Healthcare"]
collection = db["Pediatri"]

# Function for loading and processing the pediatrics data
def load_data(url):
    fileobj = urllib.request.urlopen(url)
    data = json.load(fileobj)
    return pd.DataFrame(data["result"]["records"])

def preprocess_data(df):
    df.columns = [col.capitalize() for col in df.columns]
    df = df.applymap(lambda x: x.title() if isinstance(x, str) else x)
    df = df.rename(columns={"Idmedico": "ID_med", "Nomemedico": "Name_med", "Cognomemedico": "Surname_med"})
    # Further preprocessing like creating address, calculating age, etc...
    return df

def create_mongo_db(dataframe):
    collection.delete_many({})
    data_dict = dataframe.to_dict("records")
    collection.insert_many(data_dict)
    print(f"Inserted {len(data_dict)} records into the database.")

# Load and preprocess the data
def main():
    url = 'https://dati.comune.milano.it/api/3/action/datastore_search?resource_id=22b05e1f-c5d2-4468-90e5-c098977856ef'
    df = load_data(url)
    df = preprocess_data(df)

    # Insert data into MongoDB
    create_mongo_db(df)
    st.title("👶 Healthcare: Pediatri a Milano")

    # Streamlit interface, including fetching and displaying the pediatricians' data from MongoDB
    pediatri = list(collection.find())
    st.subheader("🗺️ Mappa dei Pediatri")

    # Code for displaying the map with the pediatricians
    map_center = [45.4642, 9.16]
    mymap = folium.Map(location=map_center, zoom_start=12)

    for pediatra in pediatri:
        lat, long = pediatra.get('Lat'), pediatra.get('Long')
        if lat and long:
            folium.Marker([lat, long], popup=f"<b>{pediatra['Name_med']} {pediatra['Surname_med']}</b>").add_to(mymap)

    st_folium(mymap, width=1000, height=700)

# Run the app
main()
