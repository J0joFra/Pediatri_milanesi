# Importazione Librerie
import json
import pandas as pd

# Percorso del file
file_path = "22b05e1f-c5d2-4468-90e5-c098977856ef.json"

# Carica i dati dal file JSON
with open(file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)
    
# Stampa i dati JSON in formato leggibile
print(json.dumps(json_data, indent=4))



