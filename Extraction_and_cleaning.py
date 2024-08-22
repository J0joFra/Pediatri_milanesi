# Librerie da importare
import urllib.request
import json
import pandas

# Url dell'Api
url = 'https://dati.comune.milano.it/api/3/action/datastore_search?resource_id=22b05e1f-c5d2-4468-90e5-c098977856ef&limit=5&q=title:jones'

# Richiesta GET dell'API
with urllib.request.urlopen(url) as response:
    # Leggi la risposta e decodificala
    data = response.read().decode()

    # Converti il contenuto in JSON
    json_data = json.loads(data)

    # Stampa i dati JSON
    print(json_data)


