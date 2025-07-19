import board
import pwmio
import neopixel

from time import sleep
from adafruit_motor import servo
from digitalio import DigitalInOut, Direction


try:
    import adafruit_logging as lg
except:
    import logging as lg

log = lg.getLogger(__name__)
log.setLevel(lg.INFO)

class CurrentLimiter():
    def __init__(self, layout) -> None:

        # matches pins with board attributes
        def create_layout(d):
            tmp = {}
            for k,v in d.items():
                tmp[k] = getattr(board, v)
            return tmp

        lt = create_layout(layout)

        self.indicator = neopixel.NeoPixel(board.NEOPIXEL, 1)

        self.power = DigitalInOut(lt["power"])
        self.power.direction = Direction.OUTPUT 

        self.button = DigitalInOut(lt["handlebars"])
        self.button.direction = Direction.INPUT 

        self._pwm = pwmio.PWMOut(
            lt["servo"], duty_cycle=2**15, frequency=50) 
        self._servo = servo.Servo(self._pwm)
        self._servo.angle = 100
        self.power.value = True

    def run(self):
        while True:
            self.indicator.fill((0, 80, 0))
            self._servo.angle = 100
            while not self.button.value:
                pass

            self.indicator.fill((80, 80, 0))
            self._servo.angle = 15
            while self.button.value:
                pass

