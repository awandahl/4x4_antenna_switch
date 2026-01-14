# file: matrix_switch.py

import time
from flask import Flask, request, jsonify
import Adafruit_BBIO.GPIO as GPIO

app = Flask(__name__)

# Map relays (1..16) to BeagleBone pins (as previously agreed)
RELAY_GPIO = {
    1:  "P8_7",
    2:  "P8_8",
    3:  "P8_9",
    4:  "P8_10",
    5:  "P8_11",
    6:  "P8_12",
    7:  "P8_14",
    8:  "P8_15",
    9:  "P8_16",
    10: "P8_17",
    11: "P8_18",
    12: "P8_26",
    13: "P9_12",
    14: "P9_15",
    15: "P9_23",
    16: "P9_41",
}

# Radio and antenna indices 1..4
RADIOS = [1, 2, 3, 4]
ANTENNAS = [1, 2, 3, 4]

# Relay assignment: (radio, antenna) -> relay number
PAIR_TO_RELAY = {}
for r in RADIOS:
    for a in ANTENNAS:
        # relay numbering in row-major order:
        # R1A1=1, R1A2=2, ..., R2A1=5, ...
        relay = (r - 1) * 4 + a
        PAIR_TO_RELAY[(r, a)] = relay

# Track current assignments: radio -> antenna (or None)
current_assignment = {r: None for r in RADIOS}

# Adjust if your board is active-LOW
ACTIVE_HIGH = True


def relay_on(relay_num):
    pin = RELAY_GPIO[relay_num]
    GPIO.output(pin, GPIO.HIGH if ACTIVE_HIGH else GPIO.LOW)


def relay_off(relay_num):
    pin = RELAY_GPIO[relay_num]
    GPIO.output(pin, GPIO.LOW if ACTIVE_HIGH else GPIO.HIGH)


def init_relays():
    for relay, pin in RELAY_GPIO.items():
        GPIO.setup(pin, GPIO.OUT)
        # All OFF at startup
        relay_off(relay)


init_relays()
