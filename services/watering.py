# services/watering.py
import time
import threading


# Target the exact path to your pump code
from hardware.water_pump import pump_on, pump_off 

def _thread_function(duration):
    try:
        pump_on()
        time.sleep(duration)
    finally:  
        pump_off()

def manual_watering(duration):
    threading.Thread(target=_thread_function, args=(duration,), daemon=True).start()
    return 1
