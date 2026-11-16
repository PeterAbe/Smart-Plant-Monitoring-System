from smbus2 import SMBus

I2C_ADDRESS = 0x4B
COMMAND_CHANNEL_0 = 0x84  

dry_value = 255
wet_value = 0


def Read_Moisture():
    with SMBus(1) as bus:
            raw_data = bus.read_byte_data(I2C_ADDRESS, COMMAND_CHANNEL_0)
            raw_percentage = ((dry_value -raw_data)/(dry_value - wet_value))*100
            moisture_percentage = max(0, min(100, raw_percentage))
            return moisture_percentage
        
            