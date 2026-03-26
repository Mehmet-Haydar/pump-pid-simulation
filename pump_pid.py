#!/usr/bin/env python3
"""
Pompa Basınç Kontrol Sistemi — PID Simülasyonu
Setpoint: 4 bar | P=1.2  I=0.5  D=0.1
Pompa modeli: 1. derece gecikme sistemi (tau=3s, Kp=0.8)
"""

import time

# ─────────────────────────────────────────────
#  PID Kontrolör
# ─────────────────────────────────────────────
class PIDController:
    def __init__(self, Kp: float, Ki: float, Kd: float,
                 out_min: float = 0.0, out_max: float = 100.0):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.out_min = out_min
        self.out_max = out_max

        self._integral   = 0.0
        self._prev_error = 0.0
        self._first_scan = True

    def compute(self, setpoint: float, process_value: float, dt: float) -> float:
        error = setpoint - process_value

        # Proportional
        P_term = self.Kp * error

        # Integral (anti-windup: sadece çıkış saturasyonda değilse)
        self._integral += error * dt
        I_term = self.Ki * self._integral

        # Derivative (ilk scan'de türev spike'ı önle)
        if self._first_scan:
            D_term = 0.0
            self._first_scan = False
        else:
            D_term = self.Kd * (error - self._prev_error) / dt

        self._prev_error = error

        output = P_term + I_term + D_term

        # Anti-windup: çıkış sınırı aşıldıysa integral'i geri al
        if output > self.out_max:
            self._integral -= error * dt   # son adımı iptal et
            output = self.out_max
        elif output < self.out_min:
            self._integral -= error * dt
            output = self.out_min

        return output

    @property
    def terms(self):
        return (self.Kp * self._prev_error,
                self.Ki * self._integral,
                self.Kd * self._prev_error)   # son hesaplanan


# ─────────────────────────────────────────────
#  Pompa + Boru Sistemi Modeli
#  1. Derece Transfer Fonksiyonu: G(s) = Kp_plant / (tau*s + 1)
#  Euler ayrıklaştırma: P[k] = P[k-1] + dt/tau * (Kp_plant*u - P[k-1])
# ─────────────────────────────────────────────
class PumpSystem:
    def __init__(self, Kp_plant: float = 0.8, tau: float = 3.0,
                 deadband: float = 2.0, noise_amp: float = 0.03):
        self.Kp_plant  = Kp_plant
        self.tau       = tau
        self.deadband  = deadband      # pompanın devreye girdiği min çıkış (%)
        self.noise_amp = noise_amp     # ölçüm gürültüsü (bar)
        self.pressure  = 0.0

    def update(self, control_output: float, dt: float) -> float:
        # Deadband: çıkış çok küçükse pompa dönmez
        effective = control_output if control_output >= self.deadband else 0.0

        # 1. derece sistem dinamiği
        dp = (dt / self.tau) * (self.Kp_plant * effective - self.pressure)
        self.pressure += dp

        # Basınç fiziksel sınırları
        self.pressure = max(0.0, min(self.pressure, 10.0))

        # Ölçüm gürültüsü (sensor simülasyonu)
        import random
        measured = self.pressure + random.gauss(0, self.noise_amp)
        return max(0.0, measured)


# ─────────────────────────────────────────────
#  Renk & Çizim Araçları
# ─────────────────────────────────────────────
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
    ratio  = min(pv / 10.0, 1.0)
    filled = int(ratio * width)
    sp_pos = int((sp / 10.0) * width)

    bar = list("░" * width)
    for i in range(filled):
        bar[i] = "█"
    if 0 <= sp_pos < width:
        bar[sp_pos] = "|"

    err = abs(pv - sp)
    color = GREEN if err < 0.1 else (YELLOW if err < 0.5 else RED)
    return f"{color}[{''.join(bar)}]{RESET}"

def output_bar(out: float, width: int = 20) -> str:
    filled = int((out / 100.0) * width)
    return f"{CYAN}[{'█' * filled}{'░' * (width - filled)}]{RESET}"

def header():
    print(f"\n{BOLD}{CYAN}{'─'*78}{RESET}")
    print(f"{BOLD}{CYAN}  POMPA BASINÇ KONTROL SİSTEMİ — PID SİMÜLASYONU{RESET}")
    print(f"{BOLD}{CYAN}  Kp={1.2}  Ki={0.5}  Kd={0.1}  |  Setpoint: 4.0 bar{RESET}")
    print(f"{BOLD}{CYAN}{'─'*78}{RESET}")
    print(f"  {BOLD}{'t(s)':>5}  {'PV(bar)':>8}  {'SP(bar)':>8}  {'Hata':>7}  "
          f"{'Çıkış(%)':>9}  {'P-term':>7}  {'I-term':>7}  {'D-term':>7}{RESET}")
    print(f"  {'─'*5}  {'─'*8}  {'─'*8}  {'─'*7}  {'─'*9}  {'─'*7}  {'─'*7}  {'─'*7}")


# ─────────────────────────────────────────────
#  Simülasyon
# ─────────────────────────────────────────────
def run_simulation(
        setpoint: float = 4.0,
        duration: float = 30.0,
        dt: float = 0.5,
        Kp: float = 1.2,
        Ki: float = 0.5,
        Kd: float = 0.1,
        realtime: bool = False,
):
    pid    = PIDController(Kp, Ki, Kd, out_min=0.0, out_max=100.0)
    plant  = PumpSystem(Kp_plant=0.8, tau=3.0)

    steps  = int(duration / dt)
    t      = 0.0
    output = 0.0

    header()

    history_pv  = []
    history_out = []

    for step in range(steps + 1):
        pv     = plant.update(output, dt)
        output = pid.compute(setpoint, pv, dt)
        error  = setpoint - pv

        # PID terimleri (yaklaşık)
        P = Kp * error
        I = Ki * pid._integral
        D = Kd * (error - pid._prev_error) / dt if step > 0 else 0.0

        history_pv.append(pv)
        history_out.append(output)

        # Satır rengi
        abs_err = abs(error)
        row_color = GREEN if abs_err < 0.1 else (YELLOW if abs_err < 0.5 else WHITE)

        print(f"  {row_color}{t:5.1f}  {pv:8.3f}  {setpoint:8.3f}  "
              f"{error:+7.3f}  {output:9.2f}  {P:+7.3f}  {I:+7.3f}  {D:+7.3f}{RESET}")

        # Görsel çubuklar (her 2 adımda bir)
        if step % 2 == 0:
            pbar = pressure_bar(pv, setpoint)
            obar = output_bar(output)
            print(f"         Basınç {pbar} {pv:.2f} bar   Çıkış {obar} {output:.1f}%")

        t += dt
        if realtime:
            time.sleep(dt)

    # Özet
    steady_pv = sum(history_pv[-10:]) / 10
    overshoot = max(history_pv) - setpoint
    settling  = next((i * dt for i, v in enumerate(history_pv)
                      if abs(v - setpoint) < 0.05 * setpoint and
                      all(abs(history_pv[j] - setpoint) < 0.05 * setpoint
                          for j in range(i, min(i + 10, len(history_pv))))), None)

    print(f"\n{BOLD}{CYAN}{'─'*78}{RESET}")
    print(f"{BOLD}  PERFORMANS ÖZETİ{RESET}")
    print(f"  Kararlı durum basıncı  : {steady_pv:.3f} bar")
    print(f"  Steady-state hatası    : {abs(steady_pv - setpoint):.3f} bar "
          f"({abs(steady_pv - setpoint)/setpoint*100:.1f}%)")
    print(f"  Maksimum aşım (overshoot): {max(overshoot, 0):.3f} bar "
          f"({max(overshoot,0)/setpoint*100:.1f}%)")
    if settling:
        print(f"  Yerleşme süresi (±5%)  : {settling:.1f} s")
    else:
        print(f"  Yerleşme süresi        : {RED}>30 s (henüz yerleşmedi){RESET}")
    print(f"{BOLD}{CYAN}{'─'*78}{RESET}\n")


if __name__ == "__main__":
    run_simulation(realtime=False)
