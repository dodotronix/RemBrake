#!/usr/bin/python

import board
import asyncio

from unittest import IsolatedAsyncioTestCase 
from RemBrake_Core import Message, Display

class BrakeControlTest(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):

        print("") # print first log on the new line
        self.di = board.SCK
        self.dcki = board.RX
        self.buzz = board.MOSI

        self.msg = Message()

        # DUT
        self.dut = Display(self.di, 
                           self.dcki, 
                           self.msg)

        # simulating the display behaviour
        self.dut.ledbar.SIMUL = True

    async def test_alarm_animation(self):
        for _ in range(5):
            animation = self.dut("alarm")
            await animation()
        print("")

    async def test_reset_animation(self):
        # dummy charge value
        self.msg.charge = 0xaa00
        animation = self.dut("reset")
        await animation()
        print("")

    async def test_charging_animation(self):
        # dummy charge value
        self.msg.charge = 0xa100
        for _ in range(5):
            animation = self.dut("charging")
            self.msg.charge += 0x1000
            await animation()
        print("")

    async def test_low_battery(self):
        # dummy charge value
        for _ in range(5):
            animation = self.dut("low_battery")
            await animation()
        print("")

    async def test_indicator_animation(self):
        # dummy charge value
        for _ in range(5):
            self.msg.charge = 0xa000
            animation = self.dut("indicator")
            await animation()
            await asyncio.sleep(0.1)
        print("")

    async def test_welcome_animation(self):
        animation =  self.dut("welcome")
        await animation()
        print("")
        
if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=False)
