CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    -- these can be nullable incasese where the sensor fails to read a value or not connected
    temperature REAL,
    humidity REAL,
    moisture REAL NOT NULL,
    extra_text TEXT
);

CREATE TABLE IF NOT EXISTS watering_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    duration INTEGER NOT NULL,
    triggered_by TEXT NOT NULL CHECK (triggered_by IN ('manual', 'automatic')),
    moisture_before REAL NOT NULL,
    moisture_after REAL,
    extra_text TEXT
);

-- dashboard saves user settings so table for congfiguration
CREATE TABLE IF NOT EXISTS dashboard_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    plant_name TEXT,
    moisture_threshold REAL,
    watering_duration INTEGER,
    automatic_watering_enabled BOOLEAN,
    temperature_unit TEXT CHECK (temperature_unit IN ('C', 'F'))
);

-- indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings (timestamp);
CREATE INDEX IF NOT EXISTS idx_watering_events_timestamp ON watering_events (timestamp);