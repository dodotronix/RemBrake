
class Servo:
    def __init__(self, pwm):
        self._pwm = pwm
        self._angle = 100

    def __repr__(self):
        return f"Servo: [{self._pwm}, <Angle: {self._angle}>]"

    @property
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, value):
        self._angle = value
