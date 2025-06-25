
# SPDX-License-Identifier: MIT

import board
import logging as lg

logger = lg.getLogger(__name__)
logger.setLevel(lg.INFO)

class MY9221:

    _WIDTH = 10 # Number of LEDs
    # NOTE LED intensity range is <0, 255>
    SIMUL = False

    def __init__(self, di: board.Pin, dcki: board.Pin, simulation=False) -> None:
        self.di = di
        self.dcki = dcki
        self.leds = [" "]*self._WIDTH 
        self._register = [0] * self._WIDTH  
        self._mask = 2**self._WIDTH - 1
        self._simulation = simulation

        # clear all leds
        self.refresh()

    def __call__(self, config):
        if isinstance(config, int):
            for i in range(self._WIDTH):
                if self._mask & (0x01 << i):
                    self._register[i] = config
        elif isinstance(config, tuple):
            idx, intensity = config
            self._register[idx] = intensity
        elif all(isinstance(item, tuple) for item in config):
            for idx, intensity in config:
                self._register[idx] = intensity
        elif isinstance(config, list):
            tmp = config + [0]*(self._WIDTH - len(config))
            self._register = tmp
        else:
            raise ValueError("Value has to be tuple, list or list of tuples")
        self.refresh()

    def __len__(self):
        return self._WIDTH

    def __getitem__(self, idx):
        return self._register[idx]

    def __setitem__(self, idx, value):
        self._register[idx] = value

    def set(self, mask):
        self._mask = mask

    def get(self):
        return self._mask

    def refresh(self):
        for k,v in enumerate(self._register):
            self.leds[k] = "#" if v > 0 else " "

        if self.SIMUL:
            print(f"|{''.join(self.leds):<{self._WIDTH}}|\r", end="")
        else:
            logger.info(f"|{''.join(self.leds):<{self._WIDTH}}|")
