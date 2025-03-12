
import asyncio
import pwmio
import simpleio
import keypad

from time import sleep
from adafruit_motor import servo
from digitalio import DigitalInOut, Direction

from CircuitPython_LTC2943 import Mode, Prescaler

class BatteryMonitor():
    def __init__(self, bms, display, charging_pin=None, buzzer=None) -> None:
        self.bms = bms
        self.display = display
        self.buzzer = buzzer
        # simpleio.tone(board.D9, 440, duration=1.0)
        self._charging_pin = DigitalInOut(charging_pin)
        self._charging_pin.direction = Direction.INPUT
        self._number_of_steps = display.get_number_of_segments()
        self._charge_step = ((bms.charge_range[1] - bms.charge_range[0]) 
                            / self._number_of_steps)
        # DEBUG
        print("")
        print(self.bms.temperature)
        print(self.bms.accumulated_charge)

        # INIT
        self.bms.adc_mode = Mode.AUTOMATIC
        self.bms.prescaler = Prescaler.PRES_M64

    async def status(self):
        while True:
            # LOCK the routine until it gets the data ?
            cstatus = self.bms.accumulated_charge
            level = int(cstatus / self._charge_step)
            self.display.bits = 0x3ff >> (self._number_of_steps - level)
            print(cstatus, self.bms.temperature, level, self.bms.current)
            await asyncio.sleep(0.5)

class BreakController():
    def __init__(self, servo_pin,  remote_button, wired_button, test_pin) -> None:
        self._pwm = pwmio.PWMOut(servo_pin, duty_cycle=2 ** 15, frequency=50)
        self._servo = servo.Servo(self._pwm)
        self.test_pin = DigitalInOut(test_pin)
        self.test_pin.direction = Direction.OUTPUT
        self.test_pin.value = False

        self._keys = keypad.Keys((remote_button, wired_button),
                                 value_when_pressed=True, pull=False)

    # TODO reset servo position to the state, where it detects the pressure 
    # TODO then define how the button 0 should behave
    # TODO steps and intervals to break for the button 1???

    async def active(self):
        while True:
            event = self._keys.events.get()
            if event:
                # print(event.pressed)
                print(event)
            await asyncio.sleep(0.1)
