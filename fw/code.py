import board
import digitalio
import neopixel
import asyncio

from time import sleep
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219

from CircuitPython_MY9221 import MY9221
from CircuitPython_LTC2943 import LTC2943
from CircuitPython_RemBreak import BatteryMonitor, BreakController

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
i2c = board.I2C()
bms = LTC2943(i2c) 
display = MY9221(board.D2, board.D3)

# APPLICATION OBJECTS
battery_monitor = BatteryMonitor(bms, display, board.MISO)
break_controller = BreakController(board.RX, board.D0, board.SCK, board.TX)

async def blink():
    while True:
        pixel.fill((0, 0, 10))
        await asyncio.sleep(0.2)
        pixel.fill((0, 0, 0))
        await asyncio.sleep(0.2)

async def main():
    rgb_led = asyncio.create_task(blink())
    break_test = asyncio.create_task(break_controller.active())
    display_test = asyncio.create_task(battery_monitor.status())
    await asyncio.gather(rgb_led, break_test, display_test)

asyncio.run(main())
