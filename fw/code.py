import board
import digitalio
import neopixel
import pwmio
import simpleio

from time import sleep
from adafruit_motor import servo

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

rembut = digitalio.DigitalInOut(board.D0)
rembut.direction = digitalio.Direction.INPUT

handbut = digitalio.DigitalInOut(board.D1)
handbut.direction = digitalio.Direction.INPUT

simpleio.tone(board.D2, 440, duration=2.0)

pwm = pwmio.PWMOut(board.D3, duty_cycle=2 ** 15, frequency=50)
my_servo = servo.Servo(pwm)

while True:
    if rembut.value:
        pixel.fill((0, 255, 0))
        a = 105
    elif not handbut.value:
        pixel.fill((0, 0, 255))
        a = 105
    else:
        a = 62
        pixel.fill((255, 0, 255))
    my_servo.angle = a
    sleep(0.01)

