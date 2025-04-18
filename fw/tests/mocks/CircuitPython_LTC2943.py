
# SPDX-License-Identifier: MIT

import logging as lg

import board

class ALCC:
    ALERT = 0x02
    CHARGE_COMPLETE = 0x01
    DISABLE = 0x00

class Mode:
    AUTOMATIC = 0x03
    SCAN = 0x02
    MANUAL = 0x01
    SLEEP = 0x00

class Prescaler:
    PRES_M1 = 0x00
    PRES_M4 = 0x01
    PRES_M16 = 0x02
    PRES_M64 = 0x03
    PRES_M256 = 0x04
    PRES_M1024 = 0x05
    PRES_M4096 = 0x06

class LTC2943:
    def __init__(self, i2c: board.I2C, addr=0x64, res=2e-3) -> None:
        lg.info(f"Initializing LTC2943's I2C on address {addr},"
                f"with resistor value {res}")
        self.resistor = res
        self.i2c_bus = i2c
        self.i2c_addr = addr
        self.reset()

    def reset(self):
        self._voltage_threshold_low = 0
        self._voltage_threshold_high = 0xffff
        self._voltage_raw = 0xffff

        self._current_threshold_low = 0
        self._current_threshold_high = 0xffff
        self._current_raw = 0

        self._temperature_threshold = 0xffff
        self._temperature_raw = 0

        self._shutdown = 0

        self._accumulated_charge = 0xffff
        self._charge_threshold_low = 0
        self._charge_threshold_high = 0xffff

    # TODO set generators of noise, and charging and discharging profiles
    def testbench(self, ):
        pass

    # Here are the functions of the real LTC2943
    @property
    def voltage(self) -> float:
        """Get voltage in Volts"""
        return 23.6*self._voltage_raw/0xffff

    @property
    def voltage_range(self):
        return (self._voltage_threshold_low, self._voltage_threshold_high)

    @voltage_range.setter
    def voltage_range(self, rg):
        def tf(v) -> int:
            return int(0xffff*v/23.6)

        low, high = rg
        print(tf(low), tf(high))
        self._voltage_threshold_low = tf(low)
        self._voltage_threshold_high = tf(high)


    @property
    def temperature(self) -> float:
        """Get temperature in degree celsius"""
        return 510*self._temperature_raw/0xffff - 273.15 

    @property
    def temperature_threshold(self):
        return self.temperature_threshold

    @temperature_threshold.setter
    def temperature_threshold(self, th):
        """Set temperature threshold in degree celsius"""
        self._temperature_threshold = (th + 273.15)*0xffff/510 

    @property
    def current(self) -> float:
        """Get current in Amps."""
        return (0.06/self.resistor)*((self._current_raw-0x7fff)/0x7fff)

    @property
    def current_range(self):
        return (self._current_threshold_low, self._current_threshold_high)

    @current_range.setter
    def current_range(self, rg):
        """Set current low and high threshold."""

        def tf(v):
            return int((0x7fff*v/(0.06/self.resistor))+0x7fff)

        low, high = rg
        self._current_threshold_low  = tf(low) 
        self._current_threshold_high  = tf(high)

    @property
    def accumulated_charge(self) -> int:
        """The accumulated charge property."""
        return self._accumulated_charge

    @accumulated_charge.setter
    def accumulated_charge(self, value: int) -> None:
        """Set actual charge value """
        self._shutdown = True
        self._accumulated_charge = value
        self._shutdown = False

    @property
    def charge_range(self):
        return (self._charge_threshold_low, self._charge_threshold_high)

    @charge_range.setter
    def charge_range(self, rg):
        """Set charge low and high threshold."""
        low, high = rg
        self._charge_threshold_low = low 
        self._charge_threshold_high = high 

