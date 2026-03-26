# Pump Pressure Control — PID Simulation & TIA Portal SCL
### Pompa Basınç Kontrol Sistemi — PID Simülasyonu & TIA Portal SCL

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![SCL](https://img.shields.io/badge/TIA_Portal-V17%2B-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Domain](https://img.shields.io/badge/Domain-Industrial_Automation-red)

---

## TR — Türkçe

### Proje Hakkında

Bu proje, endüstriyel bir pompa sisteminin basınç kontrolünü **PID algoritması** ile gerçekleştiren iki katmanlı bir otomasyon çalışmasıdır:

1. **Python Simülasyonu** — PID davranışını, sistem dinamiğini ve anti-windup mekanizmasını doğrulamak için
2. **TIA Portal SCL Kodu** — Aynı mantığın Siemens S7-1200/1500 PLC'lerde doğrudan çalışacak şekilde yazılmış üretim kalitesinde implementasyonu

Otomasyon mühendisliği portföyü kapsamında, yazılım simülasyonundan PLC koduna geçişin birebir nasıl yapıldığını göstermek amacıyla hazırlanmıştır.

### Sistem Parametreleri

| Parametre | Değer |
|---|---|
| Setpoint | 4.0 bar |
| Başlangıç basıncı | 0.0 bar |
| Kp (Oransal) | 1.2 |
| Ki (İntegral) | 0.5 |
| Kd (Türevsel) | 0.1 |
| Sistem zaman sabiti (τ) | 3.0 s |
| Yerleşme süresi (±5%) | ~8 s |
| Steady-state hatası | < 1% |

### Python Simülasyonu Nasıl Çalıştırılır?

**Gereksinimler:** Python 3.8+ (harici kütüphane gerekmez)

```bash
# Depoyu klonla
git clone https://github.com/KULLANICI_ADI/pump-pid-control.git
cd pump-pid-control

# Simülasyonu başlat
python3 pump_pid.py
```

**Terminal çıktısı:**

```
──────────────────────────────────────────────────────────────────────────────
  POMPA BASINÇ KONTROL SİSTEMİ — PID SİMÜLASYONU
  Kp=1.2  Ki=0.5  Kd=0.1  |  Setpoint: 4.0 bar
──────────────────────────────────────────────────────────────────────────────
   t(s)   PV(bar)   SP(bar)     Hata   Çıkış(%)   P-term   I-term   D-term
  ─────  ────────  ────────  ───────  ─────────  ───────  ───────  ───────
    0.0     0.000     4.000   +4.000       5.80   +4.800   +1.000   +0.000
    0.5     0.797     4.000   +3.203       5.48   +3.843   +1.801   +0.000
    ...
   10.5     4.000     4.000   -0.000       5.00   -0.000   +5.010   +0.000
```

Renk kodlaması: **Kırmızı** > 0.5 bar hata | **Sarı** 0.1–0.5 bar | **Yeşil** < 0.1 bar

### Python Kod Mimarisi

```
pump_pid.py
│
├── PIDController          — PID hesaplama motoru
│   ├── compute()          — P + I + D terimleri
│   ├── Anti-windup        — Back-calculation yöntemi
│   └── Türev spike koruması — İlk scan D=0
│
├── PumpSystem             — Fiziksel süreç modeli
│   ├── 1. derece sistem   — Euler ayrıklaştırma
│   ├── Deadband           — Pompa min. devir eşiği
│   └── Ölçüm gürültüsü    — Gaussian (σ=0.03 bar)
│
└── run_simulation()       — Ana döngü + terminal görselleştirme
```

### TIA Portal'a Nasıl Import Edilir?

#### Adım 1 — Yeni Proje Oluştur
1. TIA Portal V17+ aç → **New Project**
2. PLC ekle: `S7-1200` veya `S7-1500`

#### Adım 2 — SCL Bloğunu Ekle
1. **Program blocks** → **Add new block**
2. Tip: `Function Block (FB)`, Dil: `SCL`
3. Numara: `FB100`, İsim: `PumpPressureControl`

#### Adım 3 — Kodu Yapıştır
1. `pump_pid_TIA.scl` dosyasını metin editörüyle aç
2. **FB100 gövdesi** bölümünü kopyala
3. TIA Portal SCL editörüne yapıştır
4. **Compile** (F7)

#### Adım 4 — OB35 Konfigürasyonu
1. **OB35** (Cyclic Interrupt) oluştur → Periyot: `100 ms`
2. FB100 çağrısını OB35'e ekle (SCL dosyasındaki OB35 bölümünden)
3. Instance DB otomatik oluşturulur: `PumpPressureControl_DB`

#### Adım 5 — Tag Bağlantıları
| SCL Tag | Fiziksel Adres | Açıklama |
|---|---|---|
| `DB_IO.AI_pressure_bar` | `%IW64` (ölçekli) | Basınç transmitteri 4–20 mA |
| `DB_IO.AO_pump_raw` | `%QW64` | VFD frekans referansı |
| `DB_HMI.pressure_setpoint` | HMI tag | Operatör setpoint |
| `DB_HMI.pump_enable` | HMI tag | Start/Stop |

> **Not:** AI ölçekleme: 0 = 0 bar, 27648 = 10 bar (Siemens standart)

### Dosya Yapısı

```
pump-pid/
├── pump_pid.py          # Python PID simülasyonu
├── pump_pid_TIA.scl     # TIA Portal SCL kaynak kodu (FB100 + OB35)
└── README.md            # Bu dosya
```

---

## EN — English

### About This Project

A two-layer industrial automation project implementing pressure control for a pump system using a **PID algorithm**:

1. **Python Simulation** — Validates PID behavior, system dynamics, and anti-windup mechanism before deployment
2. **TIA Portal SCL Code** — Production-ready implementation of the same logic for Siemens S7-1200/1500 PLCs

Developed as part of an automation engineering portfolio to demonstrate the translation from software simulation to PLC code.

### System Parameters

| Parameter | Value |
|---|---|
| Setpoint | 4.0 bar |
| Initial pressure | 0.0 bar |
| Kp (Proportional) | 1.2 |
| Ki (Integral) | 0.5 |
| Kd (Derivative) | 0.1 |
| Plant time constant (τ) | 3.0 s |
| Settling time (±5%) | ~8 s |
| Steady-state error | < 1% |

### Running the Python Simulation

**Requirements:** Python 3.8+ (no external libraries needed)

```bash
git clone https://github.com/USERNAME/pump-pid-control.git
cd pump-pid-control
python3 pump_pid.py
```

The terminal output shows timestamped pressure values, PID terms (P/I/D), control output percentage, and a live ASCII bar chart with color-coded error bands.

### Python Architecture

```
PIDController
├── compute(setpoint, pv, dt) → control output [0–100%]
├── Anti-windup: back-calculation (clamps integral on saturation)
└── Derivative spike protection: D=0 on first scan

PumpSystem (1st-order process model)
├── dp/dt = (Kp_plant × u − P) / τ   [Euler discretization]
├── Deadband: pump inactive below 2% output
└── Measurement noise: Gaussian σ=0.03 bar
```

### Importing to TIA Portal

1. Create a new TIA Portal V17+ project with S7-1200 or S7-1500
2. Add new block: `FB100 — PumpPressureControl`, language: SCL
3. Paste the FB body from `pump_pid_TIA.scl` and compile (F7)
4. Create `OB35` (Cyclic Interrupt, 100 ms), add FB100 call
5. Map `AI_pressure_bar` to your pressure transmitter tag (scaled 0–27648 = 0–10 bar)
6. Map `AO_pump_raw` to your VFD analog output

**Key SCL features implemented:**
- Bumpless Manual→Auto transfer (integral tracking)
- PV validity check (fault output on out-of-range)
- Delayed alarms (500 ms debounce, 5-scan counter)
- AO scaling: `0–100% → 0–27648` (Siemens 16-bit raw)
- Status word for HMI/SCADA (Auto/Manual/Alarm/Fault bits)

### File Structure

```
pump-pid/
├── pump_pid.py          # Python PID simulation
├── pump_pid_TIA.scl     # TIA Portal SCL source (FB100 + OB35)
└── README.md            # This file
```

### Skills Demonstrated

- Discrete-time PID implementation from scratch (no libraries)
- Anti-windup (back-calculation method)
- 1st-order process modeling with Euler discretization
- IEC 61131-3 SCL programming for Siemens TIA Portal
- Bumpless transfer between manual and automatic modes
- Industrial alarm management with debounce logic

---

## License

MIT License — free to use for educational and portfolio purposes.

---

*Part of an Industrial Automation Engineering Portfolio*
*Python Simulation → PLC Production Code*
