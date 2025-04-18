#!/usr/bin/python

import unittest

import board
from RemBrake_Core import BrakeCore

class BrakeControlTest(unittest.TestCase):

    def SetUp(self):
        self.message = Message()
        self.power = board.D2
        self.remote = board.TX
        self.handlebars = board.MISO

        # DUT
        self.dut = BrakeControl(board.D3, self.power, 
                                self.remote, self.remote, 
                                self.handlebars)

    # test
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

if __name__ == '__main__':
    unittest.main()
