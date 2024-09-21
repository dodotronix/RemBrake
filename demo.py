#!/usr/bin/python

import os
os.environ['BLINKA_FT232H'] = "1"

import board
import digitalio

from time import sleep

led = digitalio.DigitalInOut(board.C0)
led.direction = digitalio.Direction.OUTPUT

from_remote = digitalio.DigitalInOut(board.D7)
from_remote.direction = digitalio.Direction.INPUT

if __name__ == '__main__':

    while True:
        last_value = from_remote.value
        if (from_remote.value == True) and (last_value == False):
            led.value = not led.value
            print("clicked")

