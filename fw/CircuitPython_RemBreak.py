
import pwmio
import simpleio

from time import sleep
from adafruit_motor import servo
from digitalio import DigitalInOut, Direction

from CircuitPython_LTC2943 import Mode, Prescaler

class BatteryMonitor():
    def __init__(self, bms, display, charging_pin=None, buzzer=None) -> None:
        self.bms = bms
        self.display = display
        self.buzzer = buzzer
        self._charging_pin = DigitalInOut(charging_pin)
        self._charging_pin.direction = Direction.INPUT
        self._number_of_steps = display.get_number_of_segments()
        self._charge_step = ((bms.charge_range[1] - bms.charge_range[0]) 
                            / self._number_of_steps)

        # DEBUG
        print("")
        print(self.bms.temperature)
        print(self.bms.accumulated_charge)
        # self.start()

    def start(self):
        self.bms.adc_mode = Mode.AUTOMATIC
        self.bms.prescaler = Prescaler.PRES_M64
        # TODO coroutine which periodically 
        # checks the state of changing
        if not self._charging_pin.value:
            self.charging()
        else:
            self.discharging()

    def charging(self):
        self.display.bits = 0x3ff
        for i in range(0, 255, 25):
            self.display.intensity = i
            sleep(0.05)
        for i in range(255, 0, -25):
            self.display.intensity = i
            sleep(0.05)

    def discharging(self):
        self.display.bits = 0


class BreakController():
    def __init__(self, servo,  remote_button, wired_button) -> None:
        pass

# rembut = digitalio.DigitalInOut(board.D0)
# rembut.direction = digitalio.Direction.INPUT

# handbut = digitalio.DigitalInOut(board.SCK)
# handbut.direction = digitalio.Direction.INPUT

# pwm = pwmio.PWMOut(board.RX, duty_cycle=2 ** 15, frequency=50)
# my_servo = servo.Servo(pwm)
# simpleio.tone(board.D9, 440, duration=1.0)
