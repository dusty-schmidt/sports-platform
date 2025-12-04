import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'stats.db'
SCHEMA_PATH = Path(__file__).parent / 'schema.sql'

def init_db():
    # 1. Connect to (or create) the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 2. Apply the schema
    print("Applying schema...")
    with open(SCHEMA_PATH, 'r') as f:
        cursor.executescript(f.read())

    # 3. Seed Sports and Leagues
    print("Seeding reference data...")
    
    # Sports
    sports = [
        (1, 'Tennis'),
        (2, 'Basketball'),
        (3, 'Football'),
        (4, 'Baseball')
    ]
    cursor.executemany("INSERT OR IGNORE INTO sports (id, name) VALUES (?, ?)", sports)

    # Leagues
    leagues = [
        (1, 1, 'ATP'),  # Tennis
        (2, 1, 'WTA'),  # Tennis
        (3, 2, 'NBA'),  # Basketball
        (4, 3, 'NFL'),  # Football
        (5, 4, 'MLB')   # Baseball
    ]
    cursor.executemany("INSERT OR IGNORE INTO leagues (id, sport_id, name) VALUES (?, ?, ?)", leagues)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
