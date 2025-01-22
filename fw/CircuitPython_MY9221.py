
# library for MY9221
from digitalio import DigitalInOut, Direction

class MY9221():
    def __init__(self, di, dcki, LedNum=10, intensity=255) -> None:
        self._di = DigitalInOut(di)
        self._di.direction = Direction.OUTPUT
        self._dcki = DigitalInOut(dcki)
        self._dcki.direction = Direction.OUTPUT

        self._bits = 0x00
        self._led_num = LedNum
        self._intensity = intensity

    def _my9221_write16(self, data):
        for i in range(15, -1, -1):
            self._di.value = (data >> i) & 1
            state = self._dcki.value
            self._dcki.value = not state

    def _my9221_msg(func):
        def message(self, *args, **kwargs):
            # BEGIN
            self._my9221_write16(0)
            func(self, *args, **kwargs)
            # END
            self._my9221_write16(0)
            self._my9221_write16(0)
            # LATCH
            self._di.value = False
            for i in range(4):
                self._di.value = False
                self._di.value = True
        return message 

    @_my9221_msg
    def _refresh_display(self):
        for i in range(0, self._led_num):
            word = self._intensity if (self._bits >> i) & 1 else 0
            self._my9221_write16(word)

    @property
    def bits(self):
        """Internal register to track, which LEDs are ON"""
        return self._bits

    @bits.setter
    def bits(self, value):
        self._bits = 0x3ff & value
        self._refresh_display()

    @property
    def intensity(self):
        """Changes the brightness of the LEDs"""
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        self._intensity = 0xff & value
        self._refresh_display()

    def get_number_of_segments(self):
        return self._led_num


