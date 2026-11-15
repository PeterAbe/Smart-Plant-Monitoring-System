import json
from datetime import datetime, timezone, date, time, timedelta
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
    else:
        timestamp = _normalize_timestamp(timestamp)

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
        return _row_to_dict(cursor.fetchone())
    finally:
        if owns_connection:
            conn.close()

# function to normalize timestamp input
def _normalize_timestamp(timestamp):
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        raise ValueError("Timestamp must be a string or datetime object.")
    
    if dt.tzinfo is None:
        raise ValueError("Timestamp must include timezone information.")
    
    return dt.astimezone(timezone.utc).isoformat(timespec='seconds')

# function to convert a database row to a dictionary
def _row_to_dict(row):
    if row is None:
        return None
    reading = dict(row)
    if reading['extra_text'] is not None:
        reading['extra_text'] = json.loads(reading['extra_text'])
    return reading

# function to get readings in a range
def get_readings(start_time=None,end_time=None,limit=1440, conn=None):
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    conditions = []
    params = []
    if start_time is not None:
        start_time = _normalize_timestamp(start_time)
        conditions.append("timestamp >= ?")
        params.append(start_time)
    if end_time is not None:
        end_time = _normalize_timestamp(end_time)
        conditions.append("timestamp < ?")
        params.append(end_time)
    if start_time is not None and end_time is not None and start_time >= end_time:
        raise ValueError("Start time must be less than or equal to end time.")
    query = "SELECT * FROM readings"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY timestamp ASC, id ASC LIMIT ?"
    params.append(limit)

    owns_connection = False
    if conn is None:
        conn = db_connect()
        owns_connection = True
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_dict(row) for row in rows]
    finally:
        if owns_connection:
            conn.close()
    
# function for getting a days worth of reading 
# returns all readings for one calendar day, oldest first, as a list of dicts
# returns [] if there are none
def get_readings_for_day(day=None,timezone=None,conn=None):
    if day is None:
        day = datetime.now(timezone).date()
    elif isinstance(day, datetime):
        raise ValueError("Pass a date or in format of 'YYYY-MM-DD' string, not a datetime")
    elif isinstance(day,date):
        pass
    elif isinstance(day, str):
        day = date.fromisoformat(day)
    else:
        raise ValueError("day must be a 'YYYY-MM-DD' string or a date object.")

    def _midnight(day):
        if timezone is None:
            return datetime.combine(day, time()).astimezone()
        return datetime.combine(day, time(), tzinfo=timezone)
    start = _midnight(day)
    end = _midnight(day + timedelta(days=1))
    interval = max(1, config.LOGGING_INTERVAL_SECONDS)
    limit = (25*60*60)//interval+100
    return get_readings(start_time=start,end_time=end,limit=limit,conn=conn)