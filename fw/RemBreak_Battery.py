
import asyncio
from CircuitPython_LTC2943 import LTC2943, ALCC, Mode, Prescaler

class BatteryMonitor():

    def __init__(self, drv, display, plugged, charging=None) -> None:
        self._drv = drv
        self._plugged = plugged 
        self._charging = charging
        self._display = display

        drv.adc_mode = Mode.AUTOMATIC
        drv.prescaler = Prescaler.PRES_M64
        drv.alcc = ALCC.DISABLE
        # TODO config thresholds

        # measured physical quantities
        self.current = [0, 0] # current, previous
        self.voltage = [0, 0]
        self.charge = [0, 0]
        self.temperature = 0
        self.refresh_rate = 0.2
        self.percentage = 0

        charge_rg = self._drv.charge_range 
        self.charge_span = charge_rg[1] - charge_rg[0]

    async def start(self):
        t = asyncio.create_task(self._display.start())

        while True:

            self.current[1] = self.current[0] 
            self.current[0] = self._drv.current
            await asyncio.sleep(self.refresh_rate)
            self.voltage[1] = self.voltage[0] 
            self.voltage[0] = self._drv.voltage
            await asyncio.sleep(self.refresh_rate)
            self.charge[1] = self.charge[0]
            self.charge[0] = self._drv.accumulated_charge
            self.percentage = self.charge[0]/self.charge_span
            self._display.percentage = self.percentage

            if not self._charging.value and not self._plugged.value:
                self._display.mode[0] = self._display.PONG
                if self.charge[1] > self.charge[0]:
                    self._drv.accumulated_charge = self.charge[1]
                    self.charge[0] = self.charge[1]
            else:
                self._display.mode[0] = self._display.STATUS

            await asyncio.sleep(self.refresh_rate)
            self.temperature = self._drv.temperature
            await asyncio.sleep(self.refresh_rate)

    async def reset(self):
        self._display.mode[0] = self._display.BLINK_ALL
        
        print("waiting USB to be connected")
        # wait until plugged into USB-c and fully charged
        while self._plugged.value or self._charging.value: 
            print(self._plugged.value, self._charging.value)
            await asyncio.sleep(1)

        print("waiting until it is charged")
        # wait until the charging pin is up again
        while not self._charging.value:
            await asyncio.sleep(1)

        # reset the LTC2943 charge counter
        self._drv.accumulated_charge = 0xffff
        self._display.mode[0] = self._display.STATUS
        print("charged")
