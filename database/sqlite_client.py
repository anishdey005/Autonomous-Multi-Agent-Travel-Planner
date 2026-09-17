import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'travel_cache.db')

def get_conn():
    """
    Create and return a SQLite database connection.
    Initializes tables if they don't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Initialize tables
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accommodations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT,
            provider_item_id TEXT,
            name TEXT,
            city TEXT,
            country TEXT,
            bedrooms INTEGER,
            price_per_night REAL,
            rating REAL,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT,
            airline TEXT,
            origin TEXT,
            destination TEXT,
            depart_time TEXT,
            arrive_time TEXT,
            price REAL,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    return conn
