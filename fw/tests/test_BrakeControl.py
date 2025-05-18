#!/usr/bin/python

from unittest import IsolatedAsyncioTestCase 
import board
import asyncio
import logging as lg

import sys
logger = lg.getLogger()
logger.level = lg.DEBUG

from RemBrake_Core import BrakeControl, Message

class BrakeControlTest(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.message = Message()
        self.power = board.D2
        self.remote = board.TX
        self.handlebars = board.MISO

        # DUT
        self.dut = BrakeControl(board.D3, 
                                self.power, 
                                self.remote, 
                                self.handlebars, 
                                self.message)

        self.assertTrue(True) # Dummy assertion
        self.dut_task = asyncio.create_task(self.dut.tasks(), name="dut")

    async def asyncTearDown(self):
        self.dut_task.cancel()
        try:
            await self.dut_task
        except asyncio.CancelledError:
            pass

    async def test_assistant_button(self):

        async def gen_key_seq():
            self.dut.keys.set(0, 1)
            await asyncio.sleep(0.1)
            self.assertFalse(self.dut.assistant.done())
            self.dut.keys.set(0, 0)
            await asyncio.sleep(0.1)
            # self.assertTrue(self.dut.assistant.done())
            # await asyncio.sleep(0.5)
        
        test_task = asyncio.create_task(gen_key_seq(), name="test") 
        await test_task

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=False)

