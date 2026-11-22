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
def get_readings_for_day(day=None, tz=None, conn=None):
    if day is None:
        day = datetime.now(tz).date()
    elif isinstance(day, datetime):
        raise ValueError("Pass a date or in format of 'YYYY-MM-DD' string, not a datetime")
    elif isinstance(day, date):
        pass
    elif isinstance(day, str):
        day = date.fromisoformat(day)
    else:
        raise ValueError("day must be a 'YYYY-MM-DD' string or a date object.")
    def _midnight(day):
        if tz is None:
            return datetime.combine(day, time()).astimezone()
        return datetime.combine(day, time(), tzinfo=tz)
    start = _midnight(day)
    end = _midnight(day + timedelta(days=1))
    interval = max(1, config.LOGGING_INTERVAL_SECONDS)
    limit = (25 * 60 * 60) // interval + 100
    return get_readings(start_time=start, end_time=end, limit=limit, conn=conn)

# function to validate watering information

# Function to add a watering event to the database
def add_watering_event(duration,triggered_by,moisture_before,moisture_after=None,extra_text=None,timestamp=None,conn=None):
    # Validate watering duration
    if isinstance(duration, bool) or not isinstance(duration, int):
        raise ValueError("Watering duration must be an integer.")
    if not (
        config.MIN_WATERING_DURATION_SECONDS
        <= duration
        <= config.MAX_WATERING_DURATION_SECONDS
    ):
        raise ValueError("Watering duration is out of range.")
    # Validate how watering was triggered
    if triggered_by not in ("manual", "automatic"):
        raise ValueError("triggered_by must be 'manual' or 'automatic'.")
    # Validate moisture readings
    if moisture_before is None or not (
        config.MIN_MOISTURE <= moisture_before <= config.MAX_MOISTURE
    ):
        raise ValueError("Invalid moisture_before value.")
    if moisture_after is not None:
        if not (
            config.MIN_MOISTURE <= moisture_after <= config.MAX_MOISTURE
        ):
            raise ValueError("Invalid moisture_after value.")
    # Set or normalize timestamp
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    else:
        timestamp = _normalize_timestamp(timestamp)
    # Convert optional extra information to JSON
    if extra_text is not None:
        if not isinstance(extra_text, dict):
            raise ValueError("Extra data must be a dictionary.")
        extra_text = json.dumps(extra_text)
    # Connect to database if no connection was supplied
    owns_connection = False
    if conn is None:
        conn = db_connect()
        owns_connection = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO watering_events (timestamp,duration,triggered_by,moisture_before,moisture_after,extra_text)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp,duration,triggered_by,moisture_before,moisture_after,extra_text))
        conn.commit()
        return cursor.lastrowid
    finally:
        if owns_connection:
            conn.close()


# Function to retrieve watering history from the database
def get_watering_events(limit=100, conn=None):
    # Validate result limit
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")
    owns_connection = False
    if conn is None:
        conn = db_connect()
        owns_connection = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM watering_events ORDER BY timestamp DESC, id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        events = []
        for row in rows:
            event = dict(row)
            if event["extra_text"] is not None:
                event["extra_text"] = json.loads(event["extra_text"])
            events.append(event)
        return events
    finally:
        if owns_connection:
            conn.close()


# Function to retrieve dashboard settings
def get_dashboard_settings(conn=None):
    owns_connection = False
    if conn is None:
        conn = db_connect()
        owns_connection = True
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM dashboard_settings WHERE id = 1
        """)
        row = cursor.fetchone()
        if row is None:
            return None
        settings = dict(row)
        settings["automatic_watering_enabled"] = bool(
            settings["automatic_watering_enabled"]
        )
        return settings
    finally:
        if owns_connection:
            conn.close()


# Function to update dashboard settings
def update_dashboard_settings(plant_name=None,moisture_threshold=None,watering_duration=None,automatic_watering_enabled=None,temperature_unit=None,conn=None):
    # Validate settings before updating
    if plant_name is not None and not plant_name.strip():
        raise ValueError("Plant name cannot be empty.")
    if moisture_threshold is not None:
        if not (
            config.MIN_MOISTURE_THRESHOLD
            <= moisture_threshold
            <= config.MAX_MOISTURE_THRESHOLD
        ):
            raise ValueError("Moisture threshold is out of range.")
    if watering_duration is not None:
        if isinstance(watering_duration, bool) or not isinstance(watering_duration, int):
            raise ValueError("Watering duration must be an integer.")
        if not (
            config.MIN_WATERING_DURATION_SECONDS
            <= watering_duration
            <= config.MAX_WATERING_DURATION_SECONDS
        ):
            raise ValueError("Watering duration is out of range.")
    if automatic_watering_enabled is not None:
        if not isinstance(automatic_watering_enabled, bool):
            raise ValueError("Automatic watering setting must be True or False.")
    if temperature_unit is not None:
        if temperature_unit not in ("C", "F"):
            raise ValueError("Temperature unit must be C or F.")
    # Build update query using only supplied settings
    updates = []
    params = []
    if plant_name is not None:
        updates.append("plant_name = ?")
        params.append(plant_name.strip())
    if moisture_threshold is not None:
        updates.append("moisture_threshold = ?")
        params.append(moisture_threshold)
    if watering_duration is not None:
        updates.append("watering_duration = ?")
        params.append(watering_duration)
    if automatic_watering_enabled is not None:
        updates.append("automatic_watering_enabled = ?")
        params.append(int(automatic_watering_enabled))
    if temperature_unit is not None:
        updates.append("temperature_unit = ?")
        params.append(temperature_unit)
    if not updates:
        return
    owns_connection = False
    if conn is None:
        conn = db_connect()
        owns_connection = True
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            UPDATE dashboard_settings SET {", ".join(updates)} WHERE id = 1
            """,
            params
        )
        if cursor.rowcount == 0:
            raise ValueError("Dashboard settings have not been initialized.")
        conn.commit()
    finally:
        if owns_connection:
            conn.close()
