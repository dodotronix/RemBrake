
# library for MY9221

from simpleio import DigitalOut

class MY9221():

    WIDTH = 10 # Number of LEDs

    def __init__(self, di, dcki) -> None:

        self._di = DigitalOut(di)
        self._dcki = DigitalOut(dcki)
        self.set_all(0)

    @property
    def data(self):
        return self._di.value

    @data.setter
    def data(self, value):
        self._di.value = value

    @property
    def clock(self):
        return self._dcki.value

    @clock.setter
    def clock(self, value):
        self._dcki.value = value

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
        # CREATE MESSAGE
        words = [0] + self._register + [0, 0] 

        def shift_out(word):
            """ This copies the bits into the shift register"""
            for w in f"{word:016b}":
                self.data = int(w, 2)
                self.clock = not self.clock

        for w in words:
            shift_out(w)

        # LATCH
        self.data = False
        for i in range(4):
            self.data = not self.data
