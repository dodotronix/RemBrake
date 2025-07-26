#!/usr/bin/python

import board
import asyncio

from unittest import IsolatedAsyncioTestCase 
from RemBrake_WaveKit import Composer

class WaveKitTest(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        print("") # print first log on the new line
        self.buzz = board.MOSI

        # DUT
        self.dut = Composer(self.buzz)

    async def test_welcome_sound(self):

        notes = [("C4", 0.3), ("E4", 0.3), ("G4", 0.3), 
                 ("C5", 0.5), ("-", 0.2), ("C4", 0.4)]

        # self.assertTrue(self.dut.assistant.done())
        self.dut(notes)
        await asyncio.sleep(1)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=False)

