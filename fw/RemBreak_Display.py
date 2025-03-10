
# SPDX-License-Identifier: MIT

import asyncio

from CircuitPython_MY9221 import MY9221

class Display:

    # MODES
    STATUS = 0
    BLINK_ALL = 1
    PONG = 2
    CHARGE = 3

    def __init__(self, driver):
        self._driver = driver
        self._width = self._driver.WIDTH
        self.mode = [self.STATUS, -1]

        # Control Flags
        self.percentage = 0
        self.busy = None

    async def start(self):
        self.busy = asyncio.create_task(self.welcome())

        while not self.busy.done():
            await asyncio.sleep(0.1)

        while True:
            if self.mode[0] != self.mode[1]:
                self.mode[1] = self.mode[0]
                self.busy.cancel()

                if self.mode[0] == self.BLINK_ALL: 
                    self.busy = asyncio.create_task(self.blink_all())
                elif self.mode[0] == self.PONG: 
                    self.busy = asyncio.create_task(self.pong())
                elif self.mode[0] == self.CHARGE: 
                    self.busy = asyncio.create_task(self.charge())
                else:
                    self.busy = asyncio.create_task(self.status())

            await asyncio.sleep(1)

    async def welcome(self):

        for i in range(0, 5):
            self._driver.register = [(4-i, 100), (5+i, 100)]
            await asyncio.sleep(0.1)
        self._driver.set_all(0)

    async def blink_all(self):
        while True:
            self._driver.register = [100] * self._width
            await asyncio.sleep(0.4)
            self._driver.register = [0] * self._width
            await asyncio.sleep(0.4)

    async def snake(self):
        while True:
            buf = [100]*3 + [0]*7
            for i in range(100):
                print(buf)
                self._driver.register = buf
                h = buf.pop(0)
                buf.append(h)
                await asyncio.sleep(0.1)

    async def pong(self):
        while True:
            buf = [100]*3 + [0]*7
            for i in range(7):
                z = buf.pop(9)
                buf.insert(0, z)
                self._driver.register = buf
                await asyncio.sleep(0.1)
            for i in range(7):
                z = buf.pop(0)
                buf.insert(9, z)
                self._driver.register = buf
                await asyncio.sleep(0.1)

    async def charge(self):
        while True:
            await asyncio.sleep(0.2)
            num = int(self.percentage*self._width)
            buf = [100]*num + [0]*(10-num)
            for i in range(10-num+1, 10):
                buf[i] = 100
                self._driver.register = buf 
                await asyncio.sleep(0.2)

    # SHOW THE BATTERY STATUS
    async def status(self):
        while True:
            num = int(self.percentage*self._width)
            print(num)
            s = [100] * num + [0] * (9-num)
            self._driver.register = s
            await asyncio.sleep(2)

