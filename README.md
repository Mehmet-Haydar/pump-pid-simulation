# Pumpendruckregelung — PID-Simulation & TIA Portal SCL
### Pump Pressure Control — PID Simulation & TIA Portal SCL

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![SCL](https://img.shields.io/badge/TIA_Portal-V17%2B-orange)
![Standard](https://img.shields.io/badge/Standard-IEC_61131--3_|_ISA--5.1-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Projektbeschreibung

Dieses Projekt demonstriert die vollständige Entwicklungskette eines industriellen
Regelkreises — von der mathematischen Simulation bis zum produktionsfähigen PLC-Code.

**Aufgabe:** Druckregelung einer Pumpenanlage mittels PID-Algorithmus.
Das System regelt den Prozessdruck auf einen Sollwert von **4,0 bar**,
ausgehend von einem Anfangsdruck von 0 bar.

Das Projekt ist in zwei Schichten aufgebaut:

| Schicht | Datei | Zweck |
|---|---|---|
| Simulation | `pump_pid.py` | Validierung des PID-Verhaltens und der Systemdynamik vor der SPS-Implementierung |
| Produktion | `pump_pid_TIA.scl` | Produktionsfähiger IEC 61131-3 SCL-Code für Siemens S7-1200/1500 |

---

## Regelparameter

| Parameter | Wert | Beschreibung |
|---|---|---|
| Sollwert (SP) | 4,0 bar | Betriebsdruck |
| Anfangsdruck | 0,0 bar | Systemstart |
| Kp | 1,2 | Proportionalverstärkung |
| Ki | 0,5 | Integralverstärkung [1/s] |
| Kd | 0,1 | Differentialverstärkung [s] |
| Systemzeitkonstante τ | 3,0 s | Anlagenmodell (1. Ordnung) |
| Einschwingzeit (±5%) | ~8 s | Gemessen in der Simulation |
| Stationäre Abweichung | < 1% | Dank I-Anteil |
| Überschwingen | 0% | Gut gedämpfte Einstellung |

---

## Verwendete Technologien

- **Python 3.8+** — keine externen Bibliotheken erforderlich
- **Siemens TIA Portal V17+** — für SCL-Import
- **IEC 61131-3 SCL** — strukturierter Textcode
- **ISA-5.1 / ISA-18.2** — Terminologie und Alarmphilosophie

---

## Python-Simulation — Schnellstart

```bash
# Repository klonen
git clone https://github.com/Mehmet-Haydar/pump-pid-simulation.git
cd pump-pid-simulation

# Simulation starten (keine Installation erforderlich)
python3 pump_pid.py
```

**Beispielausgabe:**

```
──────────────────────────────────────────────────────────────────────────────
  PUMP PRESSURE CONTROL SYSTEM — PID SIMULATION
  Kp=1.2  Ki=0.5  Kd=0.1  |  Setpoint: 4.0 bar
──────────────────────────────────────────────────────────────────────────────
   t(s)   PV(bar)   SP(bar)   Error     Out(%)   P-term   I-term   D-term
    0.0     0.000     4.000   +4.000      5.80   +4.800   +1.000   +0.000
    5.0     3.560     4.000   +0.440      5.20   ...
   10.5     4.000     4.000   -0.000      5.00   ...

  PERFORMANCE SUMMARY
  Steady-state error  : 0.012 bar (0.3%)
  Peak overshoot      : 0.000 bar (0.0%)
  Settling time (±5%) : 8.0 s
```

Farbkodierung: **Rot** |e| ≥ 0,5 bar | **Gelb** |e| < 0,5 bar | **Grün** |e| < 0,1 bar

---

## Softwarearchitektur (Python)

```
pump_pid.py
│
├── PIDController                    Regelalgorithmus
│   ├── compute(sp, pv, dt)          Berechnung P + I + D
│   ├── Anti-Windup                  Back-Calculation-Methode (ISA-Standard)
│   └── Derivative-Spike-Schutz      D = 0 im ersten Abtastzyklus
│
├── PumpSystem                       Prozessmodell (Strecke)
│   ├── 1. Ordnung G(s) = K/(τs+1)   Euler-Vorwärtsintegration
│   ├── Totband (Deadband)            Minimale Pumpendrehzahl
│   └── Messgauschen                  σ = 0,03 bar (Transmitter-Simulation)
│
└── run_simulation()                 Hauptschleife + Terminalvisualisierung
    └── Leistungskennwerte           Einschwingzeit, Überschwingen, SSE
```

---

## TIA Portal — Import-Anleitung

### Schritt 1 — Neues Projekt anlegen
1. TIA Portal V17+ öffnen → **Neues Projekt**
2. SPS hinzufügen: `S7-1200` oder `S7-1500`

### Schritt 2 — SCL-Funktionsbaustein anlegen
1. **Programmbausteine** → **Neuen Baustein hinzufügen**
2. Typ: `Funktionsbaustein (FB)`, Sprache: `SCL`
3. Nummer: `FB100`, Name: `PumpPressureControl`

### Schritt 3 — Code einfügen
1. `pump_pid_TIA.scl` in einem Texteditor öffnen
2. Den FB-Rumpf (zwischen `BEGIN` und `END_FUNCTION_BLOCK`) kopieren
3. In den TIA Portal SCL-Editor einfügen
4. **Kompilieren** (F7) — keine Fehler erwartet

### Schritt 4 — OB35 konfigurieren
1. **OB35** (Zyklusunterbrechung) anlegen → Periode: `100 ms`
2. FB100-Aufruf aus dem SCL-Code in OB35 übertragen
3. Instanz-DB wird automatisch erzeugt: `PumpPressureControl_DB`

### Schritt 5 — E/A-Verschaltung

| SCL-Tag | Physikalische Adresse | Beschreibung |
|---|---|---|
| `DB_IO.AI_pressure_bar` | `%IW64` (skaliert) | Drucktransmitter 4–20 mA |
| `DB_IO.AO_pump_raw` | `%QW64` | FU-Frequenzreferenz |
| `DB_HMI.pressure_setpoint` | HMI-Tag | Bediener-Sollwert |
| `DB_HMI.pump_enable` | HMI-Tag | Start/Stop |

> **Hinweis:** AI-Skalierung: 0 = 0 bar, 27648 = 10 bar (Siemens-Standard 16-Bit)

---

## SCL-Besonderheiten

| Funktion | Beschreibung |
|---|---|
| Bumpless Transfer | Integral-Vorladung bei Manuell→Auto-Umschaltung |
| PV-Validierung | Fehlerausgang bei Transmitterwert außerhalb [-0,5 … 15 bar] |
| Alarmverzögerung | 500 ms Entprellung (5 Zyklen) gegen Fehlauslösungen |
| AO-Skalierung | `0–100% → 0–27648` für Siemens-Analogausgangsmodul |
| Status-WORD | Bit-kodierter Zustandsregister für HMI/SCADA |

---

## Projektstruktur

```
pump-pid/
├── pump_pid.py          Python-Simulation (PID + Prozessmodell + Visualisierung)
├── pump_pid_TIA.scl     TIA Portal SCL-Quellcode (FB100 + OB35)
├── README.md            Diese Datei (Deutsch — Hauptdokumentation)
├── README_EN.md         English documentation
└── README_TR.md         Türkçe dokümantasyon
```

---

## Autor

**Mehmet Haydar**
I&C Automation Engineer — Germany
[github.com/Mehmet-Haydar](https://github.com/Mehmet-Haydar)

---

*Teil eines industriellen Automatisierungs-Portfolios*
*Python-Simulation → PLC-Produktionscode (IEC 61131-3 SCL)*

Lizenz: MIT
