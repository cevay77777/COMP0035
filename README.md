# COMP0035 Coursework 1 – Air Passenger Departures

This project analyses air passenger departures over time and creates an SQLite
database from three related CSV files:

- `TotalAirPassengerDepartures.csv`
- `TotalAirPassengerDeparturesbyRegion.csv`
- `TotalAirPassengerDeparturesbyCountry.csv`

## Project structure

- `data/raw/` – original CSV files
- `data/processed/` – prepared datasets and charts
- `src/` – Python code modules
- `air_passenger_departures.db` – SQLite database file created by the code

## Environment setup

It is recommended to use a Python virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Code

After activating the virtual environment and installing dependencies, the coursework scripts can be executed as follows.

### 1. Run the Data Preparation Script

This script loads the raw CSV files, cleans the data, generates processed CSVs, and produces all analytical figures required for Section 1.

```bash
python -m src.data_preparation
```


### 2. Run the Data Description Script

This script prints a high-level summary of the raw datasets, including column names, row counts, and sample rows.  

```bash
python -m src.data_description
```
### 3. Run the Create Database Script

This script creates the SQLite database using the schema defined in db_schema.py and populates it with all global, regional, and country-level records.

```bash
python -m src.create_database
```

Which will create a resulting SQL file as air_passenger_departures.db

## 4. Github Repository

The source code is contained in the repository https://github.com/cevay77777/COMP0035