import sqlite3
from pathlib import Path
from datetime import datetime
from loaders import load_frequencies , load_assets , load_procedures , load_service_history , DATE_FMT

DB_PATH = Path(__file__).resolve().parent.parent/ 'data' / 'maintenance.sqlite'
DATA_DIR = DB_PATH.parent

def get_conn(path=DB_PATH):

    conn = sqlite3.connect(path)

    conn.execute('PRAGMA foreign_keys = ON')

    return conn

def create_freq(conn):

    conn.executescript('''

    CREATE TABLE Frequencies (
        service_frequency  TEXT PRIMARY KEY,
        service_interval_days    INTEGER NOT NULL
    );
    ''')

def create_assets(conn):

    conn.executescript('''

    CREATE TABLE Assets (
        asset_id    TEXT PRIMARY KEY,
        type    TEXT NOT NULL,
        description TEXT NOT NULL,
        location    TEXT NOT NULL,
        commissioning_date  TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('active', 'under repair', 'decommissioned')),
        linked_asset_id TEXT,
        FOREIGN KEY (linked_asset_id) REFERENCES Assets(asset_id)
    );
    ''')

def create_proc(conn):

    conn.executescript('''
    
    CREATE TABLE Procedures (
        procedure_id    TEXT PRIMARY KEY,
        asset_id    TEXT NOT NULL,
        description     TEXT NOT NULL,
        service_frequency   TEXT NOT NULL,
        FOREIGN KEY (asset_id) REFERENCES Assets(asset_id),
        FOREIGN KEY (service_frequency) REFERENCES Frequencies (service_frequency)
    );
    ''')

def create_history(conn):

    conn.executescript('''
    
    CREATE TABLE Service_History (
        record_id   TEXT PRIMARY KEY,
        procedure_id    TEXT NOT NULL,
        date_completed  TEXT NOT NULL,
        notes   TEXT,
        FOREIGN KEY (procedure_id) REFERENCES Procedures (procedure_id)
    );
    ''')

def build_database(path=DB_PATH):

    conn = get_conn(path)

    conn.executescript('''
    DROP TABLE IF EXISTS Service_History;
    DROP TABLE IF EXISTS Procedures;
    DROP TABLE IF EXISTS Assets;
    DROP TABLE IF EXISTS Frequencies;
''')

    create_freq(conn)
    create_assets(conn)
    create_proc(conn)
    create_history(conn)

    return conn

def insert_freq(conn):

    frequencies = load_frequencies(DATA_DIR/ 'frequencies.csv')

    for freq, days in frequencies.items():
        conn.execute('''INSERT INTO Frequencies (service_frequency, service_interval_days)
            VALUES ( ?,? )''', (freq, days) )

def insert_assets(conn, data_dir=DATA_DIR):
     
    good, rejected = load_assets(data_dir/ 'assets.csv')

    for line_num, row in good:
        conn.execute(
            'INSERT INTO Assets (asset_id, type, description, location, commissioning_date, status, linked_asset_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (row['asset_id'], row['type'], row['description'], row['location'],
             row['commissioning_date'], row['status'], None))

    for line_num, row in good:
        if row['linked_asset_id'] is not None:
            conn.execute(
                'UPDATE Assets SET linked_asset_id = ? WHERE asset_id = ?',
                (row['linked_asset_id'], row['asset_id'])) 

def insert_proc(conn, data_dir=DATA_DIR):
    frequencies = load_frequencies(DATA_DIR / 'frequencies.csv')
    good_assets, rejected_assets = load_assets(data_dir / 'assets.csv')
    valid_asset_ids = {row['asset_id'] for line_num, row in good_assets}
    good, rejected = load_procedures(data_dir/ 'procedures.csv', valid_asset_ids, frequencies)

    for line_num, row in good:
        conn.execute(
            'INSERT INTO Procedures (procedure_id, asset_id, description, service_frequency) VALUES (?, ?, ?, ?)',
            (row['procedure_id'], row['asset_id'], row['description'], row['service_frequency']))

def insert_history(conn, data_dir=DATA_DIR):
    frequencies = load_frequencies(DATA_DIR / 'frequencies.csv')
    good_assets, rejected_assets = load_assets(data_dir / 'assets.csv')
    valid_asset_ids = {row['asset_id'] for line_num, row in good_assets}
    good_proc, rejected_proc = load_procedures(data_dir/ 'procedures.csv', valid_asset_ids, frequencies)
    asset_dates = {row['asset_id']: datetime.strptime(row['commissioning_date'], DATE_FMT) for line_num, row in good_assets}
    procedure_commissioning = {row['procedure_id']: asset_dates[row['asset_id']] for line_num, row in good_proc}
    today = datetime.now()
    good, rejected = load_service_history(data_dir/ 'service_history.csv', procedure_commissioning, today)

    for line_num, row in good:
        conn.execute(
            'INSERT INTO Service_History (record_id, procedure_id, date_completed, notes) VALUES (?, ?, ?, ?)',
            (row['record_id'], row['procedure_id'], row['date_completed'], row['notes']))

def load_database(path=DB_PATH, data_dir=DATA_DIR):

    conn = build_database(path)

    insert_freq(conn)
    insert_assets(conn, data_dir=data_dir)
    insert_proc(conn, data_dir=data_dir)
    insert_history(conn, data_dir=data_dir)

    conn.commit()
    return conn
