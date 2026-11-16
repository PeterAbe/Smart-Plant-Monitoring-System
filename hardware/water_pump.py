import time
from gpiozero import OutputDevice

relay = OutputDevice(17, active_high=True, initial_value=False)

def TurnO():
    relay.on()
        
    
def TurnOff():
    relay.off()