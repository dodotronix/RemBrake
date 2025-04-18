
# SPDX-License-Identifier: MIT

import logging as lg

import board

class MY9221:

    WIDTH = 10 # Number of LEDs

    def __init__(self, di: board.Pin, dcki: board.Pin) -> None:
        self.di = di
        self.dcki = dcki
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
