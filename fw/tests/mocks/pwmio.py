class PWMOut():
    def __init__(self, pin, duty_cycle, frequency):
        self._pin = pin 
        self._duty_cycle = duty_cycle
        self._frequency = frequency

    def __repr__(self):
        return (f"PWM: [{self._pin}," 
        " <Duty Cycle: {self._duty_cycle}>,"
        " <Frequency: {self._frequency}>]")
