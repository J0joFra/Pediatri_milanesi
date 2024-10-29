import urllib.request
import json
import pandas as pd

# URL del dataset
url = 'https://dati.comune.milano.it/api/3/action/datastore_search?resource_id=22b05e1f-c5d2-4468-90e5-c098977856ef&limit=5'

# Apertura URL e lettura dei dati JSON
fileobj = urllib.request.urlopen(url)
data = json.load(fileobj)

records = data["result"]["records"]

# Dataframe
df = pd.DataFrame(records)
print(f"{df}\n{df.columns}")

# Capitalize
df.columns = [col.capitalize() for col in df.columns]
df = df.applymap(lambda x: x.capitalize() if isinstance(x, str) else x)

# Raname Columns
df = df.rename(columns={
    "Idmedico": "ID_med",
    "Nomemedico": "Name_med",
    "Cognomemedico": "Surname_med",
    "Nil": "Zone",
    "Long_x_4326": "Long",
    "Lat_y_4326": "Lat",
    "codice_regionale_medico": "Code_med",
    'dataNascita' : "Age",
    "Idmedico": "ID_med",
    "Nomemedico": "Name_med",
    "Cognomemedico": "Surname_med",
    "ID_Nil": "ID_zone",
    "Long_x_4326": "Long",
    "Lat_y_4326": "Lat",
    "Codice_regionale_medico": "Code_med",
    'dataNascita' : "Age",
})

print(f"{df}\n{df.columns}")

df = df.rename(columns={
    "Tipomedico": "Type_med",
    "Attivo": "Open",
    "Ambulatorioprincipale": "Main_amb",
})

print(f"{df}\n{df.columns}")


