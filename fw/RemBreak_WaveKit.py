
# SPDX-License-Identifier: MIT
import pwmio
import asyncio

class Tones():

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
            "A#2": 117,
            "B2": 123,
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
            "A#3": 233,
            "B3": 247,
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
            "A#4": 466,
            "B4": 494,
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
            "A#5": 932,
            "B5": 988,
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
            "A#6": 1865,
            "B6": 1976,
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
            "A#7": 3729,
            "B7": 3951,
            "C8": 4186,
            "-": 0
        }

    def __init__(self, pwm) -> None:
        self._pwm = pwm
        self.notes = None
        self.playing = None

    async def _worker(self):
        self._pwm.duty_cycle = 0x7FFF
        for frequency, duration in self.notes:
            if not frequency:
                self._pwm.duty_cycle = 0
            else:
                self._pwm.duty_cycle = 0x7FFF
                self._pwm.frequency = frequency
            await asyncio.sleep(duration)
        self._pwm.duty_cycle = 0

    async def play(self, notes):
        self.notes = []

        # stop previous tune
        if self.playing and not self.playing.done():
            self.playing.cancel()

        # translate string to frequency
        for note, duration in notes:
            self.notes.append((self.NOTES[note], duration))

        # play track
        self.playing = asyncio.create_task(self._worker())
