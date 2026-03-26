# Automation Project Standards — Mehmet Haydar

## Code Comments
- Always write comments in English
- Use ISA-5.1 and IEC 61131-3 terminology throughout
- Every function block (FB) must have a header comment block containing:
  block name, purpose, calling OB, author, and applicable standards
- Every logical section within a function block must have a numbered inline comment
- Variable declarations must include unit annotations in brackets, e.g. `[bar]`, `[%]`, `[s]`

## README Structure
- `README.md` = German (primary documentation — most comprehensive)
- `README_EN.md` = English
- `README_TR.md` = Turkish
- All three must contain: project purpose, technologies, setup,
  Python simulation instructions, TIA Portal import procedure

## SCL Standards
- Target platform: TIA Portal V17+ (S7-1200 / S7-1500)
- All cyclic function blocks must be called from OB35 (100 ms cycle time)
- All PID function blocks must implement anti-windup (back-calculation method)
- All controllers must support bumpless transfer on Manual → Auto mode switch
- Output variables must use ISA naming: SP (setpoint), PV (process variable), MV (manipulated variable)
- Alarm logic must comply with ISA-18.2: include scan-count debounce before latching
- AO scaling must use Siemens 16-bit raw: 0–27648 corresponds to 0–100%
- Status registers must use bit-encoded WORD for HMI/SCADA transport

## Python Simulation Standards
- Always simulate the control algorithm in Python before writing SCL code
- Simulation must use the same variable names as the SCL implementation
- Required performance metrics in every simulation output:
  - Settling time (±5% band of setpoint)
  - Peak overshoot [engineering unit and %]
  - Steady-state error [engineering unit and %]
- Process model must include Gaussian measurement noise for realistic sensor simulation
- Anti-windup and first-scan protection must be present in Python before SCL translation

## Git Commit Messages
- Always write commit messages in English
- Format: `<type>: <short imperative description>`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Examples:
  - `feat: add anti-windup back-calculation to PID controller`
  - `docs: add bilingual README (DE/EN/TR)`
  - `fix: suppress derivative spike on first scan cycle`
