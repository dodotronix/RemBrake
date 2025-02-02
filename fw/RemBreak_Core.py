
# SPDX-License-Identifier: MIT

import asyncio
import keypad
import pwmio
import neopixel
import board
import time

from adafruit_motor import servo
from digitalio import DigitalInOut, Direction
from simpleio import DigitalOut, DigitalIn

from CircuitPython_MY9221 import MY9221
from CircuitPython_LTC2943 import LTC2943
from RemBreak_Battery import BatteryMonitor
from RemBreak_Display import Display
from RemBreak_Wavekit import Tones

class RemBreakBoard():
    def __init__(self, layout) -> None:

        def create_layout(d):
            tmp = {}
            for k,v in d.items():
                tmp[k] = getattr(board, v)
            return tmp

        lt = create_layout(layout)

        # ACTUATOR INIT
        pwm = pwmio.PWMOut(lt["actuator"], duty_cycle=2 ** 15, frequency=50)
        self.actuator = servo.Servo(pwm)

        # ACTUATOR POWER SWITCH INIT
        self.actuator_switch = DigitalOut(lt["actuator_switch"])

        # REMOTE SWITCH & HANDLEBARS BUTTON INIT AS KEYS
        self.keys = keypad.Keys((lt["remote_switch"], 
                                 lt["handlebars_button"]),
                                value_when_pressed=True, pull=False)

        # SOUND MENU INIT
        pwm = pwmio.PWMOut(lt["buzzer"], variable_frequency=True)
        self.tones = Tones(pwm)

        # LEDBAR DISPLAY INIT
        self._my9221 = MY9221(lt["ledbar_di"], lt["ledbar_dcki"])
        self.display = Display(self._my9221, self.tones)

        # BATTERY MANAGEMENT SYSTEM (BMS) + ALARM PIN INIT + CHANGING PIN INIT
        self._bms = LTC2943(board.I2C())
        self._charging = DigitalIn(lt["charging"])
        self.plugged = DigitalIn(lt["plugged"])
        self.battery = BatteryMonitor(self._bms, self.display, 
                                      self.plugged, self._charging)

        # DEBUG STATE LED
        self.pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

class BreakController():
    def __init__(self, brd: RemBreakBoard) -> None:
        self._pixel = brd.pixel
        self.battery = brd.battery
        self.actuator = brd.actuator
        self.keys = brd.keys
        self.plugged = brd.plugged

        # coroutines
        self.busy = None # break is in use

        self.supervisor = False # remote button active 
        self.level = 0 # actual breaking level
        self.force = 0 # mA (force is proportional to force applied)
        self.angle = 90
        self.offset = 0
        self.active_keys = [False, False]

        self.red = 0
        self.blue = 0
        self.rgb = (0, 0, 0)

    # TODO battery under voltage set error flag and disconnect servo

    def start(self):
        async def main():
            b = asyncio.create_task(self.blink())
            c = asyncio.create_task(self.handle_led())
            d = asyncio.create_task(self.battery.start())
            e = asyncio.create_task(self.controller())
            f = asyncio.create_task(self.key_menu())
            await asyncio.gather(b, c, d, e, f)
        asyncio.run(main())

    async def controller(self):
        """ monitors the key presses and invokes breaking sequence """
        while True:
            self.actuator.angle = self.angle
            self.event = self.keys.events.get()
            if self.event:
                if self.event.pressed and self.event.key_number == 0:
                    self.active_keys[0] = time.monotonic()
                    print("Remote")
                elif self.event.pressed and self.event.key_number == 1:
                    self.active_keys[1] = time.monotonic()
                    print("Handlebars")
                elif self.event.released:
                    self.active_keys[self.event.key_number] = False
            await asyncio.sleep(0.2)

    async def key_menu(self):
        while True:
            if(isinstance(self.active_keys[0], float) 
                   and isinstance(self.active_keys[1], float)):

                    print("both keys are active")

                    tmp = time.monotonic()
                    dt = [tmp - self.active_keys[0], tmp - self.active_keys[1]]

                    if (dt[0] > 5 and dt[1] > 5):
                        if self.busy == None or self.busy.done():
                            self.busy = asyncio.create_task(self.battery.reset())
                            self.red = 10

            elif(isinstance(self.active_keys[0], float)):
                # self.force = -0.2
                # self.busy = asyncio.create_task(self.breaking_sequence(10))
                # self.supervisor = True

                if self.event: 
                    print("this will run the breaking sequence")

            elif(isinstance(self.active_keys[1], float)):
                # TODO steps breaking when pressed for longer period
                # self.busy = asyncio.create_task(self.breaking_sequence(2))

                if self.event: 
                    print("this will run the breaking sequence")

            await asyncio.sleep(0.2)
        
    async def breaking_sequence(self, timeout):
        task = asyncio.create_task(self.squeez())
        await asyncio.sleep(timeout)
        self.angle = 90
        print("canceling breaking sequence task")
        task.cancel()

    async def squeez(self):
        p = 10
        i = 5 
        d = 2
        sum_e = 0
        while True:
            amps = self.battery.current

            # PID regulator 
            e = (self.force - amps[0])
            sum_e += e
            new_angle = self.angle + p*e + i*sum_e + d*(amps[0] - amps[1])
            if (e > 0.01 or e < -0.01):
                self.angle = new_angle

            # DEBUG
            # print(f"error:{e}, error sum: {sum_e}")
            # print(f"current:{amps[0]}, current_error: {amps[0] - amps[1]}")
            # print(f"angle:{self.angle}, new_angle: {new_angle}")
            await asyncio.sleep(0.2)

    # DEBUGGING
    async def blink(self):
        while True:
            self.blue = 10
            await asyncio.sleep(0.2)
            self.blue = 0
            await asyncio.sleep(0.2)

    async def handle_led(self):
        while True:
            self.rgb = (self.red, 0, self.blue)
            self._pixel.fill(self.rgb)
            await asyncio.sleep(0.2)
