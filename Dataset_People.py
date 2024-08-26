import random
import csv

# Definiamo alcune liste di malattie e sintomi pediatrici comuni
malattie = ["Influenza", "Varicella", "Otite", "Asma", "Allergia", "Bronchite", "Raffreddore", "Febbre", "Diarrea", "Mal di gola"]
generi = ["Maschio", "Femmina"]
severita = ["Leggera", "Moderata", "Grave"]

# Lista dei codici dei medici dal file caricato
codici_medici = medici_df['CodiceRegionaleMedico'].tolist()

# Creazione di un dataset con 300 righe
pazienti = []
for _ in range(300):
    id_paziente = random.randint(1000, 9999)
    eta_paziente = random.randint(0, 15)
    malattia = random.choice(malattie)
    genere = random.choice(generi)
    codice_medico = random.choice(codici_medici)
    data_visita = f"{random.randint(2022, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    livello_severita = random.choice(severita)
    
    pazienti.append([id_paziente, eta_paziente, malattia, genere, codice_medico, data_visita, livello_severita])

# Nome del file CSV di output
output_file = "/mnt/data/pazienti_pediatrici.csv"

# Scriviamo il file CSV
header = ["ID_Paziente", "Età_Paziente", "Sintomo/Malattia", "Genere", "Codice_Medico", "Data_Visita", "Severità"]

with open(output_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(pazienti)

output_file
