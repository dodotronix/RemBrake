
class NeoPixel:
    def __init__(self, pin, size):
        self.pin = pin
        self.size = size
        self.red = 0
        self.green = 0
        self.blue = 0

    def fill(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
