from gpiozero import OutputDevice

relay = OutputDevice(17, active_high=True, initial_value=False)

def pump_on():
    relay.on()
def pump_off():
    relay.off()