import json
from datetime import datetime, timezone
import config
from database.db import db_connect

# function to add sensor reading to the database
# sample usage:
# add_sensor_reading(moisture=50, temperature=25, humidity=60, extra_text={"location": "greenhouse"}, timestamp="2026-11-14T13:00:00+00:00")
# returns the id of the inserted row
def add_sensor_reading(moisture, temperature= None, humidity=None,
                        extra_text=None, timestamp=None, conn=None):

    if moisture is None:
        raise ValueError("Moisture value is required.")
    if not (config.MIN_MOISTURE <= moisture <= config.MAX_MOISTURE):
        raise ValueError(f"Moisture value {moisture} is out of range.")
    if temperature is not None:
        if not (config.MIN_TEMPERATURE <= temperature <= config.MAX_TEMPERATURE):
            raise ValueError(f"Temperature value {temperature} is out of range.")
    if humidity is not None:
        if not (config.MIN_HUMIDITY <= humidity <= config.MAX_HUMIDITY):
            raise ValueError(f"Humidity value {humidity} is out of range.")
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')

    if extra_text is not None:
        if not isinstance(extra_text, dict):
            raise ValueError("Extra data must be a dictionary.")
        extra_text = json.dumps(extra_text)
    owns_connection = False
    if conn is None:
        conn = db_connect()
        owns_connection = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO readings (moisture, temperature, humidity, extra_text, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (moisture, temperature, humidity, extra_text, timestamp))
        conn.commit()
        return cursor.lastrowid
    finally:
        if owns_connection:
            conn.close()

# function to get the latest sensor reading from the database
# sample usage:
# latest_reading = get_latest_reading()
# returns a dictionary with the latest reading or None if no readings are found
# sample output:
# {timestamp: "2026-11-14T13:00:00+00:00", moisture: 50, temperature: 25, humidity: 60, extra_text: {"location": "greenhouse"}}
def get_latest_reading(conn=None):
    owns_connection = False
    if conn is None:
        conn = db_connect()
        owns_connection = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM readings
            ORDER BY timestamp DESC, id DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row is None:
            return None
        reading = dict(row)
        if reading['extra_text'] is not None:
            reading['extra_text'] = json.loads(reading['extra_text'])
        return reading
    finally:
        if owns_connection:
            conn.close()