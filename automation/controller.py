from config import (
    AC_OFF_TEMP_C,
    AC_ON_TEMP_C,
    OCCUPANCY_HOLD_SECONDS,
)


class RoomController:
    def __init__(self):
        self.last_motion = {zone: None for zone in range(1, 5)}
        self.ac_on = False

    def decide(self, motion, light, temperature_c, now):
        occupied = {}

        for zone in range(1, 5):
            if motion[zone]:
                self.last_motion[zone] = now

            last_seen = self.last_motion[zone]
            occupied[zone] = (
                last_seen is not None
                and now - last_seen < OCCUPANCY_HOLD_SECONDS
            )

        leds = {
            zone: occupied[zone] and not light[zone]["bright"]
            for zone in range(1, 5)
        }

        fans = {
            1: occupied[1] or occupied[2],
            2: occupied[3] or occupied[4],
        }

        if temperature_c is None or not any(occupied.values()):
            self.ac_on = False
        elif self.ac_on:
            self.ac_on = temperature_c > AC_OFF_TEMP_C
        else:
            self.ac_on = temperature_c >= AC_ON_TEMP_C

        return {
            "occupied": occupied,
            "leds": leds,
            "fans": fans,
            "ac": self.ac_on,
        }