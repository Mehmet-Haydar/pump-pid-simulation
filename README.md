# Pump PID Simulation

PID controller simulation for industrial pump systems — tuning, response analysis, and visualization.

## Overview

This project simulates a PID-controlled pump system, demonstrating:
- PID tuning methods (Ziegler-Nichols, manual)
- System response analysis (overshoot, settling time)
- Real-time visualization

## Why This Project?

As an automation engineer, I use Python to simulate and validate control algorithms before implementing them in PLC (SCL/Structured Text). This workflow:
1. **Simulate** in Python → fast iteration, easy debugging
2. **Validate** the logic → test edge cases
3. **Convert** to SCL → deploy on Siemens S7

## Tech Stack

- Python 3.x
- NumPy, Matplotlib
- Control systems libraries

## Quick Start

```bash
git clone https://github.com/Mehmet-Haydar/pump-pid-simulation.git
cd pump-pid-simulation
pip install -r requirements.txt
python main.py
```

## Project Structure

```
pump-pid-simulation/
├── main.py              # Main simulation
├── pid_controller.py    # PID class
├── pump_model.py        # Pump system model
├── visualization.py     # Plotting functions
├── requirements.txt
├── notes-tr/            # Türkçe notlar (personal notes in Turkish)
└── README.md
```

## Related Projects

- [Stewart Platform](https://github.com/Mehmet-Haydar/Stewart_Platform) — 6-DOF kinematics
- [Automation Learning](https://github.com/Mehmet-Haydar/automation-learning) — My PLC/automation journey

## License

MIT

---

*Part of my journey from factory floor to automation engineering.*
*GitHub: [@Mehmet-Haydar](https://github.com/Mehmet-Haydar)*
