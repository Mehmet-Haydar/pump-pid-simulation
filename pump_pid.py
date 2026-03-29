#!/usr/bin/env python3
"""
Pump Pressure Control System — PID Simulation
Setpoint: 4 bar | Kp=2.0  Ki=0.5  Kd=0.1
Plant model: First-order lag process (tau=3 s, Kp_plant=0.8)

Author  : Mehmet Haydar, I&C Automation Engineer
Standard: ISA-5.1, IEC 61131-3
"""

import time


# ─────────────────────────────────────────────────────────────────────────────
#  PID CONTROLLER
#  Implements a discrete-time PID algorithm with:
#    - Back-calculation anti-windup (ISA standard method)
#    - Derivative spike suppression on first execution cycle
#    - Configurable output limits (out_min / out_max)
# ─────────────────────────────────────────────────────────────────────────────
class PIDController:
    def __init__(self, Kp: float, Ki: float, Kd: float,
                 out_min: float = 0.0, out_max: float = 100.0):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.out_min = out_min
        self.out_max = out_max

        self._integral   = 0.0   # Integral accumulator [error × s]
        self._prev_error = 0.0   # Error value from previous scan cycle
        self._first_scan = True  # First-scan flag — suppresses derivative kick

    def compute(self, setpoint: float, process_value: float, dt: float) -> float:
        """
        Execute one PID scan cycle.

        Args:
            setpoint      : Desired process value (SP) [bar]
            process_value : Measured process variable (PV) [bar]
            dt            : Scan cycle time [s]

        Returns:
            control_output: Manipulated variable (MV) sent to final control element [%]
        """
        # Control deviation: e(t) = SP - PV
        error = setpoint - process_value

        # --- Proportional term ---
        P_term = self.Kp * error

        # --- Integral term (pre-accumulation before anti-windup check) ---
        self._integral += error * dt
        I_term = self.Ki * self._integral

        # --- Derivative term (error-based, not PV-based) ---
        # Suppress derivative kick on first scan cycle to avoid
        # a large transient output on controller enable
        if self._first_scan:
            D_term = 0.0
            self._first_scan = False
        else:
            D_term = self.Kd * (error - self._prev_error) / dt

        self._prev_error = error

        # --- Raw controller output ---
        output = P_term + I_term + D_term

        # --- Anti-windup: back-calculation method ---
        # If the output is saturated, undo the most recent integral increment
        # to prevent integrator wind-up (ISA recommended practice)
        if output > self.out_max:
            self._integral -= error * dt   # Revert last integration step
            output = self.out_max
        elif output < self.out_min:
            self._integral -= error * dt
            output = self.out_min

        return output

    @property
    def terms(self):
        """Return the last computed P, I, D contributions (approximate)."""
        return (self.Kp * self._prev_error,
                self.Ki * self._integral,
                self.Kd * self._prev_error)


# ─────────────────────────────────────────────────────────────────────────────
#  PUMP + PIPING SYSTEM PROCESS MODEL
#
#  Transfer function (s-domain):  G(s) = Kp_plant / (tau·s + 1)
#  Discretized via forward Euler:  P[k] = P[k-1] + (dt/tau) · (Kp_plant·u - P[k-1])
#
#  Includes:
#    - Actuator deadband (minimum pump speed threshold)
#    - Physical output limits (0–10 bar)
#    - Additive Gaussian measurement noise (sensor simulation)
# ─────────────────────────────────────────────────────────────────────────────
class PumpSystem:
    def __init__(self, Kp_plant: float = 0.8, tau: float = 3.0,
                 deadband: float = 2.0, noise_amp: float = 0.03):
        self.Kp_plant  = Kp_plant   # Plant static gain [bar / %output]
        self.tau       = tau        # Process time constant [s]
        self.deadband  = deadband   # Minimum control output to start pump [%]
        self.noise_amp = noise_amp  # Measurement noise standard deviation [bar]
        self.pressure  = 0.0        # Internal process state [bar]

    def update(self, control_output: float, dt: float) -> float:
        """
        Advance the process model by one time step.

        Args:
            control_output : Manipulated variable from PID controller [%]
            dt             : Integration step size [s]

        Returns:
            measured_pv : Simulated transmitter reading with additive noise [bar]
        """
        # Actuator deadband: pump does not respond below minimum output threshold
        effective = control_output if control_output >= self.deadband else 0.0

        # First-order lag dynamics — Euler forward integration
        dp = (dt / self.tau) * (self.Kp_plant * effective - self.pressure)
        self.pressure += dp

        # Enforce physical process limits (0 bar floor, 10 bar ceiling)
        self.pressure = max(0.0, min(self.pressure, 10.0))

        # Add Gaussian white noise to simulate pressure transmitter measurement
        import random
        measured = self.pressure + random.gauss(0, self.noise_amp)
        return max(0.0, measured)


# ─────────────────────────────────────────────────────────────────────────────
#  TERMINAL DISPLAY UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
BLUE   = "\033[94m"


def pressure_bar(pv: float, sp: float, width: int = 30) -> str:
    """
    Render an ASCII bar chart for process variable vs. setpoint.
    Color-coded by control deviation:
      Green  : |e| < 0.1 bar  (within tight band)
      Yellow : |e| < 0.5 bar  (within acceptable band)
      Red    : |e| >= 0.5 bar (outside acceptable band)
    """
    ratio  = min(pv / 10.0, 1.0)
    filled = int(ratio * width)
    sp_pos = int((sp / 10.0) * width)

    bar = list("░" * width)
    for i in range(filled):
        bar[i] = "█"
    if 0 <= sp_pos < width:
        bar[sp_pos] = "|"   # Setpoint marker

    err   = abs(pv - sp)
    color = GREEN if err < 0.1 else (YELLOW if err < 0.5 else RED)
    return f"{color}[{''.join(bar)}]{RESET}"


def output_bar(out: float, width: int = 20) -> str:
    """Render an ASCII bar chart for controller output (MV) percentage."""
    filled = int((out / 100.0) * width)
    return f"{CYAN}[{'█' * filled}{'░' * (width - filled)}]{RESET}"


def header():
    """Print the simulation table header with column labels."""
    print(f"\n{BOLD}{CYAN}{'─'*78}{RESET}")
    print(f"{BOLD}{CYAN}  PUMP PRESSURE CONTROL SYSTEM — PID SIMULATION{RESET}")
    print(f"{BOLD}{CYAN}  Kp={2.0}  Ki={0.5}  Kd={0.1}  |  Setpoint: 4.0 bar{RESET}")
    print(f"{BOLD}{CYAN}{'─'*78}{RESET}")
    print(f"  {BOLD}{'t(s)':>5}  {'PV(bar)':>8}  {'SP(bar)':>8}  {'Error':>7}  "
          f"{'Out(%)':>9}  {'P-term':>7}  {'I-term':>7}  {'D-term':>7}{RESET}")
    print(f"  {'─'*5}  {'─'*8}  {'─'*8}  {'─'*7}  {'─'*9}  {'─'*7}  {'─'*7}  {'─'*7}")


# ─────────────────────────────────────────────────────────────────────────────
#  SIMULATION MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────
def run_simulation(
        setpoint: float = 4.0,    # Pressure setpoint [bar]
        duration: float = 30.0,   # Total simulation time [s]
        dt: float = 0.5,          # Scan cycle time [s]
        Kp: float = 2.0,
        Ki: float = 0.5,
        Kd: float = 0.1,
        realtime: bool = False,   # If True, pause dt seconds between scans
):
    pid   = PIDController(Kp, Ki, Kd, out_min=0.0, out_max=100.0)
    plant = PumpSystem(Kp_plant=0.8, tau=3.0)

    steps  = int(duration / dt)
    t      = 0.0
    output = 0.0   # Initial manipulated variable (MV) = 0%

    header()

    history_pv  = []   # PV history for performance metrics
    history_out = []   # MV history

    for step in range(steps + 1):
        # Update process model with current MV, obtain new PV measurement
        pv     = plant.update(output, dt)
        output = pid.compute(setpoint, pv, dt)
        error  = setpoint - pv

        # Reconstruct individual PID terms for display (approximate)
        P = Kp * error
        I = Ki * pid._integral
        D = Kd * (error - pid._prev_error) / dt if step > 0 else 0.0

        history_pv.append(pv)
        history_out.append(output)

        # Row color based on absolute control deviation
        abs_err   = abs(error)
        row_color = GREEN if abs_err < 0.1 else (YELLOW if abs_err < 0.5 else WHITE)

        print(f"  {row_color}{t:5.1f}  {pv:8.3f}  {setpoint:8.3f}  "
              f"{error:+7.3f}  {output:9.2f}  {P:+7.3f}  {I:+7.3f}  {D:+7.3f}{RESET}")

        # Render bar charts every two scan cycles to reduce output density
        if step % 2 == 0:
            pbar = pressure_bar(pv, setpoint)
            obar = output_bar(output)
            print(f"         PV {pbar} {pv:.2f} bar   MV {obar} {output:.1f}%")

        t += dt
        if realtime:
            time.sleep(dt)

    # --- Performance metrics (ISA standard definitions) ---
    steady_pv = sum(history_pv[-10:]) / 10   # Average of last 10 samples
    overshoot = max(history_pv) - setpoint   # Peak overshoot [bar]

    # Settling time: first index where PV stays within ±5% of SP for 10 consecutive scans
    settling = next(
        (i * dt for i, v in enumerate(history_pv)
         if abs(v - setpoint) < 0.05 * setpoint and
         all(abs(history_pv[j] - setpoint) < 0.05 * setpoint
             for j in range(i, min(i + 10, len(history_pv))))),
        None
    )

    print(f"\n{BOLD}{CYAN}{'─'*78}{RESET}")
    print(f"{BOLD}  PERFORMANCE SUMMARY{RESET}")
    print(f"  Steady-state process value : {steady_pv:.3f} bar")
    print(f"  Steady-state error (offset): {abs(steady_pv - setpoint):.3f} bar "
          f"({abs(steady_pv - setpoint)/setpoint*100:.1f}%)")
    print(f"  Peak overshoot             : {max(overshoot, 0):.3f} bar "
          f"({max(overshoot, 0)/setpoint*100:.1f}%)")
    if settling:
        print(f"  Settling time (±5% band)   : {settling:.1f} s")
    else:
        print(f"  Settling time              : {RED}>30 s (not yet settled){RESET}")
    print(f"{BOLD}{CYAN}{'─'*78}{RESET}\n")


if __name__ == "__main__":
    run_simulation(realtime=False)
