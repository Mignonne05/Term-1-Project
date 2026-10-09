import csv
import time
import firebase_admin
from firebase_admin import db
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path

from actuators.ac_motor import ACMotor
from actuators.fan_control import FanControl
from actuators.led_control import ZoneLEDs
from automation.controller import RoomController
from sensors.dht11_sensor import DHT11Sensor
from sensors.ldr_sensor import LDRSensors
from sensors.pir_sensor import PIRSensors




LOG_PATH = Path(__file__).resolve().parent / "room_log.csv"

FIELDNAMES = ["timestamp", "temperature_c", "humidity_percent"]

for zone in range(1, 5):
    FIELDNAMES += [
        f"zone{zone}_motion",
        f"zone{zone}_occupied",
        f"zone{zone}_light_v",
        f"zone{zone}_bright",
        f"zone{zone}_led_on",
    ]

FIELDNAMES += ["fan1_on", "fan2_on", "ac_motor_on"]


def main():
    firebase_admin.initialize_app(options={
        "databaseURL": (
            "https://smart-classroom-119ef-default-rtdb."
            "asia-southeast1.firebasedatabase.app"
        )
    })
    
    controller = RoomController()

    with ExitStack() as stack:
        pir = PIRSensors()
        stack.callback(pir.close)

        dht = DHT11Sensor()
        stack.callback(dht.close)

        ldr = LDRSensors()

        leds = ZoneLEDs()
        stack.callback(leds.close)

        fans = FanControl()
        stack.callback(fans.close)

        motor = ACMotor()
        stack.callback(motor.close)

        log_has_header = LOG_PATH.exists() and LOG_PATH.stat().st_size > 0

        with LOG_PATH.open("a", newline="", encoding="utf-8") as log_file:
            writer = csv.DictWriter(log_file, fieldnames=FIELDNAMES)

            if not log_has_header:
                writer.writeheader()
            last_history_upload = time.monotonic() - 60
            while True:
                motion = pir.read_zones()
                light = ldr.read_zones()

                try:
                    temperature_c, humidity_percent = dht.read()
                except RuntimeError as error:
                    print(f"DHT11 read failed: {error}")
                    temperature_c = None
                    humidity_percent = None

                decision = controller.decide(
                    motion,
                    light,
                    temperature_c,
                    time.monotonic(),
                )

                for zone, on in decision["leds"].items():
                    leds.set_zone(zone, on)

                for fan, on in decision["fans"].items():
                    fans.set_fan(fan, on)

                if decision["ac"]:
                    motor.on()
                else:
                    motor.off()

                row = {
                    "timestamp": datetime.now().astimezone().isoformat(
                        timespec="seconds"
                    ),
                    "temperature_c": temperature_c,
                    "humidity_percent": humidity_percent,
                    "fan1_on": decision["fans"][1],
                    "fan2_on": decision["fans"][2],
                    "ac_motor_on": decision["ac"],
                }

                for zone in range(1, 5):
                    row[f"zone{zone}_motion"] = motion[zone]
                    row[f"zone{zone}_occupied"] = decision["occupied"][zone]
                    row[f"zone{zone}_light_v"] = round(
                        light[zone]["voltage"], 3
                    )
                    row[f"zone{zone}_bright"] = light[zone]["bright"]
                    row[f"zone{zone}_led_on"] = decision["leds"][zone]

                writer.writerow(row)
                log_file.flush()
                try:
                    db.reference("rooms/lecture_room_1/current").set(row)

                    now = time.monotonic()
                    if now - last_history_upload >= 60:
                        db.reference("rooms/lecture_room_1/history").push(row)
                        last_history_upload = now
                except Exception as error:
                    print(f"Firebase upload failed: {error}")

                print(f"Saved reading: {row['timestamp']}")
                time.sleep(2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped. Outputs switched off.")