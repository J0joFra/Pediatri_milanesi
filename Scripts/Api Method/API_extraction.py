import urllib.request
import json
import pandas as pd

# URL del dataset
url = 'https://dati.comune.milano.it/api/3/action/datastore_search?resource_id=22b05e1f-c5d2-4468-90e5-c098977856ef&limit=5'

# Apertura URL e lettura dei dati JSON
fileobj = urllib.request.urlopen(url)
data = json.load(fileobj)

records = data["result"]["records"]

# DataFrame
df = pd.DataFrame(records)
print(f"{df}\n{df.columns}")

# Capitalizza i titoli delle colonne
df.columns = [col.capitalize() for col in df.columns]
df = df.applymap(lambda x: x.capitalize() if isinstance(x, str) else x)

# Rinomina le colonne
df = df.rename(columns={
    "Idmedico": "ID_med",
    "Nomemedico": "Name_med",
    "Cognomemedico": "Surname_med",
    "Nil": "Zone",
    "Long_x_4326": "Long",
    "Lat_y_4326": "Lat",
    "Codice_regionale_medico": "Code_med",
    'DataNascita': "Age",
    "ID_Nil": "ID_zone",
})

df = df.rename(columns={
    "Tipomedico": "Type_med",
    "Attivo": "Open",
    "Ambulatorioprincipale": "Main_amb",
    "Luogo_ambulatorio": "L_ambul",
})

print(f"{df}\n{df.columns}")

# Colonna combinata 'Via', 'Civico' e 'Luogo_ambulatorio'
def create_address(row):
    parts = []
    if pd.notna(row['Via']) and row['Via']:
        parts.append(row['Via'])
    if pd.notna(row['Civico']) and row['Civico']:
        parts.append(row['Civico'])
    if pd.notna(row['L_ambul']) and row['L_ambul']:
        parts.append(row['L_ambul'])
    return ', '.join(parts)

df['Address'] = df.apply(create_address, axis=1)
df['Address'] = df['Address'].str.title()

df = df.drop(['_id','Via', 'Civico', 'L_ambul'], axis=1)

print(df['Address'])
print(df.columns)
