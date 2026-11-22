
import sys
import time
from types import ModuleType
from unittest.mock import Mock

# Mock the physical pump
fake_pump = ModuleType("hardware.water_pump")
fake_pump.pump_on = Mock()
fake_pump.pump_off = Mock()
sys.modules["hardware.water_pump"] = fake_pump

# Mock the physical moisture sensor
fake_sensor = ModuleType("hardware.moisture_sensor")
fake_sensor.read_moisture = Mock()
sys.modules["hardware.moisture_sensor"] = fake_sensor

from database.db import db_init
from database.models import (
    get_dashboard_settings,
    update_dashboard_settings,
    get_latest_reading,
    get_watering_events
)

import services.monitoring as monitoring

# Initialize database
db_init()

# Save the original settings
original_settings = get_dashboard_settings()

try:
    # Configure automatic watering for the test
    update_dashboard_settings(
        moisture_threshold=30,
        watering_duration=1,
        automatic_watering_enabled=True
    )

    # Simulate three sensor readings
    simulated_readings = iter([20.0, 25.0, 30.0])
    monitoring.read_moisture = lambda: next(simulated_readings)

    # Run one complete monitoring cycle
    monitoring.monitoring_cycle()

    # Wait for the watering thread to finish
    time.sleep(1.5)

    # Check the three saved moisture readings
    latest_reading = get_latest_reading()
    print("Latest moisture reading:", latest_reading["moisture"])

    # Check the watering event
    events = get_watering_events(limit=1)
    print("Latest watering event:", events[0] if events else None)

    assert events, "No watering event was saved."
    assert events[0]["triggered_by"] == "automatic"
    assert events[0]["duration"] == 1
    assert events[0]["moisture_before"] == 25.0

    # Check mocked pump functions
    fake_pump.pump_on.assert_called_once()
    fake_pump.pump_off.assert_called_once()

    print("Complete monitoring-to-watering test passed!")

finally:
    # Restore the original dashboard settings
    update_dashboard_settings(
        plant_name=original_settings["plant_name"],
        moisture_threshold=original_settings["moisture_threshold"],
        watering_duration=original_settings["watering_duration"],
        automatic_watering_enabled=original_settings["automatic_watering_enabled"],
        temperature_unit=original_settings["temperature_unit"]
    )
