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
  
<img width="513" height="385" alt="bbb_headers" src="https://github.com/user-attachments/assets/ae9b7e7e-b9a2-46fe-99ce-f40bbfd5d12c" />

![a30123495324702ed8b21357d4811e0c](https://github.com/user-attachments/assets/17dc8cb5-628d-4a65-a22f-1f29e19680fd)

Design is around a **single source of truth** (the BBB) with explicit ownership and priority, so “antenna battles” are handled by rules, not by race conditions.

## Core web UI model

BBB maintain a state like:

```json
{
  "radios": {
    "1": {"name": "Atlas 215X", "antenna": 2, "owner": "SM0XYZ"},
    "2": {"name": "K2",        "antenna": null, "owner": null},
    "3": {"name": "uBITX",     "antenna": 4, "owner": "SM0ABC"},
    "4": {"name": "Spare",     "antenna": null, "owner": null}
  },
  "antennas": {
    "1": {"name": "80/40 dipole", "in_use_by": null},
    "2": {"name": "20 m vertical","in_use_by": 1},
    "3": {"name": "15 m Yagi",    "in_use_by": null},
    "4": {"name": "RX loop",      "in_use_by": 3}
  }
}
```

The web page shows this as a 4×4 matrix:

- Rows: radios (with name, owner, TX/busy indicator).
- Columns: antennas (name, band, “in use by …”).
- Cells: button or indicator for “radio X → antenna Y”.

Clicking a cell sends `POST /set` with the user identity (or station label). The backend decides whether to grant or deny.

## Dealing with “battle of antennas”

Pick one of these policies and encode it in the backend:

1. **First‑come, first‑served (simple):**
    - If an antenna is free → grant.
    - If in use and that radio is not TX → deny with message “Antenna in use by Rk/OpName; please coordinate.”
2. **Priority per radio or operator:**
    - Assign each radio or operator a numeric priority.
    - When someone requests an antenna that is in use by *lower* priority, backend can:
        - Either deny with “occupied by higher priority” or
        - Force a pre‑emption with a short countdown (“Op A will be disconnected from A2 in 10 s”).
3. **Reservation / lock:**
    - Add a “lock” flag per antenna or radio: when locked, only the owning operator or the console admin can change assignments.
    - UI shows a lock icon; other operators see the button disabled or get a clear “locked” message.

In all cases, the **logic layer** is the same relay control you already have; the difference is what the HTTP handler allows.

## Web interface details

- Front‑end: a single HTML page (Bootstrap table) that:
    - Polls `/status` every few seconds (or uses WebSockets) to update the matrix.
    - Sends `POST /set` for clicks, including: `radio`, `antenna`, `operator_id`.
- Back‑end (Flask):
    - Extends `set_radio_antenna()` with checks: is antenna free? does priority allow pre‑emption? is this radio locked?
    - On state change: updates `current_assignment` *and* an in‑memory/object store with owner and timestamps.

If you tell how you plan to identify operators (simple shared password per operator vs no auth vs full login), a concrete `/set` API shape and HTML stub for the matrix UI can be sketched next, including where to show “antenna in use by …” and “locked” indicators.
