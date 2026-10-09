from gpiozero import LED

from config import LED_PINS


class ZoneLEDs:
    def __init__(self):
        self.leds = {
            zone: LED(pin, initial_value=False)
            for zone, pin in LED_PINS.items()
        }

    def set_zone(self, zone, on):
        if zone not in self.leds:
            raise ValueError(f"Unknown zone: {zone}")

        if on:
            self.leds[zone].on()
        else:
            self.leds[zone].off()

    def close(self):
        for led in self.leds.values():
            led.off()
            led.close()