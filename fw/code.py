# SPDX-License-Identifier: MIT

# RemBrake main application
from RemBrake_Core import BrakeCore

layout = {
    "ready":        "D0",
    "enable":       "D1",
    "power":        "D2",
    "servo":        "D3",
    "remote":       "TX",
    "buzz":         "MOSI",
    "handlebars":   "MISO",
    "display_di":   "SCK",
    "display_dcki": "RX"}

# INITIALIZE REMBREAK BOARD
core = BrakeCore(layout)
core.run()
