# HEALTHCARE: Frelance Pediatricians
## Project Description

This project aims to collect, clean and upload data regarding pediatricians active in the municipality of Milan in the month of August. The data were downloaded from the official website of the Municipality of Milan and analyzed through a Python pipeline.

Il progetto è suddiviso in tre fasi principali:

1. **Impostazione del database**: Configurazione di un database SQL per archiviare i dati.
2. **Raccolta e pulizia dei dati**: Scaricamento dei dati in formato CSV e applicazione delle operazioni di pulizia.
3. **Caricamento dei dati**: Inserimento dei dati puliti nel database SQL.

## Struttura del progetto

- `Database_setting.py`: Script per l'impostazione del database SQL e il caricamento dei dati puliti nella tabella `Medici`.
- `Extraction_and_cleaning.py`: Script per il download dei dati dal sito del Comune di Milano, la pulizia e la preparazione dei dati per il caricamento.
- `requirements.txt`: File contenente le librerie Python necessarie per eseguire gli script.
- `.env`: File per memorizzare le variabili di ambiente (non incluso nel repository per motivi di sicurezza).

## Dati

I dati utilizzati nel progetto sono stati scaricati dal [sito ufficiale del Comune di Milano](https://www.comune.milano.it/) e contengono informazioni relative ai pediatri attivi nella città durante il mese di agosto.

## Requisiti

- **Software**:
  - Python 3.x
  - Un server SQL (ad esempio, MySQL o PostgreSQL)

- **Librerie Python**:
  - `pandas`
  - `numpy`
  - `pymysql`
  - `sqlalchemy`
  - `python-dotenv`

## Installazione

1. **Clona questo repository**:
   ```bash
   git clone https://github.com/tuo-username/pediatri-milano-agosto.git
   ```

2. **Naviga nella cartella del progetto**:
   ```bash
   cd pediatri-milano-agosto
   ```

3. **Crea e attiva un ambiente virtuale (opzionale ma consigliato)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows usa `venv\Scripts\activate`
   ```

4. **Installa i requisiti**:
   ```bash
   pip install -r requirements.txt
   ```

## Configurazione

### Variabili di ambiente

Per motivi di sicurezza, è consigliato utilizzare variabili di ambiente per memorizzare le credenziali del database invece di includerle direttamente nel codice.

1. **Crea un file `.env` nella directory del progetto** e aggiungi le seguenti variabili:
   ```env
   DB_HOST=127.0.0.1
   DB_USER=root
   DB_PASSWORD=GigiTrottolino24
   DB_NAME=pediatri
   ```

2. **Assicurati di aggiungere `.env` al tuo `.gitignore** per evitare di commettere accidentalmente le credenziali:
   ```gitignore
   # File di ambiente
   .env
   ```

### Aggiornamento degli script

#### `Database_setting.py`

Modifica lo script per caricare le variabili di ambiente utilizzando `python-dotenv`:

```python
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Dettagli della connessione al database
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

# Percorso del file CSV
file_csv_path = 'medici_pulito.csv'

# Carica i dati dal file CSV
df = pd.read_csv(file_csv_path)

# Crea la connessione al database MySQL
engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}')

# Carica i dati nel database
df.to_sql('Medici', con=engine, if_exists='replace', index=False)

print("Dati caricati con successo nella tabella 'Medici'.")
```

#### `Extraction_and_cleaning.py`

Se non lo hai già fatto, potresti voler aggiornare questo script per scaricare automaticamente i dati dal sito del Comune di Milano. Tuttavia, dal codice fornito, sembra che tu stia già caricando un file CSV locale. Assicurati che il percorso del file CSV sia corretto e che i dati siano accessibili.

## Istruzioni per l'uso

1. **Esegui lo script per estrarre e pulire i dati**:
   ```bash
   python Extraction_and_cleaning.py
   ```
   
   Questo script esegue le seguenti operazioni:
   - Carica i dati dal file CSV scaricato.
   - Gestisce i valori mancanti sostituendo alcuni campi.
   - Converte la colonna `dataNascita` in formato datetime e calcola l'età.
   - Standardizza i valori nella colonna `tipoMedico`.
   - Converte le colonne `attivo` e `ambulatorioPrincipale` in booleani.
   - Crea una colonna `nome_completo` combinando nome e cognome.
   - Pulisce e formatta le colonne di testo.
   - Converte le coordinate in float.
   - Rimuove alcune colonne non necessarie.
   - Riordina le colonne e esporta il DataFrame pulito in `medici_pulito.csv`.

2. **Configura il database e carica i dati puliti**:
   ```bash
   python Database_setting.py
   ```
   
   Questo script esegue le seguenti operazioni:
   - Carica le variabili di ambiente per la connessione al database.
   - Carica i dati puliti dal file CSV `medici_pulito.csv`.
   - Crea una connessione al database MySQL.
   - Carica i dati nel database nella tabella `Medici`.

## Sicurezza

**Nota Importante:** Non condividere mai le tue credenziali di database in repository pubblici. Utilizza sempre variabili di ambiente o file di configurazione che non vengono inclusi nel controllo di versione per gestire informazioni sensibili.

## Esempio di `requirements.txt`

Assicurati che il tuo `requirements.txt` includa tutte le librerie necessarie:

```
pandas
numpy
pymysql
sqlalchemy
python-dotenv
```

Puoi generare automaticamente questo file eseguendo:

```bash
pip freeze > requirements.txt
```

## Autore

Joaquim Francalanci - [LinkedIn](https://www.linkedin.com/)

