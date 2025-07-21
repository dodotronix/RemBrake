#!/usr/bin/python

import asyncio

from unittest import IsolatedAsyncioTestCase 
from RemBrake_Core import BrakeCore

class RemBrakeCoreTest(IsolatedAsyncioTestCase):
    def plugged(self, value):
        self.dut.keys.set(0, value)

    def handlebars(self, value):
        self.dut.keys.set(1, value)

    def remote(self, value):
        self.dut.keys.set(2, value)

    def charge(self, value):
        self.dut.battery.drv.set_accumulated_charge(value)

    def current(self, value):
        self.dut.battery.drv.set_current(value)

    def status(self, value):
        self.dut.battery.drv.status = value

    def undervoltage(self):
        self.status(0x06)

    def overflow(self):
        self.status(0x20)

    def charged(self, value):
        self.dut.ready.set(value)

    async def asyncSetUp(self):
        print("") # print first log on the new line
        self.layout = {
            "ready":        "D0",
            "enable":       "D1",
            "power":        "D2",
            "servo":        "D3",
            "remote":       "TX",
            "buzz":         "MOSI",
            "handlebars":   "MISO",
            "display_di":   "SCK",
            "display_dcki": "RX"}

        # DUT
        self.dut = BrakeCore(self.layout)
        # initial battery charge
        self.charge(0xaf00)

        asyncio.create_task(self.dut.main())

    # async def test_charging(self):
    #     async def seq_gen():
    #         await asyncio.sleep(0.78)
    #         self.plugged(True)
    #         await asyncio.sleep(1)
    #         self.plugged(False)
    #         await asyncio.sleep(0.2)
    #         self.plugged(True)
    #         await asyncio.sleep(1.4)

    #     sequence = asyncio.create_task(
    #         seq_gen(), name="charging_sequence") 
    #     await sequence 

    # async def test_reset(self):
    #     async def seq_gen():
    #         await asyncio.sleep(1.51)
    #         self.plugged(True)
    #         await asyncio.sleep(0.2)
    #         self.charged(True)
    #         await asyncio.sleep(1.04)
    #         self.remote(True)
    #         await asyncio.sleep(0.2)
    #         self.handlebars(True)
    #         await asyncio.sleep(3.1)

    #     sequence = asyncio.create_task(
    #         seq_gen(), name="reset_sequence") 
    #     await sequence 

    # async def test_user_braking(self):
    #     async def seq_gen():
    #         await asyncio.sleep(1.6)
    #         self.handlebars(True)
    #         await asyncio.sleep(0.2)
    #         self.remote(True)
    #         await asyncio.sleep(18)

    #     sequence = asyncio.create_task(
    #         seq_gen(), name="user_braking_sequence") 
    #     await sequence 

    async def test_low_battery(self):
        async def seq_gen():
            self.dut.msg.charge = 0x00fa
            self.status(0x04)
            await asyncio.sleep(1.6)
            self.plugged(True)
            await asyncio.sleep(1.6)

        sequence = asyncio.create_task(
            seq_gen(), name="low_battery_sequence") 
        await sequence 

    # async def test_boot(self):
    #     async def seq_gen():
    #         self.plugged(True)
    #         self.status(0x02)
    #         await asyncio.sleep(1.6)
    #         self.status(0x00)
    #         await asyncio.sleep(2)

    #     sequence = asyncio.create_task(
    #         seq_gen(), name="boot_sequence") 
    #     await sequence 

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=False)
