
import logging as lg

logger = lg.getLogger(__name__)
logger.setLevel(lg.INFO)

class PWMOut():
    def __init__(self, pin, duty_cycle:int=0, 
                 frequency:int = 500, 
                 variable_frequency:bool = False):
        self._pin = pin 
        self._duty_cycle = duty_cycle
        self._frequency = frequency
        self._varible_frequency = variable_frequency

    def deinit(self):
        logger.info(f"MOCK deinitializing PWM {self._pin}")

    def __repr__(self):
        return (f"PWM: [{self._pin}," 
        f" <Duty Cycle: {self._duty_cycle}>,"
        f" <Frequency: {self._frequency}>]")
