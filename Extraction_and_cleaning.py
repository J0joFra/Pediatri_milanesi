# Libreria da estrarre
import requests

# URL dell'API del Comune di Milano
url = 'https://dati.comune.milano.it/api/3/action/datastore_search?resource_id=22b05e1f-c5d2-4468-90e5-c098977856ef&limit=5&q=title:jones'

# Effettuiamo la richiesta HTTP GET all'API
response = requests.get(url)

# Verifichiamo che la richiesta sia stata completata con successo 
if response.status_code == 200:
    data = response.json()
    print("Dati estratti correttamente")
else:
    print(f"Errore durante l'estrazione:\n{response.status_code}")
