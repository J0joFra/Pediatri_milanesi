# HEALTHCARE: Freelance Pediatricians
## Project Description

This project aims to collect, clean, and upload data regarding freelance pediatricians active in the municipality of Milan during the month of August, which were downloaded from the [official website of the Municipality of Milan](https://dati.comune.milano.it/dataset/ds235-sociale-pediatri-libera-scelta) and analyzed through a Python pipeline.

The project is divided into three main phases:

1. **Database Setup**: Configuration of an SQL database to store the data.
2. **Data Collection and Cleaning**: Downloading the data in CSV format and applying cleaning operations.
3. **Data Upload**: Inserting the cleaned data into the SQL database.

## Project Structure

- `Database_setting.py`: Script to set up the SQL database and load the cleaned data into the `Medici` table.
- `Extraction_and_cleaning.py`: Script to download the data from the Municipality of Milan’s website, clean and prepare it for upload.
- `requirements.txt`: A file containing the necessary Python libraries to run the scripts.
- `.env`: A file to store environment variables (not included in the repository for security reasons).

## Requirements

- **Software**:
  - Python 3.x
  - An SQL server (e.g., MySQL or PostgreSQL)

- **Python Libraries**:
  - `pandas`
  - `numpy`
  - `pymysql`
  - `sqlalchemy`
  - `python-dotenv`

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/your-username/pediatri-milano-agosto.git
   ```

2. **Navigate to the project folder**:
   ```bash
   cd pediatri-milano-agosto
   ```

3. **Create and activate a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. **Install the requirements**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

To securely handle database credentials, it is recommended to use environment variables instead of hardcoding them in the scripts.

1. **Create a `.env` file in the project directory** and add the following variables:
   ```env
   DB_HOST=127.0.0.1
   DB_USER=root
   DB_PASSWORD=YourSecurePassword
   DB_NAME=pediatri
   ```

2. **Make sure to add `.env` to your `.gitignore`** to avoid accidentally committing your credentials:
   ```gitignore
   # Environment file
   .env
   ```

#### `Extraction_and_cleaning.py`

If you haven't already, you might want to update this script to automatically download data from the Municipality of Milan's website. However, based on the provided code, it appears that you are already loading a local CSV file. Make sure the file path is correct and that the data is accessible.

## Usage Instructions

1. **Run the script to extract and clean the data**:
   ```bash
   python Extraction_and_cleaning.py
   ```

   This script performs the following operations:
   - Loads the data from the downloaded CSV file.
   - Handles missing values by filling in certain fields.
   - Converts the `dataNascita` column to datetime format and calculates age.
   - Standardizes values in the `tipoMedico` column.
   - Converts the `attivo` and `ambulatorioPrincipale` columns to booleans.
   - Creates a `nome_completo` column by combining first and last names.
   - Cleans and formats text columns.
   - Converts coordinates to float.
   - Removes unnecessary columns.
   - Reorders the columns and exports the cleaned DataFrame to `medici_pulito.csv`.

2. **Set up the database and load the cleaned data**:
   ```bash
   python Database_setting.py
   ```

   This script performs the following operations:
   - Loads environment variables for database connection.
   - Loads the cleaned data from the `medici_pulito.csv` file.
   - Establishes a connection to the MySQL database.
   - Loads the data into the SQL database in the `Medici` table.

## Security

**Important Note**: Never share your database credentials in public repositories. Always use environment variables or configuration files that are excluded from version control to manage sensitive information.

## Example of `requirements.txt`

Ensure your `requirements.txt` includes all the necessary libraries:

```
pandas
numpy
pymysql
sqlalchemy
python-dotenv
```

You can automatically generate this file by running:

```bash
pip freeze > requirements.txt
```

## Author

Joaquim Francalanci - [LinkedIn](https://www.linkedin.com/)
