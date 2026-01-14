# 4x4_antenna_switch

BeagleBone Black P8/P9 pins → 16 relay inputs, plus power and grounds. This assumes a 5 V relay board with opto/transistor inputs that are active‑HIGH.

## 1. Power and common connections

- Relay board VCC (logic side): **5 V** from your 5 V supply.
- Relay board GND: to **BeagleBone Black GND** (e.g. P9_1 and/or P9_2).
- If relay board has a separate JD‑VCC (coil power), feed that also with 5 V and keep its GND common with BBB.

Do **not** power the relay coils from the BBB’s 5 V pin; use an external 5 V supply sized for all 16 relays on, then tie grounds together.

## 2. BeagleBone → relay input mapping

Use only GPIO‑safe pins (no HDMI/eMMC conflicts) and keep them in order so cabling is simple. One possible mapping:


| Relay | Relay IN pin | BBB header pin | BBB signal name |
| :-- | :-- | :-- | :-- |
| 1 | IN1 | P8_7 | GPIO66 |
| 2 | IN2 | P8_8 | GPIO67 |
| 3 | IN3 | P8_9 | GPIO69 |
| 4 | IN4 | P8_10 | GPIO68 |
| 5 | IN5 | P8_11 | GPIO45 |
| 6 | IN6 | P8_12 | GPIO44 |
| 7 | IN7 | P8_14 | GPIO26 |
| 8 | IN8 | P8_15 | GPIO47 |
| 9 | IN9 | P8_16 | GPIO46 |
| 10 | IN10 | P8_17 | GPIO27 |
| 11 | IN11 | P8_18 | GPIO65 |
| 12 | IN12 | P8_26 | GPIO61 |
| 13 | IN13 | P9_12 | GPIO60 |
| 14 | IN14 | P9_15 | GPIO48 |
| 15 | IN15 | P9_23 | GPIO49 |
| 16 | IN16 | P9_41 | GPIO20 |

Notes:

- All listed pins are standard GPIOs on P8/P9 and are safe to use for output when configured correctly in the device tree.
- Run a 16‑way ribbon (or two 8‑way) from these BBB pins to the relay board’s IN1–IN16.
- Double‑check the particular relay board’s pinout: some are active‑LOW (IN pulled low turns relay ON). If so, you will invert logic in software, but wiring stays the same.


## 3. RF side wiring (radios/antennas → relay contacts)

Same logical scheme as before, now tied to relay numbers above:

- Radios: R1, R2, R3, R4.
- Antennas: A1, A2, A3, A4.

**Relay assignment:**

- R1–A1 → relay 1 (IN1 / P8_7)
- R1–A2 → relay 2 (IN2 / P8_8)
- R1–A3 → relay 3 (IN3 / P8_9)
- R1–A4 → relay 4 (IN4 / P8_10)
- R2–A1 → relay 5 (IN5 / P8_11)
- R2–A2 → relay 6 (IN6 / P8_12)
- R2–A3 → relay 7 (IN7 / P8_14)
- R2–A4 → relay 8 (IN8 / P8_15)
- R3–A1 → relay 9 (IN9 / P8_16)
- R3–A2 → relay 10 (IN10 / P8_17)
- R3–A3 → relay 11 (IN11 / P8_18)
- R3–A4 → relay 12 (IN12 / P8_26)
- R4–A1 → relay 13 (IN13 / P9_12)
- R4–A2 → relay 14 (IN14 / P9_15)
- R4–A3 → relay 15 (IN15 / P9_23)
- R4–A4 → relay 16 (IN16 / P9_41)

**RF contacts:**

For radio 1 (R1):

- Tie COM of relays 1–4 together → short coax bus → R1 connector.
- NO of relay 1 → short coax → A1 connector.
- NO of relay 2 → short coax → A2 connector.
- NO of relay 3 → short coax → A3 connector.
- NO of relay 4 → short coax → A4 connector.

Repeat:

- R2: COM relays 5–8 bussed → R2; NOs of 5–8 to A1–A4.
- R3: COM relays 9–12 bussed → R3; NOs to A1–A4.
- R4: COM relays 13–16 bussed → R4; NOs to A1–A4.

NC terminals: leave open or tie to ground/dummy load according to how much extra isolation wanted; for QRP a simple open is usually fine if coax and box layout are tight.

## 4. Mechanical / grounding

- Mount relay board and all 8 RF connectors (4 radios, 4 antennas) in a metal box.
- Keep coax pigtails as short and direct as possible; bond shields to the box.
- Bring the BBB in via a shielded cable or mount it inside and bring Ethernet/USB out with appropriate feedthroughs.
- Tie BBB ground to the RF box ground at one solid point.
