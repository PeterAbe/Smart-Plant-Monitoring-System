import sqlite3
import config
from pathlib import Path

# initialize the database connection
def db_connect(db_path=None):
    if db_path is None:
        db_path = Path(config.DATABASE_PATH)
    if str(db_path) != ":memory:":
        path_object = Path(db_path)
        if not path_object.parent.exists():
            path_object.parent.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {path_object.parent}")
    conn = sqlite3.connect(db_path)
    # allow access to columns by name
    conn.row_factory = sqlite3.Row
    # enables relational integrity and foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    # enables write-ahead logging for better concurrency
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

# initialize the database schema
def db_init(conn = None):
    owns_connection = False
    if conn is None:
        conn = db_connect()
        owns_connection = True
    try:
        with open(config.SCHEMA_PATH, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.execute("""
            INSERT OR IGNORE INTO dashboard_settings(
                id, plant_name, moisture_threshold,
                watering_duration,
                automatic_watering_enabled,
                temperature_unit
                ) VALUES (1,?,?,?,?,?)""", (
                    config.DEFAULT_PLANT_NAME,
                    config.DEFAULT_MOISTURE_THRESHOLD,
                    config.DEFAULT_WATERING_DURATION_SECONDS,
                    int(config.DEFAULT_ALLOW_AUTOMATIC_WATERING),
                    config.DEFAULT_TEMPERATURE_UNITS
                ))
        conn.commit()
        print("Database initialized successfully.")
    finally:
        if owns_connection:
            conn.close()

if __name__ == "__main__":
    db_init()