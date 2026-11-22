from gpiozero import OutputDevice

relay = OutputDevice(17, active_high=False, initial_value=False)

pump_status= "OFF"

def pump_on():
    global pump_status
    relay.on()
    pump_status= "ON"
    print("Pump status: ", pump_status)
    
def pump_off():
    global pump_status
    relay.off()
    pump_status= "OFF"
    print("Pump status: ", pump_status)

def get_pump_status():
	return pump_status
