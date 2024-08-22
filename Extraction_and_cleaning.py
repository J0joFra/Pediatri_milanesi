# Librerie
import pandas as pd
import numpy as np

# Percorso del file CSV scaricato
file_csv_path = '22b05e1f-c5d2-4468-90e5-c098977856ef.csv'

# Carica i dati dal file CSV
df = pd.read_csv(file_csv_path)

# Gestisci i valori mancanti
df = df.fillna({
    'civico': 'N/A',
    'luogo_ambulatorio': 'Milano'
})

# Converti la colonna 'dataNascita' in formato datetime
df['dataNascita'] = pd.to_datetime(df['dataNascita'], errors='coerce')

# Funzione per calcolare l'età
def calcola_eta(data_nascita):
    if pd.notnull(data_nascita):
        oggi = pd.Timestamp.now()
        eta = oggi.year - data_nascita.year - ((oggi.month, oggi.day) < (data_nascita.month, data_nascita.day))
        return eta
    return np.nan

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
        df[col] = df[col].str.strip().str.title()  # Trasforma in Title Case

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

# Stampa le prime righe del DataFrame pulito
print("\nPrime righe del DataFrame pulito:")
print(df.head())
