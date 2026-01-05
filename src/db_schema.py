"""
SQL schema definitions for the SQLite database aligned with the COMP0035 relational model.
"""

CREATE_REGION_TABLE = """
CREATE TABLE IF NOT EXISTS Region (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT UNIQUE NOT NULL
);
"""

CREATE_COUNTRY_TABLE = """
CREATE TABLE IF NOT EXISTS Country (
    country_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_name TEXT NOT NULL,
    region_id INTEGER NOT NULL,
    FOREIGN KEY (region_id) REFERENCES Region(region_id)
);
"""

CREATE_GLOBAL_DEPARTURES_TABLE = """
CREATE TABLE IF NOT EXISTS GlobalDepartures (
    month TEXT PRIMARY KEY,
    value REAL
);
"""

CREATE_REGIONAL_DEPARTURES_TABLE = """
CREATE TABLE IF NOT EXISTS RegionalDepartures (
    month TEXT NOT NULL,
    region_id INTEGER NOT NULL,
    value REAL,
    PRIMARY KEY (month, region_id),
    FOREIGN KEY (region_id) REFERENCES Region(region_id)
);
"""

CREATE_COUNTRY_DEPARTURES_TABLE = """
CREATE TABLE IF NOT EXISTS CountryDepartures (
    month TEXT NOT NULL,
    country_id INTEGER NOT NULL,
    value REAL,
    PRIMARY KEY (month, country_id),
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);
"""
