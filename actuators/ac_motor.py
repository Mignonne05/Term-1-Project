from gpiozero import OutputDevice

from config import AC_MOTOR_PIN


class ACMotor:
    def __init__(self):
        self.control = OutputDevice(
            AC_MOTOR_PIN,
            active_high=True,
            initial_value=False,
        )

    def on(self):
        self.control.on()

    def off(self):
        self.control.off()

    def close(self):
        self.off()
        self.control.close()