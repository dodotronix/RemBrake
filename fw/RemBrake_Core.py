# SPDX-License-Identifier: MIT

import asyncio
import keypad
import neopixel
import board
import pwmio

from adafruit_motor import servo
from digitalio import DigitalInOut, Direction

from CircuitPython_MY9221 import MY9221
from CircuitPython_LTC2943 import LTC2943, ALCC, Mode, Prescaler
from RemBrake_WaveKit import Composer

try:
    import adafruit_logging as lg
except:
    import logging as lg

log = lg.getLogger(__name__)
log.setLevel(lg.INFO)

class Message():
    def __init__(self):
        self.config = {
            'charge_range' : (0x00ff, 0xffff),
            'voltage_range' : (6.2, 8.5),
            'servo_default' : 100,
            'led_intensity' : 100,
            'user_braking' : [(130, 2), (150, 4), (130, 30)],
            'assistant_braking' : [(150, 5), (135, 10)]
        }

        self.sounds = { "welcome"  : [("C5", 0.15),
                                      ("E5", 0.15),
                                      ("G5", 0.15),
                                      ("C6", 0.15),],

                       "plugged"   : [("E5", 0.12),
                                      ("G5", 0.2),
                                      ("-", 0.2)],

                       "unplugged" : [("G5", 0.2),
                                      ("E5", 0.12),
                                      ("-", 0.2)],

                       "charged" : [("C5", 0.12),
                                    ("E5", 0.12),
                                    ("G5", 0.12),
                                    ("C6", 0.3),],

                       "reset" : [("C5", 0.08),
                                  ("D5", 0.08),
                                  ("E5", 0.08),
                                  ("G5", 0.08),
                                  ("C6", 0.08),
                                  ("-", 0.04)],

                       "alarm" : [("H6", 0.15),
                                  ("-", 0.1),
                                  ("H6", 0.15)]}

        self.msg = {
            'angle': self.config['servo_default'],
            'charge': 0,
            'current': 0,
            'kalman': 0,
            'pid_angle': 0,
            'status': 0,
            'percentage': 0,
            'alarm': False
        }

        # kalman init
        self.P = 0
        self.r = 100
        self.q = 0.1

    @property
    def light(self) -> bool:
        return self.config['led_intensity']

    @property
    def default(self) -> list:
        return self.config['servo_default']

    @property
    def charge_range(self) -> tuple:
        return self.config['charge_range']

    @property
    def voltage_range(self) -> tuple:
        return self.config['voltage_range']

    @property
    def user(self) -> int:
        return self.config['user_braking']

    @property
    def assistant(self) -> int:
        return self.config['assistant_braking']
    
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
    def charge(self) -> int:
        return self.msg['charge']

    @property
    def percentage(self) -> float:
        return self.msg['percentage']

    @charge.setter
    def charge(self, value: int) -> None:
        low, high = self.config['charge_range']
        self.msg['charge'] = value

        # limit the value to range <0, 1>
        normalized = (value - low)/(high - low)
        self.msg['percentage'] = max(0, min(1, normalized))

    @property
    def current(self) -> float:
        return self.msg['current']

    @current.setter
    def current(self, value: float) -> None:
        self.msg['current'] = value

        # kalman filter
        P_pred = self.P + self.q
        K = P_pred/(P_pred + self.r)
        self.msg['kalman'] += K*(value - self.msg['kalman'])
        self.P = (1 - K)*P_pred

    @property
    def pid(self) -> float:
        return self.msg['pid_angle']

    @pid.setter
    def pid(self, value) -> None:
        self.msg['pid_angle'] = value

    @property
    def kalman(self) -> float:
        return self.msg['kalman']

class DebuggingIndicator():
    def __init__(self, pin, message: Message, period=0.2):
        self._indicator = neopixel.NeoPixel(pin, 1)
        self.message = message
        self.period = period
        self._instance0 = None
        self._instance1 = None

    def run(self):
        if not self._instance0:
            self._instance0 = asyncio.create_task(self._alive())
        if not self._instance1:
            self._instance1 = asyncio.create_task(self._info())

    async def _info_current(self):
        while True:
            print(f"{self.message.kalman}, {self.message.current}, {self.message.pid}")
            await asyncio.sleep(5*self.period)

    async def _info(self):
        t = 5*self.period # 1s
        while True:
            string = "MESSAGE -> ["
            for k,v in self.message.msg.items():
                string = f"{string}{k}:{v}, "
            log.info(f"{string[:-2]}]")
            await asyncio.sleep(t)

    async def _alive(self):
        while True:
            self._indicator.fill((0, 0, 10))
            await asyncio.sleep(self.period)
            self._indicator.fill((0, 0, 0))
            await asyncio.sleep(self.period)

class BrakeCore():
    def __init__(self, layout) -> None:

        # matches pins with board attributes
        def create_layout(d):
            tmp = {}
            for k,v in d.items():
                tmp[k] = getattr(board, v)
            return tmp

        lt = create_layout(layout)

        # main FSM states
        self._waiting = None
        self.state = None
        self.next_state = "boot"

        self.state_handlers = {
            "boot" : self.boot,
            "running": self.running, 
            "user" : self.user,
            "assistant" : self.assistant,
            "plugged" : self.plugged,
            "charging": self.charging,
            "idle" : self.idle,
            "unplugged" : self.unplugged,
            "reset": self.reset,
            "alarm": self.alarm}

        self.msg = Message()
        self.ready = DigitalInOut(lt['ready']) 
        self.debug = DebuggingIndicator(
            board.NEOPIXEL, self.msg)

        # TODO can initial states of keys
        keys = (lt['enable'],
                lt['handlebars'], 
                lt['remote'])

        # find initial states of the pins before 
        # switching to the boot state
        self.hold = 0
        for n,k in enumerate(keys):
            pin = DigitalInOut(k)
            pin.direction = Direction.INPUT
            self.hold |= (pin.value << n)
            pin.deinit()

        self.keys = keypad.Keys(keys, 
                                value_when_pressed=True, 
                                pull=False)

        self.brake = BrakeControl(
            lt['servo'],
            lt['power'],
            self.msg)

        self.battery = BatteryMonitor(
            board.I2C(), self.msg)

        self.player = Composer(lt['buzz'])

        self.display = Display(
            lt['display_di'], 
            lt['display_dcki'],
            self.msg)
        
        self.transitions = {"boot"      : {0 : "running",
                                           1 : "plugged"},
                            "running"   : {1 : "plugged",
                                           2 : "user",
                                           4 : "assistant"},
                            "plugged"   : {0 : "unplugged"},
                            "charging"  : {0 : "unplugged"},
                            "idle"      : {0 : "unplugged",
                                           7 : "reset"},
                            "unplugged" : {0 : "running",
                                           1 : "plugged"},
                            "assistant" : {0 : "running",
                                           2 : "user",
                                           5 : "plugged",
                                           7 : "plugged"},
                            "user"      : {0 : "running", 
                                           3 : "plugged",
                                           6 : "assistant"},
                            "reset"     : {0 : "running", 
                                           3 : "idle",
                                           5 : "idle"},
                            "alarm"     : {1 : "plugged"}}

    def run(self):
        log.info("launching main program")
        asyncio.run(self.main())

    async def main(self):
        while(True):
            if self.next_state:
                try :
                    handler = self.state_handlers[self.next_state]
                except:
                    handler = self.state_handlers["boot"]
                    self.next_state = "boot"
                if self.state != self.next_state:
                    log.info(f"State: {self.next_state}")
                    self.state = self.next_state
                self.next_state = await handler()

            # NOTE the key changes will never happen 
            # concurently due to the readout from 
            # queue of events, this reduces number 
            # of posibilities in state transitions
            # in the Finite State Machine (FSM)
            e = self.keys.events.get()
            if e:
                if e.pressed:
                    self.hold |= (1 << e.key_number)
                elif e.released:
                    self.hold &= ~(1 << e.key_number)
                self.next_state = \
                self.transitions[self.state].get(
                    self.hold, self.next_state)

            # check for alarm in running state
            if self.msg.alarm and not (self.hold & 0x01):
                self.next_state = "alarm"

            await asyncio.sleep(0.001)

    async def boot(self):
        sound = self.player(self.msg.sounds["welcome"])
        animation = self.display("welcome")
        await asyncio.gather(sound(), animation())

        self.debug.run()
        self.battery.run()
        self.brake.run()
        return self.transitions["boot"][self.hold]

    async def running(self):
        self.brake.handler.try_cancel("user")
        if self.ready.direction != Direction.OUTPUT:
            self.ready.direction = Direction.OUTPUT
            self.ready.value = True # system running 

        animation = self.display("indicator")
        await animation()
        return "running" 

    async def user(self):
        self.brake.handler.try_run("user")
        return None

    async def assistant(self):
        self.brake.handler.force_run("assistant")
        return None

    async def plugged(self):
        self.brake.deactivate()
        if self.ready.direction != Direction.INPUT:
            self.ready.direction = Direction.INPUT

        sound = self.player(self.msg.sounds["plugged"])
        await asyncio.gather(sound())
        return "charging"

    async def charging(self):
        if not self.ready.value:
            animation = self.display("charging")
            await animation()
            return "charging"
        else:
            sound = self.player(self.msg.sounds["charged"])
            animation = self.display("indicator")
            await asyncio.gather(sound(), animation())
            return "idle"

    async def idle(self):
        if self._waiting:
            self._waiting.cancel()

        animation = self.display("indicator")
        await animation()
        return "idle"

    async def unplugged(self):
        self.brake.run()
        sound = self.player(self.msg.sounds["unplugged"])
        await asyncio.gather(sound())
        return "running"

    async def reset(self):
        # NOTE you won't leave this state until you release 
        # one button, switching the on/off switch won't work 
        # until you release both buttons.
        async def timeout(t):
            try:
                await asyncio.sleep(t)
                log.info(f"Timeout counter finished")

                self.battery.reset()
                sound = self.player(self.msg.sounds["reset"])
                animation = self.display("reset")
                await asyncio.gather(sound(), animation())
                self.next_state = "idle"

            except asyncio.CancelledError:
                log.info(f"Timeout counter canceled")

        self._waiting = asyncio.create_task(timeout(2))

        # this has to return None otherwise the _waiting 
        # instance timeout is going to be overwritten
        # in the next call of the handle reset
        return None

    async def alarm(self):
        self.brake.deactivate()

        sound = self.player(self.msg.sounds["alarm"])
        if self.msg.status == 0x04:
            animation = self.display("low_battery")
        else:
            animation = self.display("alarm")
        await asyncio.gather(sound(), animation())
        return "alarm"

class AsyncHandler():
    def __init__(self, functions):
        self._function_dict = functions
        self._instance = None
        self._name = None

    def __call__(self, name):
        self._name = name
        log.info(f"Launching instance: {self._name}")
        self._instance = asyncio.create_task(
            self._function_dict[name]())

    def try_run(self, name):
        if self.done():
            self.__call__(name)

    def try_cancel(self, name):
        if name == self._name:
            self.cancel()

    def force_run(self, name):
        if (name != self._name):
            self.cancel()
        elif not self.done():
            return
        self.__call__(name)

    def cancel(self):
        if self._instance and not self._instance.done():
            log.info(f"Cancelling instance: {self._name}")
            self._instance.cancel()

    def done(self):
        if self._instance:
            return self._instance.done()
        else:
            return 1

class Display:

    def __init__(self, di, dcki, message: Message):
        self.ledbar = MY9221(di, dcki)

        self.msg = message
        self.animations = {"welcome" : self.welcome,
                           "charging" : self.charging,
                           "indicator" : self.indicator,
                           "low_battery": self.low_battery,
                           "reset" : self.reset,
                           "alarm" : self.alarm}

    def __call__(self, name):
        return self.animations.get(name, self.indicator)

    def ledbar_level(self):
        if self.msg.percentage:
            tmp = min(self.msg.percentage + 1/len(self.ledbar), 1)
            return int(tmp*len(self.ledbar))
        return 0

    async def welcome(self):
        self.ledbar(0)
        for i in range(5):
            self.ledbar[i] = self.msg.light
            self.ledbar[9-i] = self.msg.light
            self.ledbar.refresh()
            await asyncio.sleep(0.15)
    
    async def charging(self):
        tmp = self.ledbar_level()
        self.ledbar(0)
        for i in range(tmp):
            self.ledbar[i] = self.msg.light
            self.ledbar.refresh()
            await asyncio.sleep(0.1)

    async def low_battery(self):
        self.ledbar(0)
        await asyncio.sleep(0.08)
        self.ledbar[0] = self.msg.light
        self.ledbar.refresh()
        await asyncio.sleep(0.08)

    async def indicator(self):
        tmp = self.ledbar_level()
        self.ledbar([self.msg.light]*tmp)

    async def reset(self):
        for _ in range(3):
            self.ledbar(0)
            await asyncio.sleep(0.15)
            self.ledbar(self.msg.light)
            await asyncio.sleep(0.15)

    async def alarm(self):
        self.ledbar(0)
        await asyncio.sleep(0.3)

        self.ledbar(self.msg.light)
        await asyncio.sleep(0.08)

        self.ledbar(0)
        await asyncio.sleep(0.08)

        self.ledbar(self.msg.light)
        await asyncio.sleep(0.08)

class BatteryMonitor():

    def __init__(self, i2c, message: Message) -> None:
        self.drv = LTC2943(i2c_bus=i2c, res=10e-3)
        self._instance = None

        self.drv.adc_mode = Mode.AUTOMATIC
        self.drv.prescaler = Prescaler.PRES_M64
        self.drv.alcc = ALCC.DISABLE
        self.msg = message

        # set limits
        self.drv.voltage_range = message.voltage_range
        self.drv.charge_range = message.charge_range

    def reset(self):
        self.msg.charge = 0xffff
        self.drv.accumulated_charge = self.msg.charge

    def run(self):
        async def driver(): 
            try:
                while True:
                    self.msg.status = self.drv.status
                    self.msg.current = self.drv.current
                    self.msg.charge = self.drv.accumulated_charge

                    # Here we set alarm flag when
                    # the BMS detects undervoltage
                    if (self.msg.status & 0x06):
                        self.msg.alarm = True
                    elif not (self.msg.status & 0x06) and self.msg.alarm:
                        self.msg.alarm = False

                    # NOTE the chinese module does 
                    # not stop always at the 0xffff 
                    # value so we have to limit the 
                    # value manually.
                    if (self.msg.status & 0x20):
                        self.reset()

                    await asyncio.sleep(0.2)

            except asyncio.CancelledError:
                log.info(f"Stopping battery monitor")

        if not self._instance or self._instance.done():
            self._instance = asyncio.create_task(driver())

    def cancel(self):
        if self._instance:
            self._instance.cancel()

class BrakeControl():
    def __init__(self, srv, pwr, message: Message) -> None:

        self.power = DigitalInOut(pwr)
        self.power.direction = Direction.OUTPUT 

        self.msg = message
        self.handler = AsyncHandler({
            "user" : self.user_braking,
            "assistant" : self.assistant_braking})

        self._instance = None
        self._angle = self.msg.default
        self._pwm = pwmio.PWMOut(srv, duty_cycle=2**15, frequency=50) 
        self._servo = servo.Servo(self._pwm)

    # TODO don't create this as a standalone 
    # create, put it in the main loop, because
    # cancellation takes too long
    def run(self):
        async def driver():
            try:
                # enable servo power
                self.power.value = True
                last_angle = 0
                while True:
                    # TODO PID regulator
                    if last_angle != self._angle:
                        self._servo.angle = self._angle
                        last_angle = self._angle
                    await asyncio.sleep(0.001)
            except asyncio.CancelledError:
                log.info(f"Stopping servo driver")
                self._angle = self.msg.default
                self.power.value = False

        if not self._instance or self._instance.done():
            self._instance = asyncio.create_task(driver())

    def deactivate(self):
        self.handler.cancel()
        if not self.done():
            self._instance.cancel()

    def done(self):
        if self._instance:
            return self._instance.done()
        return 0

    async def braking_sequence(self, sequence, infinite=False):
        try:
            for l in sequence:
                self._angle, period = l
                log.info(f"braking angle: {self._angle}")
                await asyncio.sleep(period)

            # wait until the task is deactivated
            while infinite:
                await asyncio.sleep(0.2)

            log.info("braking sequence finished")
            self._angle = self.msg.default

        except asyncio.CancelledError:
            log.info(f"Stopping braking sequence")
            self._angle = self.msg.default

    def user_braking(self):
        return self.braking_sequence(self.msg.user, True)

    def assistant_braking(self):
        return self.braking_sequence(self.msg.assistant)
