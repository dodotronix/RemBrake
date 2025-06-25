
import logging as lg

logger = lg.getLogger(__name__)
logger.setLevel(lg.INFO)

class Servo:
    def __init__(self, pwm):
        self._pwm = pwm
        self._angle = 100
        logger.info(f"MOCK_INFO initializing servo {self._pwm}; angle {self._angle}")

    def __repr__(self):
        return f"MOCK_INFO servo [{self._pwm}, <Angle: {self._angle}>]"

    @property
    def angle(self):
        logger.info(f"MOCK_GET servo angle {self._angle} deg")
        return self._angle
    
    @angle.setter
    def angle(self, value):
        self._angle = value
        logger.info(f"MOCK_SET servo angle to {self._angle} deg")
