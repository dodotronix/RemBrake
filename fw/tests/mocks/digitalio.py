import board

import logging as lg

class Direction:
    OUTPUT = 0
    INPUT = 1

class DigitalInOut:
    def __init__(self, pin: board.Pin):
        self.pin = pin
        self._direction = 0
        self._value = 0

    @property
    def direction(self):
        lg.info(f"direction of {self.pin} is {self._direction}")
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = "OUTPUT"
        if value == Direction.INPUT:
            self._direction = "INPUT"
        lg.info(f"Direction of {self.pin} set to {self._direction}")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        assert self._direction == "INPUT"
        lg.info(f"Value of {self.pin} set to {value}")
        self._value = value

