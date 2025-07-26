#!/usr/bin/python

import board
import asyncio

from unittest import IsolatedAsyncioTestCase 
from RemBrake_Core import BatteryMonitor, Message

class BrakeControlTest(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        print("") # print first log on the new line
        self.message = Message()
        self.i2c = board.I2C()

        # DUT
        self.dut = BatteryMonitor(self.i2c, self.message)
        self.dut()

    async def test_battery_monitor(self):
        
        async def input_dummy_data():
            current_samples = [-0.1, -0.2, -0.3,
                               -0.4, -0.5, -0.6]
            # battery charged
            accumulated_charge = 0xff00
            self.dut.drv.accumulated_charge = accumulated_charge

            for i in current_samples:
                res = self.dut.drv.resistor
                readout_current = int((res*i/0.06)*0x7fff+0x7fff)

                # charge level simulation
                accumulated_charge += 10 if (i >= 0) else -10

                self.dut.drv.set_current(readout_current)
                self.dut.drv.accumulated_charge = accumulated_charge
                await asyncio.sleep(0.2)
        
        test_task = asyncio.create_task(
            input_dummy_data(), 
            name="current_simulation") 
        await test_task

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=False)

