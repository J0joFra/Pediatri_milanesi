import urllib.request
import json
import pandas as pd
import numpy as np
import pymongo

# Funzione per calcolare l'età
def calcola_eta(data_nascita):
    if pd.notnull(data_nascita):
        oggi = pd.Timestamp.now()
        eta = oggi.year - data_nascita.year - ((oggi.month, oggi.day) < (data_nascita.month, data_nascita.day))
        return eta
    return np.nan

# Funzione principale
def main():
    # URL dell'API
    url = 'https://dati.comune.milano.it/api/3/action/datastore_search?resource_id=22b05e1f-c5d2-4468-90e5-c098977856ef&limit=5000'

    # Carica i dati dall'API
    response = urllib.request.urlopen(url)
    data = json.load(response)
    records = data["result"]["records"]

    # Converti i dati in un DataFrame
    df = pd.DataFrame(records)

    # Preprocessing
    df = df.fillna({
        'civico': 'N/A',
        'luogo_ambulatorio': 'Milano'
    })

    # Converti la colonna 'dataNascita' in formato datetime
    df['dataNascita'] = pd.to_datetime(df['dataNascita'], errors='coerce')

    # Applica la funzione per calcolare l'età
    df['età'] = df['dataNascita'].apply(calcola_eta)

    # Standardizza i valori nella colonna 'tipoMedico'
    df['tipoMedico'] = df['tipoMedico'].replace({
        'PLS': 'Pediatra di Libera Scelta',
        'Incaricato provvisorio Pediatra': 'Pediatra Incaricato Provvisorio'
    })

    # Converti 'attivo' e 'ambulatorioPrincipale' in booleani
    df['attivo'] = df['attivo'].astype(bool, errors='ignore')
    df['ambulatorioPrincipale'] = df['ambulatorioPrincipale'].astype(bool, errors='ignore')

    # Crea una colonna 'nome_completo' combinando nome e cognome
    df['nome_completo'] = (df['nomeMedico'].astype(str) + ' ' + df['cognomeMedico'].astype(str)).str.title()

    # Rimuovi spazi extra dalle colonne di testo e trasforma in Title Case
    text_columns = ['nomeMedico', 'cognomeMedico', 'comune_medico', 'aft', 'via', 'luogo_ambulatorio', 'NIL']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()

    # Converti le coordinate in float
    df['LONG_X_4326'] = pd.to_numeric(df['LONG_X_4326'], errors='coerce')
    df['LAT_Y_4326'] = pd.to_numeric(df['LAT_Y_4326'], errors='coerce')

    # Rimuovi le colonne 'NomeMedico' e 'CognomeMedico'
    df = df.drop(columns=['nomeMedico', 'cognomeMedico'], errors='ignore')

    # Trasforma i nomi delle colonne in "Title Case"
    df.columns = df.columns.str.replace('_', ' ').str.title().str.replace(' ', '')

    # Riordina le colonne
    columns_order = ['IdMedico', 'NomeCompleto', 'CodiceRegionaleMedico', 
                     'DataNascita', 'Età', 'TipoMedico', 'Attivo', 'AmbulatorioPrincipale', 'ComuneMedico', 
                     'Aft', 'Via', 'Civico', 'LuogoAmbulatorio', 'Cap', 'Municipio', 'IdNil', 'Nil', 
                     'LongX4326', 'LatY4326', 'Location']

    # Assicurati che tutte le colonne da ordinare siano presenti
    existing_columns_order = [col for col in columns_order if col in df.columns]
    df = df[existing_columns_order]

    # Connessione a MongoDB
    client = pymongo.MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
    db = client["Healthcare"]
    collection = db["Pediatri"]

    # Svuota la collezione se esiste
    collection.delete_many({})

    # Inserisci i dati in MongoDB
    data_dict = df.to_dict("records")
    collection.insert_many(data_dict)
    print(f"Inseriti {len(data_dict)} documenti nella collezione 'Pediatri'.")

# Esegui il main
if __name__ == "__main__":
    main()
