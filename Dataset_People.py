import random
import csv
import pandas as pd

# Supponiamo che tu abbia un file CSV contenente i codici dei medici
df = pd.read_csv("medici_pulito.csv")

# Definiamo alcune liste di malattie e sintomi pediatrici comuni
malattie = ["Influenza", "Varicella", "Otite", "Asma", "Allergia", "Bronchite", "Raffreddore", "Febbre", "Diarrea", "Mal di gola"]
generi = ["Maschio", "Femmina"]
severita = ["Leggera", "Moderata", "Grave"]

# Lista dei codici medici dal CSV
codici_medici = df['CodiceRegionaleMedico'].tolist()

# Filtriamo i codici dei medici in base ai valori forniti dall'utente
codici_medici_filtrati = [codice for codice in codici_medici if codice in codici_medici]

# Creiamo nuovamente il dataset di pazienti con solo i codici dei medici filtrati
pazienti_filtrati = []
for _ in range(300):
    id_paziente = random.randint(1000, 9999)
    eta_paziente = random.randint(0, 15)
    malattia = random.choice(malattie)
    genere = random.choice(generi)
    codice_medico = random.choice(codici_medici_filtrati)
    data_visita = f"{random.randint(2022, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    livello_severita = random.choice(severita)
    
    pazienti_filtrati.append([id_paziente, eta_paziente, malattia, genere, codice_medico, data_visita, livello_severita])

# Scriviamo il nuovo file CSV con i dati filtrati
output_file_filtrato = "pazienti_pediatrici.csv"

with open(output_file_filtrato, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["ID_Paziente", "Età_Paziente", "Sintomo/Malattia", "Genere", "Codice_Medico", "Data_Visita", "Severità"])
    writer.writerows(pazienti_filtrati)

print(f"File creato: {output_file_filtrato}")
