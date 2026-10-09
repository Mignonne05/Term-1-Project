import board
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15

from config import ADS1115_ADDRESS, LDR_BRIGHT_THRESHOLD_V


class LDRSensors:
    def __init__(self):
        i2c = board.I2C()
        ads = ADS1115(i2c, address=ADS1115_ADDRESS)

        self.channels = {
            1: AnalogIn(ads, ads1x15.Pin.A0),
            2: AnalogIn(ads, ads1x15.Pin.A1),
            3: AnalogIn(ads, ads1x15.Pin.A2),
            4: AnalogIn(ads, ads1x15.Pin.A3),
        }

    def read_zones(self):
        readings = {}

        for zone, channel in self.channels.items():
            voltage = channel.voltage
            readings[zone] = {
                "voltage": voltage,
                "bright": voltage >= LDR_BRIGHT_THRESHOLD_V,
            }

        return readings