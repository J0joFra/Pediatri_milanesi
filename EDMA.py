#Importazioni Librerie
import pandas as pd
import numpy as np

#Importazione Dataset
file_path = r"cedefop-datatable.csv"
df = pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=',')

#Prime righe del dataset
print(df.head())

#Informazioni generali
print(df.info())

#Eliminiamo colonna "Flags"
df = df.drop(columns=['Flags'])

#Dimensione dataset Aggoirnato
print(df.shape)

#Valori unici Prima Colonna
valori_unici = df['Dataset'].unique()
print("Valori unici:", valori_unici)
print(df.head(20))