# services/watering.py
import time
import threading
import config

from hardware.water_pump import pump_on, pump_off

def _thread_function(duration):
    try:
        pump_on()
        time.sleep(duration)
    finally:
        pump_off()


def manual_watering(duration):
    # Validate watering duration
    if isinstance(duration, bool) or not isinstance(duration, int):
        raise ValueError("Watering duration must be an integer.")
    if not (
        config.MIN_WATERING_DURATION_SECONDS
        <= duration
        <= config.MAX_WATERING_DURATION_SECONDS
    ):
        raise ValueError("Watering duration is out of range.")
    # Start watering in a separate thread
    watering_thread = threading.Thread(target=_thread_function,args=(duration,),daemon=True)
    watering_thread.start()
    return 1
