
import asyncio
from CircuitPython_LTC2943 import LTC2943, ALCC, Mode, Prescaler

class BatteryMonitor():

    WELCOME = [("D4", 0.1), ("G4", 0.1), ("C5", 0.1), ("E5", 0.1)]
    ERROR = [ ("E7", 0.5), ("-", 0.1),  ("E7", 0.5), ("-", 0.1)]
    WARNING = [ ("G4", 0.3), ("-", 0.2), ("G4", 0.3), ("-", 0.2)]

    def __init__(self, drv, display, sound, switch, plugged, charging=None) -> None:
        self._drv = drv
        self._plugged = plugged 
        self._charging = charging
        self._display = display
        self._sound = sound
        self.sw = switch

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
        self.warning = None
        self.error = None
        self.status = 0

        self.warning_threshold = 0xffff-100
        self.error_threlhold = 0xffff-200

        self._drv.charge_range = (0xff00, 0xffff)
        charge_rg = self._drv.charge_range 
        self.charge_span = charge_rg[1] - charge_rg[0]

    async def start(self):
        asyncio.create_task(self._sound.play(self.WELCOME))
        asyncio.create_task(self._display.start())
        print("TODO: servo power back on")
        # self.sw.value = False

        while True:

            self.current[1] = self.current[0] 
            self.current[0] = self._drv.current
            await asyncio.sleep(self.refresh_rate)
            self.voltage[1] = self.voltage[0] 
            self.voltage[0] = self._drv.voltage
            await asyncio.sleep(self.refresh_rate)
            self.status = self._drv.status
            await asyncio.sleep(self.refresh_rate)

            # when counter overflow limit the value
            if (self.status >> 5 & 0x1) and not self._charging.value:
                self._drv.accumulated_charge = 0xffff
            self.charge[1] = self.charge[0]
            self.charge[0] = self._drv.accumulated_charge
            self.percentage = (self.charge[0] - 0xff00)/self.charge_span
            print(f"percentage: {self.percentage}")
            self._display.percentage = self.percentage

            if not self._charging.value and not self._plugged.value:
                self._display.mode[0] = self._display.CHARGE
            else:
                self._display.mode[0] = self._display.STATUS

            print(self.charge)

            # Alarms
            if self.charge[0] < self.error_threlhold and self._charging.value and self.error == None:
                try:
                    print("reset warning task")
                    self.warning.cancel()
                except:
                    pass
                print("created error task")
                self.error = asyncio.create_task(self.error_routine()) 

            elif not self._charging.value and self.error != None:
                print("reseting error alarm")
                try:
                    self.error.cancel()
                    self.error = None
                except:
                    pass
                print("TODO: servo power back on")
                # self.sw.value = False

            if (self.charge[0] < self.warning_threshold and self.charge[0] > self.error_threlhold and self._charging.value and
                    self.warning == None and self.error == None):
                print("created warning task")
                self.warning = asyncio.create_task(self.warning_routine())

            elif not self._charging.value and self.warning != None:
                print("reseting warning alarm")
                try:
                    self.warning.cancel()
                    self.warning = None
                except:
                    pass
                
            await asyncio.sleep(self.refresh_rate)
            self.temperature = self._drv.temperature
            await asyncio.sleep(self.refresh_rate)

    async def warning_routine(self):
        while True:
            print("warning low charge")
            asyncio.create_task(self._sound.play(self.WARNING))
            await asyncio.sleep(5)

    async def error_routine(self):
        print("TODO: cut servo power")
        print("error low charge")
        while True:
            asyncio.create_task(self._sound.play(self.ERROR))
            await asyncio.sleep(2)

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
