from gpiozero import OutputDevice

from config import FAN_RELAY_PINS, RELAY_ACTIVE_LOW


class FanControl:
    def __init__(self):
        self.relays = {
            fan: OutputDevice(
                pin,
                active_high=not RELAY_ACTIVE_LOW,
                initial_value=False,
            )
            for fan, pin in FAN_RELAY_PINS.items()
        }

    def set_fan(self, fan, on):
        if fan not in self.relays:
            raise ValueError(f"Unknown fan: {fan}")

        if on:
            self.relays[fan].on()
        else:
            self.relays[fan].off()

    def close(self):
        for relay in self.relays.values():
            relay.off()
            relay.close()