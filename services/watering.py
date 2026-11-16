# services/watering.py
import time
import threading
# Target the exact path to your pump code
from hardware.water_pump import * 

def _thread_function(duration):
    TurnOn()
    time.sleep(duration)  
    TurnOff()

def manual_watering(duration):
    threading.Thread(target=_thread_function, args=(duration,), daemon=True).start()
    return 1
