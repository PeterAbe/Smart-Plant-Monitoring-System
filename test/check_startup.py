import sys
import types
from unittest.mock import MagicMock

# Mock physical pump hardware
mock_pump = types.ModuleType("hardware.water_pump")
mock_pump.pump_on = MagicMock()
mock_pump.pump_off = MagicMock()
sys.modules["hardware.water_pump"] = mock_pump

# Mock monitoring startup
mock_monitoring = types.ModuleType("services.monitoring")
mock_monitoring.start_monitoring = MagicMock(
    side_effect=lambda: print("Monitoring started.")
)
sys.modules["services.monitoring"] = mock_monitoring

# Import app and prevent Flask from starting its server
import app
app.app.run = MagicMock(
    side_effect=lambda **kwargs: print("Flask server startup requested.")
)

# Execute run.py as the main program
import runpy
runpy.run_module("run", run_name="__main__")

print("Startup test completed.")