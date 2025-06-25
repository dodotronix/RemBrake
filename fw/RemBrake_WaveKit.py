# SPDX-License-Identifier: MIT
import pwmio
import asyncio

try:
    import adafruit_logging as lg
except:
    import logging as lg


logger = lg.getLogger(__name__)
logger.setLevel(lg.INFO)

class Composer():

    NOTES = {
        "C2": 65,
        "C#2": 69,
        "D2": 73,
        "D#2": 78,
        "E2": 82,
        "F2": 87,
        "F#2": 92,
        "G2": 98,
        "G#2": 104,
        "A2": 110,
        "B2": 117,
        "H2": 123,
        "C3": 131,
        "C#3": 139,
        "D3": 147,
        "D#3": 156,
        "E3": 165,
        "F3": 175,
        "F#3": 185,
        "G3": 196,
        "G#3": 208,
        "A3": 220,
        "B3": 233,
        "H3": 247,
        "C4": 262,
        "C#4": 277,
        "D4": 294,
        "D#4": 311,
        "E4": 330,
        "F4": 349,
        "F#4": 370,
        "G4": 392,
        "G#4": 415,
        "A4": 440,
        "B4": 466,
        "H4": 494,
        "C5": 523,
        "C#5": 554,
        "D5": 587,
        "D#5": 622,
        "E5": 659,
        "F5": 698,
        "F#5": 740,
        "G5": 784,
        "G#5": 831,
        "A5": 880,
        "B5": 932,
        "H5": 988,
        "C6": 1047,
        "C#6": 1109,
        "D6": 1175,
        "D#6": 1245,
        "E6": 1319,
        "F6": 1397,
        "F#6": 1480,
        "G6": 1568,
        "G#6": 1661,
        "A6": 1760,
        "B6": 1865,
        "H6": 1976,
        "C7": 2093,
        "C#7": 2217,
        "D7": 2349,
        "D#7": 2489,
        "E7": 2637,
        "F7": 2794,
        "F#7": 2960,
        "G7": 3136,
        "G#7": 3322,
        "A7": 3520,
        "B7": 3729,
        "H7": 3951,
        "C8": 4186,
        "-": 0
    }

    def __init__(self, buzz) -> None:
        self._pwm = pwmio.PWMOut(buzz, variable_frequency=True)
        self.notes = [] 

    async def _worker(self):
        try:
            logger.info(f"starting new soundtrack")
            self._pwm.duty_cycle = 0x7FFF
            for frequency, duration in self.notes:
                if not frequency:
                    self._pwm.duty_cycle = 0
                else:
                    self._pwm.duty_cycle = 0x7FFF
                    self._pwm.frequency = frequency
                logger.info("frequency: {}; duty_cycle: {}; "
                    "duration: {}".format(self._pwm.frequency, 
                                          self._pwm.duty_cycle, 
                                          duration))

                await asyncio.sleep(duration)
            self._pwm.duty_cycle = 0

        except asyncio.CancelledError:
            print(f"soundtrack canceled")

    def __call__(self, notes):
        self.notes = []

        # translate string to frequency
        for note, duration in notes:
            self.notes.append((self.NOTES[note], duration))

        # return track player
        return self._worker
