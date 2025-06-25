import board

import logging as lg

logger = lg.getLogger(__name__)
logger.setLevel(lg.INFO)

class Direction:
    OUTPUT = 0
    INPUT = 1

class DigitalInOut:
    def __init__(self, pin: board.Pin):
        self.pin = pin
        self._direction = 0
        self._value = 0
        self._direction_str = {0 : "OUTPUT", 1 : "INPUT"}

    @property
    def direction(self):
        logger.info(f"MOCK_INFO direction of {self.pin}"
            f" is {self._direction_str[self._direction]}")
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = Direction.OUTPUT
        if value == Direction.INPUT:
            self._direction = Direction.INPUT
            self._value = 0
        logger.info(f"MOCK_SET direction of {self.pin} to"
            f" {self._direction_str[self._direction]}")

    @property
    def value(self):
        logger.info(f"MOCK_GET {self.pin} is {self._value}")
        return self._value

    @value.setter
    def value(self, value):
        assert self._direction == Direction.OUTPUT
        self._value = value
        logger.info(f"MOCK_SET {self.pin} to {self._value}")

    # simulation purpose
    def set(self, value):
        self._value = value
        logger.info(f"SIMULATION_MOCK_SET {self.pin} to {self._value}")

    def deinit(self):
        logger.info(f"MOCK_INFO {self.pin} deinitialized")
