
import sys

import logging as lg

NEOPIXEL = 0

_pins = ["D0", "D1",  "D2", "D3", "TX", "MOSI", "MISO", "SCK", "RX"]

class Pin:
    def __init__(self, name):
        lg.info(f"MOCK initializing pin {name}")
        self.name = name

    def __repr__(self):
        return f"<MOCK_PIN {self.name}>"

class I2C:
    def __init__(self):
        lg.info(f"MOCK initializing I2C")

# generate pin attributes of the board module
module = sys.modules[__name__]
for name in _pins:
    setattr(module, name, Pin(name)) 
