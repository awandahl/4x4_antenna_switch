
# 4x4_antenna_switch

Mapping that includes both **GPIO numbers and the physical header pins** on the standard Wemos/AZ‑Delivery Lolin32.

## Lolin32 → 16‑relay board wiring

Use any free header pins that expose the listed GPIOs; the “Pin\#” column is the silkscreen/header position on the Lolin32 board.


| Relay IN | ESP32 GPIO | Lolin32 header pin label / position |
| :-- | :-- | :-- |
| IN1 | GPIO4 | Pin labeled **4** |
| IN2 | GPIO5 | Pin labeled **5** |
| IN3 | GPIO12 | Pin labeled **12** |
| IN4 | GPIO13 | Pin labeled **13** |
| IN5 | GPIO14 | Pin labeled **14** |
| IN6 | GPIO16 | Pin labeled **16** |
| IN7 | GPIO17 | Pin labeled **17** |
| IN8 | GPIO18 | Pin labeled **18** |
| IN9 | GPIO19 | Pin labeled **19** |
| IN10 | GPIO21 | Pin labeled **21** |
| IN11 | GPIO22 | Pin labeled **22** |
| IN12 | GPIO23 | Pin labeled **23** |
| IN13 | GPIO25 | Pin labeled **25** |
| IN14 | GPIO26 | Pin labeled **26** |
| IN15 | GPIO27 | Pin labeled **27** |
| IN16 | GPIO32 | Pin labeled **32** |

Common connections:

- Any Lolin32 **GND** pin → relay board **GND**.
- Your internal **5 V** injection (from buck or relay‑board converter) goes to the Lolin32 5 V rail point you choose to solder to, not a header pin.[^2][^3]


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
  

![a30123495324702ed8b21357d4811e0c](https://github.com/user-attachments/assets/17dc8cb5-628d-4a65-a22f-1f29e19680fd)
<img width="1262" height="921" alt="Screenshot 2026-01-28 at 22-09-27 ESP32_Lolin32_Pinout pdf" src="https://github.com/user-attachments/assets/72f699b9-1a5b-4d10-962c-778f14f00bbe" />

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
