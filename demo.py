#!/usr/bin/python

import os
os.environ['BLINKA_FT232H'] = "1"

import board
import digitalio

from pyftdi.ftdi import Ftdi
from time import sleep

print(dir(board))

led = digitalio.DigitalInOut(board.C0)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    sleep(0.5)
    led.value = False
    sleep(0.5)
