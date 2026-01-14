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

DEAD_TIME_SEC = 0.05  # 50 ms dead time


def set_radio_antenna(radio, antenna):
    """
    Set 'radio' (1..4) to 'antenna' (1..4) or None to disconnect.
    Enforces one antenna per radio and one radio per antenna.
    """

    if radio not in RADIOS:
        raise ValueError("Invalid radio")
    if antenna is not None and antenna not in ANTENNAS:
        raise ValueError("Invalid antenna")

    # 1) Turn off any relay currently used by this radio
    old_ant = current_assignment[radio]
    if old_ant is not None:
        old_relay = PAIR_TO_RELAY[(radio, old_ant)]
        relay_off(old_relay)
        current_assignment[radio] = None

    # 2) Ensure no other radio is using this antenna (if requested)
    if antenna is not None:
        for r, a in current_assignment.items():
            if r != radio and a == antenna:
                # Disconnect that other radio first
                off_relay = PAIR_TO_RELAY[(r, a)]
                relay_off(off_relay)
                current_assignment[r] = None

    # 3) Dead time (break-before-make)
    time.sleep(DEAD_TIME_SEC)

    # 4) Turn on new relay, if any
    if antenna is not None:
        relay = PAIR_TO_RELAY[(radio, antenna)]
        relay_on(relay)
        current_assignment[radio] = antenna

