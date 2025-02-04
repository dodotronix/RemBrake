
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
        print("\nTODO: cut servo power")

        # REMOTE SWITCH & HANDLEBARS BUTTON INIT AS KEYS
        self.keys = keypad.Keys((lt["remote_switch"], 
                                 lt["handlebars_button"]),
                                value_when_pressed=True, pull=False)

        # LEDBAR DISPLAY INIT
        self._my9221 = MY9221(lt["ledbar_di"], lt["ledbar_dcki"])
        self.display = Display(self._my9221)

        # SOUND MENU INIT
        pwm = pwmio.PWMOut(lt["buzzer"], variable_frequency=True)
        self.tones = Tones(pwm)

        # BATTERY MANAGEMENT SYSTEM (BMS) + ALARM PIN INIT + CHANGING PIN INIT
        self._bms = LTC2943(board.I2C())
        self._charging = DigitalIn(lt["charging"])
        self.plugged = DigitalIn(lt["plugged"])
        self.battery = BatteryMonitor(self._bms, self.display, self.tones, 
                                      self.actuator_switch, self.plugged, 
                                      self._charging)

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

        self.force = 0 # regulated force
        self.active = False # PID active
        self.angle = 90 # initial angle
        self.max_force = -1 # 1 A
        self.supervisor = False
        self.user = False
        self.debug = True

        self.active_keys = [False, False]

        self.red = 0
        self.blue = 0
        self.rgb = (0, 0, 0)

    # TODO battery under voltage set error flag and disconnect servo

    def start(self):
        async def main():
            a = asyncio.create_task(self.breaking())
            b = asyncio.create_task(self.blink())
            c = asyncio.create_task(self.handle_led())
            d = asyncio.create_task(self.battery.start())
            e = asyncio.create_task(self.controller())
            f = asyncio.create_task(self.key_menu())
            await asyncio.gather(a, b, c, d, e, f)
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
            # NOTE the system has to be on and connected to the usb
            # then if you press both buttons and wait for at least 5s 
            # it starts reset battery sequence and waits until the battery
            # is fully charged, then it resets the internal charge counter

            if(isinstance(self.active_keys[0], float) 
                   and isinstance(self.active_keys[1], float) and not self.plugged.value):

                    print("both keys are active")

                    tmp = time.monotonic()
                    dt = [tmp - self.active_keys[0], tmp - self.active_keys[1]]

                    if (dt[0] > 5 and dt[1] > 5):
                        try:
                            self.busy.cancel()
                            self.user = False
                            self.supervisor = False
                            self.active = False
                        except:
                            pass
                        self.busy = asyncio.create_task(self.battery.reset())
                        self.red = 10

                        # wait until both keys are inactive
                        while self.active_keys[0] or self.active_keys[1]:
                            await asyncio.sleep(0.2)
                        self.red = 0
                        print("both were released")

            if(isinstance(self.active_keys[0], float)):
                print("running supervisor breaking")
                if not self.supervisor:
                    try:
                        self.busy.cancel() # cancel old breaking
                    except:
                        pass
                    self.busy = asyncio.create_task(self.supervisor_breaking(10))

            elif(isinstance(self.active_keys[1], float)) and not self.supervisor:
                print("running handlebars breaking")
                if not self.supervisor and not self.user:
                    try:
                        self.busy.cancel() # cancel old breaking
                    except:
                        pass

                    self.busy = asyncio.create_task(self.handlebars_breaking(1, -0.1))

            elif not self.active_keys[1] and self.user:
                print("turn off handlebars task")
                self.user = False
                self.active = False
                self.busy.cancel() # cancel old job

            await asyncio.sleep(0.2)

    async def handlebars_breaking(self, time_step, force_step):
        self.active = True
        self.user = True
        while True:
            tmp_force = self.force + force_step
            if tmp_force > self.max_force:
                self.force = tmp_force
            elif tmp_force != self.max_force:
                self.force = self.max_force
            await asyncio.sleep(time_step)
        
    async def supervisor_breaking(self, timeout):
        self.user = False
        self.supervisor = True
        self.force = -0.2
        self.active = True
        await asyncio.sleep(timeout)
        self.active = False
        self.supervisor = False
        print("canceling supervisor breaking")

    async def breaking(self):
        p = 10
        i = 5 
        d = 2
        sum_e = 0
        while True:
            if self.active:
                amps = self.battery.current

                # PID regulator 
                e = (self.force - amps[0])
                sum_e += e
                new_angle = self.angle + p*e + i*sum_e + d*(amps[0] - amps[1])
                if self.debug:
                    print("Your current force: ", self.force)
                    # print(f"error:{e}, error sum: {sum_e}")
                    # print(f"current:{amps[0]}, current_error: {amps[0] - amps[1]}")
                    # print(f"angle:{self.angle}, new_angle: {new_angle}")
                elif (e > 0.01 or e < -0.01):
                    self.angle = new_angle
            else:
                self.angle = 90 # if PID is not active go to initial position
                self.force = 0

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
