import board
import digitalio
import neopixel

from time import sleep
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219

from CircuitPython_MY9221 import MY9221
from CircuitPython_LTC2943 import LTC2943
from CircuitPython_RemBreak import BatteryMonitor

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
i2c = board.I2C()
bms = LTC2943(i2c) 
display = MY9221(board.D2, board.D3)
battery_monitor = BatteryMonitor(bms, display, board.MISO)

while True:
    # print(bms.accumulated_charge)
    # print(bms.voltage)
    # print(bms.current)
    # battery_monitor.charging()
    battery_monitor.start()
    pixel.fill((0, 0, 10))
    sleep(0.5)
    pixel.fill((0, 0, 0))
    sleep(0.5)
