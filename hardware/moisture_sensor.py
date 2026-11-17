from smbus2 import SMBus

I2C_ADDRESS = 0x4B
COMMAND_CHANNEL_0 = 0x84  

DRY_VALUE = 255
WET_VALUE = 0


def read_moisture():
    with SMBus(1) as bus:
            raw_data = bus.read_byte_data(I2C_ADDRESS, COMMAND_CHANNEL_0)
            raw_percentage = ((DRY_VALUE -raw_data)/(DRY_VALUE - WET_VALUE))*100
            moisture_percentage = max(0, min(100, raw_percentage))
            return moisture_percentage
