#Importazioni Librerie
import pandas as pd
import numpy as np

#Importazione Dataset
file_path = r"cedefop-datatable.csv"
df = pd.read_csv(file_path, encoding='ISO-8859-1', delimiter=',')

#Prime righe del dataset
print(df.head())
