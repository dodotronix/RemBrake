# SPDX-License-Identifier: MIT

# RemBrake main application
from RemBrake_Core import BrakeController, RemBrakeBoard

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
rb_brd = RemBrakeBoard(brd_layout)
rb = BrakeController(rb_brd)
rb.start()
