class PWMOut():
    def __init__(self, servo, duty_cycle, frequency):
        self._servo = servo
        self._duty_cycle = duty_cycle
        self._frequency = frequency

    def __repr__(self):
        return (f"PWM: [{self._servo}," 
        " <Duty Cycle: {self._duty_cycle}>,"
        " <Frequency: {self._frequency}>]")
