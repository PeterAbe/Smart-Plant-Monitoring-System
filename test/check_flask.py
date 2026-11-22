import sys
import types
from unittest.mock import MagicMock

# Mock only the physical pump hardware
mock_pump = types.ModuleType("hardware.water_pump")
mock_pump.pump_on = MagicMock()
mock_pump.pump_off = MagicMock()

sys.modules["hardware.water_pump"] = mock_pump

import app

client = app.app.test_client()

response = client.post(
    "/api/manual-water",
    json={"duration": 5}
)

print("Status code:", response.status_code)
print("Response:", response.get_json())