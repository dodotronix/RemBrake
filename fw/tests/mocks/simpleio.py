
import board

class DigitalOut:
    def __init__(self, pin: board.Pin):
        self.pin = pin
        self.value = None

    def __repr__(self):
        return f"[DigitalOut: {self.pin}, <Value: {self.value}>]"

    @property
    def value(self):
        return self.value

    @value.setter
    def value(self, v):
        self.value = v

