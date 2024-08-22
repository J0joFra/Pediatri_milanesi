import pandas as pd
import pymysql
from sqlalchemy import create_engine

# Dettagli della connessione al database
db_host = 'localhost'      # Indirizzo del server MySQL
db_user = 'tuo_utente'     # Nome utente del database
db_password = 'tua_password' # Password del database
db_name = 'nome_del_database' # Nome del database

# Percorso del file CSV
file_csv_path = 'medici_pulito.csv'

# Carica i dati dal file CSV
df = pd.read_csv(file_csv_path)

# Crea la connessione al database MySQL
engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}')

# Carica i dati nel database
df.to_sql('Medici', con=engine, if_exists='replace', index=False)

print("Dati caricati con successo nella tabella 'Medici'.")
