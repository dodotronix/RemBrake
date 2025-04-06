
# SPDX-License-Identifier: MIT

import asyncio
import keypad
import pwmio
import neopixel
import board

from adafruit_motor import servo
from digitalio import DigitalInOut, Direction
from simpleio import DigitalOut, DigitalIn

from CircuitPython_MY9221 import MY9221
from CircuitPython_LTC2943 import LTC2943, ALCC, Mode, Prescaler
from RemBrake_Wavekit import Composer

class DebuggingIndicator():
    def __init__(self, pin, message: Message, period=0.2):
        self.indicator = neopixel.NeoPixel(pin, 1)
        self.message = message
        self.red = 0
        self.green = 0
        self.blue = 0
        self.period = period

    async def tasks(self):
        await asyncio.gather(asyncio.create_task(self._refresher()), 
                             asyncio.create_task(self._alive()),
                             asyncio.create_task(self._info()))
    async def _info(self):
        while True:
            print(self.message.msg)
            await asyncio.sleep(5*self.period)

    async def _alive(self):
        while True:
            self.blue = 1
            await asyncio.sleep(self.period)
            self.blue = 0
            await asyncio.sleep(self.period)

    async def _refresher(self):
        while True:
            self.indicator.fill((self.red, self.green, self.blue))
            await asyncio.sleep(self.period)

class BrakeCore():
    def __init__(self, layout) -> None:

        # matches each pin with corresponding
        # board attribute
        def create_layout(d):
            tmp = {}
            for k,v in d.items():
                tmp[k] = getattr(board, v)
            return tmp

        lt = create_layout(layout)

        self.message = Message()
        self.debug = DebuggingIndicator(board.NEOPIXEL, self.message)
        self.battery = BatteryMonitor(board.I2C(), self.message)

        self.ios = IOs(
            lt['ready'],
            lt['enable'],
            self.message)

        self.display = Display(
            lt['display_di'], 
            lt['display_dcki'], 
            self.message)

        self.brake = BrakeControl(
            lt['servo'],
            lt['power'],
            lt['remote'],
            lt['handlebars'],
            self.message)

    def start(self):
        async def main():
            await asyncio.gather(
                self.display.tasks(),
                self.battery.tasks(),
                self.debug.tasks(),
                self.brake.tasks(),
                self.ios.task()
            )
        print("run program")
        asyncio.run(main())

class Message():
    def __init__(self):
        self.config = {
            'charge_range' : (0x00ff, 0xffff),
            'voltage_range' : (6.2, 8.5),
            'servo_default' : 105,
            'user_braking' : [(85, 2), (60, 4), (90, 15)],
            'assistant_braking' : [(65, 2), (90, 2)]
        }

        self.msg = {
            'angle' : self.config['servo_default'],
            'charge' : 0,
            'current' : 0,
            'status' : 0,
            'percentage' : 0,
            'alarm': None,
            'charging' : None,
            'bms_reset' : False
        }
    @property
    def default(self) -> list:
        return self.config['servo_default']

    @property
    def assistant(self) -> list:
        return self.config['assistant_braking']

    @property
    def user(self) -> list:
        return self.config['user_braking']

    @property
    def charge_range(self) -> tuple:
        return self.config['change_range']

    @property
    def voltage_range(self) -> tuple:
        return self.config['voltage_range']

    @property
    def percentage(self) -> float:
        return self.msg['percentage']

    @property
    def status(self) -> int:
        return self.msg['status']

    @status.setter
    def status(self, value: int) -> None:
        self.msg['status'] = value

    @property
    def angle(self) -> float:
        return self.msg['angle']

    @angle.setter
    def angle(self, value: float) -> None:
        self.msg['angle'] = value

    @property
    def alarm(self) -> bool:
        return self.msg['alarm']

    @alarm.setter
    def alarm(self, value: bool) -> None:
        self.msg['alarm'] = value

    @property
    def charging(self) -> bool:
        return self.msg['charging']

    @charging.setter
    def charging(self, value: bool) -> None:
        self.msg['charging'] = value

    @property
    def charge(self) -> int:
        return self.msg['charge']

    @property
    def percentage(self) -> float:
        return self.msg['percentage']

    @charge.setter
    def charge(self, value: int) -> None:
        low, high = self.config['charge_range']
        self.msg['charge'] = value
        self.msg['percentage'] = (value - low)/(high - low)

    @property
    def reset(self) -> bool:
        return self.msg['bms_reset']

    @reset.setter
    def reset(self, value: bool) -> None:
        self.msg['bms_reset'] = value

    @property
    def current(self) -> float:
        return self.msg['current']

    @current.setter
    def current(self, value: float) -> None:
        self.msg['current'] = value

class IOs():
    def __init__(self, rdy, ena, message: Message) -> None:
        self.period = 0.2
        self.message = message

        self.enable = DigitalInOut(ena)
        self.enable.direction = Direction.INPUT
        self.ready = DigitalInOut(rdy) 
        self.ready.direction = Direction.OUTPUT

    async def task(self):
        await asyncio.create_task(self.start())

    async def start(self):
        while True:
            if self.enable.value:
                if self.message.charging is None:
                    self.ready.direction = Direction.INPUT
                self.message.charging = not self.ready.value
            else:
                if self.message.charging is not None:
                    self.message.charging = None
                    self.ready.direction = Direction.OUTPUT
                self.ready.value = False
            await asyncio.sleep(self.period)

class BatteryMonitor():

    def __init__(self, i2c, message: Message) -> None:
        self.drv = LTC2943(i2c_bus=i2c, res=10e-3)

        self.drv.adc_mode = Mode.AUTOMATIC
        self.drv.prescaler = Prescaler.PRES_M64
        self.drv.alcc = ALCC.DISABLE
        self.message = message
        self.period = 0.2

        # set limits
        self.drv.voltage_range = (7.0, 8.5)
        self.drv.charge_range = (0x00ff, 0xffff)

    async def tasks(self):
        await asyncio.gather(
            asyncio.create_task(self.refresher())
        )

    async def refresher(self): 
        while True:
            self.message.status = self.drv.status
            self.message.current = self.drv.current
            self.message.charge = self.drv.accumulated_charge

            # NOTE the chinese module doesn't stop 
            # always at the 0xffff value so we have 
            # to limit the value manually.
            if ((self.message.status & 0x20) or self.message.reset)\
                and self.message.charging is not None:
                if not self.message.charging:
                    self.message.reset = False
                self.message.charge = 0xffff
                self.drv.accumulated_charge = self.message.charge

            # NOTE this means the cable is plugged 
            # and either it is charging or it is 
            # waiting to be disconnected from the 
            # charger
            self.message.alarm = False
            if self.message.charging is None:
                if (self.message.status & 0x06):
                    self.message.alarm = True

            await asyncio.sleep(self.period)

class Display:
    def __init__(self, di, dcki, message: Message):
        self.drv = MY9221(di, dcki)
        # self.drv = MY9221_dummy()

        self.width = self.drv.WIDTH
        self.message = message
        self.level = 0
        self.nlevel = 0
        self.boot = True 
        self.active = 'welcome'
        self.next = 'welcome'

        self.animations = {
            'alarm': self.alarm,
            'reset': self.reset,
            'charging': self.charging,
            'indicator': self.indicator,
            'welcome': self.welcome
        }

    def tasks(self):
        await asyncio.gather(
            asyncio.create_task(self.selector()),
            asyncio.create_task(self.refresher())
        )

    async def selector(self):
        while True:
            self.level = int(self.message.percentage*self.width + 0.5)
            self.nlevel = self.width - self.level

            if not self.boot:
                if self.message.reset:
                    self.next = 'reset'
                elif self.message.alarm:
                    self.next = 'alarm'
                elif self.message.charging:
                    self.next = 'charging'
                else:
                    self.next = 'indicator'
            await asyncio.sleep(0.2)

    async def refresher(self, period=0.2):
        anim = self.animations['welcome']()
        while True:
            try:
                if (self.active != self.next):
                    anim = self.animations[self.next]()
                    self.active = self.next
                self.drv.register = next(anim)
            except Exception:
                self.boot = False
                anim = self.animations[self.active]()
            await asyncio.sleep(period)

    def welcome(self, intensity=100):
        yield [0] * self.width
        for i in range(0, 5):
            yield [(4-i, intensity), (5+i, intensity)]

    def indicator(self, intensity=100):
        yield [intensity]*self.level + [0]*(self.width - self.level)

    def reset(self, intensity=100):
        yield [intensity] * self.width
        yield [0] * self.width

    def alarm(self, intensity=100):
        for i in range(10):
            yield [int(255/10*i-0.5)] * self.width

    def charging(self, intensity=100):
        yield [intensity]*self.level + [0]*self.nlevel
        for i in range(self.level, self.width):
            yield (i, intensity)

class MY9221_dummy:

    WIDTH = 10 # Number of LEDs

    def __init__(self):
        self.leds = [" "]*self.WIDTH 
        self.set_all(0)

    @property
    def register(self):
        return self._register

    @register.setter
    def register(self, config):
        if isinstance(config, tuple):
            id, intensity = config
            self._register[id] = intensity
        elif all(isinstance(item, tuple) for item in config):
            for id, intensity in config:
                self._register[id] = intensity
        elif isinstance(config, list):
            for index, intensity in enumerate(config):
                self._register[index] = intensity 
        else:
            raise ValueError("Value has to be tuple, list or list of tuples")
        self.refresh()

    def set_all(self, value):
        self._register = [value] * self.WIDTH  
        self.refresh()

    def refresh(self):
        for k,v in enumerate(self._register):
            self.leds[k] = "#" if v > 0 else " "
        print(f'|{''.join(self.leds)}|' + ' '*30 + '\r', end=" ")

class BrakeControl():
    def __init__(self, srv, pwr, remote, handlebars, message: Message) -> None:
        self.keys = keypad.Keys((remote, handlebars), 
                                value_when_pressed=True, 
                                pull=False)

        self.servo = servo.Servo(
            pwmio.PWMOut(srv, duty_cycle=2 ** 15, frequency=50)
        )

        self.power = DigitalInOut(pwr)
        self.power.direction = Direction.OUTPUT 
        self.message = message
        self.active_keys = [False, False]
        self.both = False

    def tasks(self):
        await asyncio.gather(
            asyncio.create_task(self.key_menu()),
            asyncio.create_task(self.driver())
        )

    async def driver(self):
        while True:
            if self.message.charging is None and not self.message.alarm:
                self.power.value = True
                self.servo.angle = self.message.angle
            else:
                self.servo.angle = self.message.default
                self.power.value = False
            await asyncio.sleep(0.1)

    async def braking_gradientally(self):
        try:
            for l in self.message.user:
                self.message.angle, period = l
                print(f"braking angle: {self.message.angle}")
                await asyncio.sleep(period)

            # wait until the task is deactivated
            while True:
                await asyncio.sleep(0.2)

        except asyncio.CancelledError:
            print(f"gradient braking stopped")
            self.message.angle = self.message.default

    async def braking_until_still(self):
        try:
            for l in self.message.assistant:
                self.message.angle, period = l
                print(f"braking angle: {self.message.angle}")
                await asyncio.sleep(period)

            print(f"braking until still stopped")
            self.message.angle = self.message.default

        except asyncio.CancelledError:
            print(f"gradient braking stopped")
            self.message.angle = self.message.default

    async def reset_timeout(self):
        # NOTE if the reset is already 
        # active, there nothing to do
        if self.message.reset:
            self.message.reset = False
            return

        # NOTE wait for 5s and check, if 
        # the both keys are still pressed
        for i in range(25):
            await asyncio.sleep(0.2)
            if not self.both:
                return

        self.message.reset = True
        print(f"reset timeout success")

    async def key_menu(self):

        async def dummy_task():
            await asyncio.sleep(0)

        user = asyncio.create_task(dummy_task())
        assistant = asyncio.create_task(dummy_task())
        bms_reset = asyncio.create_task(dummy_task())

        while True:
            self.event = self.keys.events.get()
            if self.event:
                if self.event.pressed:
                    self.active_keys[self.event.key_number] = True
                    print("pressed button")

                    if self.active_keys[0] and self.active_keys[1]:
                        self.both = True
                        if bms_reset.done():
                            user.cancel()
                            assistant.cancel()
                            bms_reset = asyncio.create_task(
                                self.reset_timeout())

                    elif self.active_keys[0]:
                        if assistant.done(): 
                            user.cancel() # it cancels the user
                            assistant = asyncio.create_task(
                                self.braking_until_still())
                    else:
                        if assistant.done():
                            user = asyncio.create_task(
                                self.braking_gradientally())
                    
                elif self.event.released:
                    print("released button")
                    bms_reset.cancel() # cancels the reset timeout
                    user.cancel() # it cancels the user's brake
                    self.active_keys[self.event.key_number] = False
            await asyncio.sleep(0.1)
