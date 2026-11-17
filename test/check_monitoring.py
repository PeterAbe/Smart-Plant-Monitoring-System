import sys
import types
from unittest.mock import MagicMock

mock_sensor = types.ModuleType("hardware.moisture_sensor")
mock_sensor.read_moisture = MagicMock()
sys.modules["hardware.moisture_sensor"] = mock_sensor

mock_pump = types.ModuleType("hardware.water_pump")
mock_pump.pump_on = MagicMock()
mock_pump.pump_off = MagicMock()
sys.modules["hardware.water_pump"] = mock_pump

mock_watering = types.ModuleType("services.watering")
mock_watering.manual_watering = MagicMock()
sys.modules["services.watering"] = mock_watering

import services.monitoring as monitoring

monitoring.get_dashboard_settings = MagicMock(return_value={
    "moisture_threshold": 30,
    "automatic_watering_enabled": True,
    "watering_duration": 5
})

# Simulate elapsed time
mock_clock = MagicMock(side_effect=[100, 110])
monitoring.time.monotonic = mock_clock

monitoring.last_automatic_watering_time = 0

first_result = monitoring.trigger_automatic_watering(20)
second_result = monitoring.trigger_automatic_watering(20)

print("First watering triggered:", first_result)
print("Second watering triggered:", second_result)
print("Total watering calls:", mock_watering.manual_watering.call_count)