# Pompa Basınç Kontrol Sistemi — PID Simülasyonu & TIA Portal SCL

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![SCL](https://img.shields.io/badge/TIA_Portal-V17%2B-orange)
![Standard](https://img.shields.io/badge/Standart-IEC_61131--3_|_ISA--5.1-lightgrey)
![License](https://img.shields.io/badge/Lisans-MIT-green)

---

## Proje Hakkında

Bu proje, endüstriyel bir pompa basınç kontrol döngüsünün matematiksel simülasyondan
üretim kalitesinde PLC koduna geliştirme sürecinin tamamını kapsamaktadır.

**Amaç:** Başlangıç basıncı 0 bar olan bir pompa sisteminde, ayrık zamanlı PID algoritması
ile işlem basıncını **4,0 bar** setpointe düzenlemek.

Proje iki katmandan oluşmaktadır:

| Katman | Dosya | Amaç |
|---|---|---|
| Simülasyon | `pump_pid.py` | PLC'ye geçmeden önce PID davranışını ve sistem dinamiğini doğrulama |
| Üretim | `pump_pid_TIA.scl` | Siemens S7-1200/1500 için IEC 61131-3 SCL kodu |

---

## Kontrol Döngüsü Parametreleri

| Parametre | Değer | Açıklama |
|---|---|---|
| Setpoint (SP) | 4,0 bar | Çalışma basıncı |
| Başlangıç PV | 0,0 bar | Sistem başlangıç koşulu |
| Kp | 1,2 | Oransal kazanç |
| Ki | 0,5 | İntegral kazanç [1/s] |
| Kd | 0,1 | Türevsel kazanç [s] |
| Süreç zaman sabiti τ | 3,0 s | 1. derece sistem modeli |
| Yerleşme süresi (±%5) | ~8 s | Simülasyonda ölçüldü |
| Kararlı durum hatası | < %1 | İntegral terim sayesinde |
| Maksimum aşım | %0 | İyi sönümlenmiş ayar |

---

## Kullanılan Teknolojiler

- **Python 3.8+** — harici kütüphane gerektirmez
- **Siemens TIA Portal V17+** — SCL import ve PLC devreye alma
- **IEC 61131-3 SCL** — yapılandırılmış metin programlama dili
- **ISA-5.1 / ISA-18.2** — enstrümantasyon terminolojisi ve alarm felsefesi

---

## Python Simülasyonu — Çalıştırma

```bash
git clone https://github.com/Mehmet-Haydar/pump-pid-simulation.git
cd pump-pid-simulation
python3 pump_pid.py
```

Terminal çıktısı; zaman damgalı PV, SP, kontrol sapması, kontrolör çıkışı ve
ayrı P/I/D katkılarını içeren bir tablo görüntüler. Renk kodlu ASCII çubuk
grafikler, kontrol yanıtının canlı görünümünü sağlar.

**Renk kodlaması:** Kırmızı |e| ≥ 0,5 bar | Sarı |e| < 0,5 bar | Yeşil |e| < 0,1 bar

---

## Python Kod Mimarisi

```
PIDController
├── compute(setpoint, pv, dt) → MV [%]
├── Anti-windup: back-calculation (son integral adımı geri alınır)
└── Türev spike koruması: İlk çalışma döngüsünde D = 0

PumpSystem  (1. derece süreç modeli)
├── G(s) = Kp_plant / (τs + 1)  →  Euler ileri integrasyon
├── Aktüatör deadband: MV < %2 iken pompa çalışmaz
└── Gaussian ölçüm gürültüsü: σ = 0,03 bar (transmitter simülasyonu)

run_simulation()
└── Performans metrikleri: yerleşme süresi, aşım, kararlı durum hatası
```

---

## TIA Portal Import Talimatı

### Adım 1 — Proje Oluşturma
TIA Portal V17+ aç → Yeni Proje → S7-1200 veya S7-1500 PLC ekle.

### Adım 2 — SCL Fonksiyon Bloğu Ekleme
Programlama blokları → Yeni blok ekle → Fonksiyon Bloğu (FB), Dil: SCL,
Numara: FB100, İsim: `PumpPressureControl`.

### Adım 3 — Kodu Yapıştırma
`pump_pid_TIA.scl` dosyasını aç, FB gövdesini kopyala, TIA Portal SCL
editörüne yapıştır, ardından F7 ile derle.

### Adım 4 — OB35 Yapılandırması
OB35 (Döngüsel Kesme, periyot: 100 ms) oluştur. SCL dosyasındaki FB100
çağrısını OB35'e ekle. Instance DB otomatik oluşturulur: `PumpPressureControl_DB`.

### Adım 5 — I/O Bağlantıları

| SCL Etiketi | Fiziksel Adres | Açıklama |
|---|---|---|
| `DB_IO.AI_pressure_bar` | `%IW64` (ölçekli) | Basınç transmitteri 4–20 mA |
| `DB_IO.AO_pump_raw` | `%QW64` | VFD hız referans çıkışı |
| `DB_HMI.pressure_setpoint` | HMI etiketi | Operatör setpointi |
| `DB_HMI.pump_enable` | HMI etiketi | Start/Stop |

> AI ölçekleme: ham 0 = 0 bar, ham 27648 = 10 bar (Siemens 16-bit standardı)

---

## SCL Implementasyon Özellikleri

| Özellik | Açıklama |
|---|---|
| Bumpless transfer | Manuel→Oto geçişinde integral ön yükleme |
| PV doğrulama | Transmitter menzil dışında ise arıza çıkışı |
| Alarm gecikme | 500 ms bekleme (5 tarama) — yanlış alarm önleme |
| AO ölçekleme | `0–%100 → 0–27648` Siemens analog çıkış modülü için |
| Durum WORD'ü | HMI/SCADA için bit kodlu durum kaydı |

---

## Dosya Yapısı

```
pump-pid/
├── pump_pid.py       Python PID simülasyonu
├── pump_pid_TIA.scl  TIA Portal SCL kaynak kodu (FB100 + OB35)
├── README.md         Almanca dokümantasyon (ana dosya)
├── README_EN.md      İngilizce dokümantasyon
└── README_TR.md      Bu dosya
```

---

## Yazar

**Mehmet Haydar**
I&C Otomasyon Mühendisi — Almanya
[github.com/Mehmet-Haydar](https://github.com/Mehmet-Haydar)

---

*Endüstriyel Otomasyon Mühendisliği Portföyünün Bir Parçası*
*Python Simülasyonu → PLC Üretim Kodu (IEC 61131-3 SCL)*

Lisans: MIT
