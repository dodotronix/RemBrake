#!/usr/bin/python

import board
import asyncio

from unittest import IsolatedAsyncioTestCase 
from RemBrake_Core import BrakeControl, Message

class BrakeControlTest(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):

        print("") # print first log on the new line
        self.message = Message()
        self.servo = board.D3
        self.power = board.D2

        # DUT
        self.dut = BrakeControl(self.servo, 
                                self.power,
                                self.message)

        # self.assertTrue(True) # Dummy assertion
        self.dut()

    async def test_assistant_button(self):

        async def gen_key_seq():
            await asyncio.sleep(0.1)
            self.message.callbacks["braking"].try_run("user")
            await asyncio.sleep(0.1)
            self.message.callbacks["braking"].force_run("assistant")
            await asyncio.sleep(0.1)
            # self.assertTrue(self.dut.assistant.done())
        
        test_task = asyncio.create_task(gen_key_seq(), name="test") 
        await test_task

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=False)

