import urllib.request
import json

url = 'https://dati.comune.milano.it/api/3/action/datastore_search?resource_id=22b05e1f-c5d2-4468-90e5-c098977856ef&limit=5'
fileobj = urllib.request.urlopen(url)
data = json.load(fileobj)

# Stampa i record
print(data["result"]["records"])
