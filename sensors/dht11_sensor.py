import adafruit_dht
import board


class DHT11Sensor:
    def __init__(self):
        # GPIO4 is physical pin 7.
        self.sensor = adafruit_dht.DHT11(board.D4, use_pulseio=False)

    def read(self):
        temperature_c = self.sensor.temperature
        humidity_percent = self.sensor.humidity
        return temperature_c, humidity_percent

    def close(self):
        self.sensor.exit()