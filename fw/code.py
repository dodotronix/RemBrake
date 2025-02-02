# SPDX-License-Identifier: MIT

# RemBreak main application
from RemBreak_Core import BreakController, RemBreakBoard

brd_layout = {
    "actuator":          "RX",
    "buzzer":            "SCK",
    "handlebars_button": "MISO",
    "charging":          "MOSI",
    "ledbar_di":         "D2",
    "ledbar_dcki":       "D3",
    "plugged":           "D1",
    "remote_switch":     "D0",
    "actuator_switch":   "TX"}

# INITIALIZE REMBREAK BOARD
rb_brd = RemBreakBoard(brd_layout)
rb = BreakController(rb_brd)
rb.start()
