import pandas as pd

# Percorso del file CSV scaricato
file_csv_path = '22b05e1f-c5d2-4468-90e5-c098977856ef.csv'

# Carica i dati dal file CSV
df = pd.read_csv(file_csv_path)

# Stampa le prime righe del DataFrame per verificare i dati
print(df.head())

# Stampa le colonne per verificare che siano corrette
print(df.columns)
