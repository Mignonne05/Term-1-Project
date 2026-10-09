from gpiozero import MotionSensor

from config import PIR_PINS


class PIRSensors:
    def __init__(self):
        self.sensors = {
            zone: MotionSensor(pin)
            for zone, pin in PIR_PINS.items()
        }

    def read_zones(self):
        return {
            zone: sensor.motion_detected
            for zone, sensor in self.sensors.items()
        }

    def close(self):
        for sensor in self.sensors.values():
            sensor.close()