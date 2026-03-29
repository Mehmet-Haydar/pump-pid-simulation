# Pump Pressure Control — PID Simulation & TIA Portal SCL

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![SCL](https://img.shields.io/badge/TIA_Portal-V17%2B-orange)
![Standard](https://img.shields.io/badge/Standard-IEC_61131--3_|_ISA--5.1-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Project Overview

This project demonstrates the full engineering workflow from mathematical simulation
to production-ready PLC code for an industrial pump pressure control loop.

**Objective:** Regulate pump discharge pressure to a setpoint of **4.0 bar**
from an initial state of 0 bar using a discrete-time PID algorithm.

The project is structured in two layers:

| Layer | File | Purpose |
|---|---|---|
| Simulation | `pump_pid.py` | Validate PID behavior and process dynamics before PLC deployment |
| Production | `pump_pid_TIA.scl` | IEC 61131-3 SCL code for Siemens S7-1200/1500 |

---

## Control Loop Parameters

| Parameter | Value | Description |
|---|---|---|
| Setpoint (SP) | 4.0 bar | Operating pressure |
| Initial PV | 0.0 bar | System start condition |
| Kp | 1.2 | Proportional gain |
| Ki | 0.5 | Integral gain [1/s] |
| Kd | 0.1 | Derivative gain [s] |
| Process time constant τ | 3.0 s | First-order plant model |
| Settling time (±5%) | ~8 s | Measured in simulation |
| Steady-state error | < 1% | Eliminated by integral action |
| Peak overshoot | 0% | Well-damped tuning |

---

## Technologies

- **Python 3.8+** — standard library only, no external dependencies
- **Siemens TIA Portal V17+** — for SCL import and PLC deployment
- **IEC 61131-3 SCL** — structured text programming language
- **ISA-5.1 / ISA-18.2** — instrumentation notation and alarm philosophy

---

## Running the Python Simulation

```bash
git clone https://github.com/Mehmet-Haydar/pump-pid-simulation.git
cd pump-pid-simulation
python3 pump_pid.py
```

The terminal output displays a timestamped table with PV, SP, control deviation,
controller output, and individual P/I/D contributions. ASCII bar charts with
color-coded deviation bands provide a live view of the control response.

---

## Python Architecture

```
PIDController
├── compute(setpoint, pv, dt) → MV [%]
├── Anti-windup: back-calculation (reverts last integral step on saturation)
└── Derivative spike protection: D = 0 on first execution cycle

PumpSystem  (first-order process model)
├── G(s) = Kp_plant / (τs + 1)  →  Euler forward discretization
├── Actuator deadband: pump inactive below 2% MV
└── Gaussian measurement noise: σ = 0.03 bar (transmitter simulation)

run_simulation()
└── Performance metrics: settling time, peak overshoot, steady-state error
```

---

## TIA Portal Import Instructions

### Step 1 — Create Project
Open TIA Portal V17+ → New Project → Add S7-1200 or S7-1500 PLC.

### Step 2 — Add SCL Function Block
Program blocks → Add new block → Function Block (FB), Language: SCL,
Number: FB100, Name: `PumpPressureControl`.

### Step 3 — Paste Code
Open `pump_pid_TIA.scl`, copy the FB body, paste into TIA Portal SCL editor,
then compile with F7.

### Step 4 — Configure OB35
Create OB35 (Cyclic Interrupt, period: 100 ms). Add the FB100 call from the
SCL file. The instance DB (`PumpPressureControl_DB`) is created automatically.

### Step 5 — I/O Assignment

| SCL Tag | Physical Address | Description |
|---|---|---|
| `DB_IO.AI_pressure_bar` | `%IW64` (scaled) | Pressure transmitter 4–20 mA |
| `DB_IO.AO_pump_raw` | `%QW64` | VFD speed reference output |
| `DB_HMI.pressure_setpoint` | HMI tag | Operator setpoint |
| `DB_HMI.pump_enable` | HMI tag | Start/Stop |

> AI scaling: raw 0 = 0 bar, raw 27648 = 10 bar (Siemens 16-bit standard)

---

## SCL Implementation Highlights

| Feature | Description |
|---|---|
| Bumpless transfer | Integral pre-load on Manual→Auto switch |
| PV validation | Fault output on transmitter out-of-range [-0.5 … 15 bar] |
| Alarm debounce | 500 ms delay (5 scans) prevents nuisance trips |
| AO scaling | `0–100% → 0–27648` for Siemens analog output module |
| Status WORD | Bit-encoded register for HMI/SCADA (Auto/Manual/Alarm/Fault) |

---

## Skills Demonstrated

- Discrete-time PID algorithm from scratch (no libraries)
- Anti-windup via back-calculation (ISA standard method)
- First-order process modeling with Euler discretization
- IEC 61131-3 SCL programming for Siemens TIA Portal
- Bumpless transfer between operating modes
- ISA-18.2 alarm management with debounce logic
- PROFINET-ready status register design

---

## File Structure

```
pump-pid/
├── pump_pid.py       Python PID simulation
├── pump_pid_TIA.scl  TIA Portal SCL source (FB100 + OB35)
├── README.md         German documentation (primary)
├── README_EN.md      This file
└── README_TR.md      Turkish documentation
```

---

## Author

**Mehmet Haydar**
I&C Automation Engineer — Germany
[github.com/Mehmet-Haydar](https://github.com/Mehmet-Haydar)

---

*Part of an Industrial Automation Engineering Portfolio*
*Python Simulation → PLC Production Code (IEC 61131-3 SCL)*

License: MIT
# Update 1
