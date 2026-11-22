# BMW E46 320d (M47TÜ) — Bosch EDC16C31 (`SW 1037361858`) ECU Calibration, TunerPro XDF & Map Pack

**Vehicle / Engine:** BMW E46 320d 2.0d (`M47TÜ` / `M47D20O1`, 150 HP / 110 kW stock, 4-cyl 16V Common-Rail)  
**ECU:** Bosch **EDC16C31** (`DDE 5.0` / `DDE5`) — 1 MB Flash (`1,048,576` bytes, Big-Endian 16-bit)  
**Software / Calibration ID:** Bosch SW `1037361858` (`10373618581974842A`) | BMW Cal ID `O_U6K482` (`0001970048020KU60`)  
**Target Hardware Setup:**
- Bosch CP3 **R70** High-Pressure Fuel Pump (`0 445 010 070` / `0445010070`)
- Bosch **0 445 110 216** (`0445110216`) Upgrade Injectors *(replacing stock `0 445 110 131` / `0445110131`)*
- **Hybrid Turbocharger** (VNT / N75 geometry calibrated)
- **GM 5L40-E** (`A5S390R`) 5-Speed Automatic Transmission (TCC lock-up & per-gear torque protection)
- Stock **3-Bar MAP Sensor** (`3000 mbar` absolute limit) & Stock **1800-Bar Rail Pressure Sensor** (`1650 bar` operating ceiling)

---

## ECU Torque, Estimated Dyno Power & Calibration Charts

![BMW E46 320d ECU Torque & Estimated Output Curves](./docs/dyno_curves.png)

> **Note:** ECU Torque values (`Nm`) are read directly from the active ECU torque limiters (`min(0x0E6DC2, 0x0E6E6A, 0x0E6F1A, 0x0E0672)`). Crank Power (`HP`) is estimated using an M47TÜ friction loss baseline calibrated to the factory 150 HP @ 4000 RPM rating and has not been measured on a physical chassis dyno.

| Engine RPM | Stock OEM Ref (ECU Nm / Est. HP) | Stage 1 (ECU Nm / Est. HP) | **Stage 2 (ECU Nm / Est. HP)** | **Stage 3 (ECU Nm / Est. HP)** | **Stage 3 + 4800 RPM Popcorn** |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1000** | 220 Nm / 28.5 HP | 315 Nm / 42.0 HP | **330 Nm / 44.1 HP** | **345 Nm / 46.3 HP** | **345 Nm / 46.3 HP** |
| **1500** | 340 Nm / 67.2 HP | 360 Nm / 71.5 HP | **375 Nm / 74.7 HP** | **390 Nm / 78.0 HP** | **390 Nm / 78.0 HP** |
| **1750** | 348 Nm / 79.8 HP | 395 Nm / 91.4 HP | **415 Nm / 96.4 HP** | **435 Nm / 101.4 HP** | **435 Nm / 101.4 HP** |
| **2000** | 358 Nm / 93.1 HP | 420 Nm / 110.8 HP | **445 Nm / 117.9 HP** | **465 Nm / 123.6 HP** | **465 Nm / 123.6 HP** |
| **2250** | 362 Nm / 105.2 HP | **440 Nm** / 130.1 HP | **475 Nm / 141.3 HP** | **495 Nm / 147.7 HP** | **495 Nm / 147.7 HP** |
| **2500** | **367 Nm** / 117.4 HP | **440 Nm** / 143.4 HP | **485 Nm / 159.5 HP** | **515 Nm / 170.1 HP** | **515 Nm / 170.1 HP** |
| **3000** | 365 Nm / 136.8 HP | 436 Nm / 167.0 HP | **482 Nm / 186.7 HP** | **512 Nm / 199.5 HP** | **512 Nm / 199.5 HP** |
| **3500** | 348 Nm / 147.3 HP | 432 Nm / 189.4 HP | **478 Nm / 212.3 HP** | **508 Nm / 227.2 HP** | **508 Nm / 227.2 HP** |
| **4000** | 322 Nm / **149.8 HP** | 423 Nm / 207.3 HP | **470 Nm / 234.1 HP** | **498 Nm / 250.0 HP** | **498 Nm / 250.0 HP** |
| **4400** | 293 Nm / 142.0 HP | 406 Nm / 213.0 HP | **448 Nm / 239.3 HP** | **476 Nm / 256.9 HP** | **476 Nm / 256.9 HP** |
| **4600** | 274 Nm / 133.9 HP | 400 Nm / **216.1 HP** | **442 Nm / 243.6 HP** | **470 Nm / 262.0 HP** | **475 Nm / 265.6 HP** |
| **4790** | 141 Nm / 45.2 HP | 307 Nm / 158.5 HP | **307 Nm / 158.5 HP** | **307 Nm / 158.5 HP** | **475 Nm / 273.0 HP** |
| **4800** | 134 Nm / 40.3 HP | 288 Nm / 145.6 HP | **288 Nm / 145.6 HP** | **288 Nm / 145.6 HP** | **0 Nm (Hardcut)** |
| **4950** | 0 Nm / 0.0 HP | 0 Nm / 0.0 HP | **0 Nm / 0.0 HP** | **0 Nm / 0.0 HP** | **0 Nm / 0.0 HP** |

### Boost Targets, GM 5L40-E Per-Gear Protection & Bosch 216 Injector Duration

![BMW E46 320d Boost, GM 5L40-E Gear Protection & Injector Duration](./docs/calibration_overview.png)

---

## Documentation & Definition Files

| File | Description |
| :--- | :--- |
| [**`BMW_E46_320d_EDC16C31_1037361858.xdf`**](BMW_E46_320d_EDC16C31_1037361858.xdf) | **TunerPro XDF Map Definition File (42 Maps/Curves/Constants)** — Byte-verified for Bosch EDC16C31 SW `1037361858` (`O_U6K482`): Driver Wish, Torque Limiters, GM 5L40-E Gear Limits, NM2IQ, 216 Injector Duration, Boost, VNT, Rail, EGR & Swirl Flaps |
| [**`BMW_E46_EDC16C31_Analysis_and_Stage_Report.md`**](BMW_E46_EDC16C31_Analysis_and_Stage_Report.md) | Complete ECU analysis of `bmw backup.bin`, engineering notes for R70 + 216 + Hybrid + GM 5L40-E, Stage 1/2/3/Popcorn specs, and WinOLS / TunerPro map address reference table |
| [**`stage2_variants/Stage2_File_Comparison.md`**](stage2_variants/Stage2_File_Comparison.md) | Byte-level comparison of the 10 experimental Stage 2/3 variant binaries against Reference Stage 2, including axis anomalies, SOI / 2nd rail boundary warnings, and checksum caveats |

---

## Stage Calibration Overview

> **Note:** Power figures below are theoretical estimates and have not been dyno-verified.

| Calibration File | Est. Power / Torque | Fueling (IQ) | Target Boost (SVBL) | Rail Limit | Lambda | Features |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`BMW_E46_320d_R70_216_Hybrid_Stage1.bin`** | ~205–210 HP / 440 Nm | ~72 mg/str | 2600 mbar (2680) | 1648.5 bar | 1.15 | 216 Duration, GM 5L40-E protection, EGR Off |
| **`BMW_E46_320d_R70_216_Hybrid_Stage2.bin`** | ~235 HP / 485 Nm | ~80 mg/str | 2680 mbar (2750) | 1655.0 bar | 1.08 | 216 Duration, Hybrid VNT, GM 5L40-E protection, EGR & Swirl Flaps Off |
| **`BMW_E46_320d_R70_216_Hybrid_Stage3.bin`** | ~255–265 HP / 515 Nm | ~88–90 mg/str | 2780 mbar (2850) | 1655.0 bar | 1.03 | 216 Duration, Full SOI & Hybrid VNT, GM 5L40-E protection, EGR & Flaps Off |
| **`BMW_E46_320d_R70_216_Hybrid_Stage3_Popcorn_4800RPM.bin`** | ~255–265 HP / 515 Nm | ~88–90 mg/str | 2780 mbar (2850) | 1655.0 bar | 1.03 | Stage 3 + synchronized `4790 → 4800 RPM` Hardcut / Popcorn |

---

## Repository Contents

### Root Calibration & Reference Binaries (`1,048,576` bytes each)

| File | MD5 Hash | Role / Notes |
| :--- | :--- | :--- |
| `BMW_E46_320d_R70_216_Hybrid_Stage1.bin` | `5c63681a2f2a92dd1d0121de6b4e0e4c` | Stage 1 calibration for R70 + 216 + Hybrid + GM 5L40-E |
| `BMW_E46_320d_R70_216_Hybrid_Stage2.bin` | `7b945c6124e0ededb2a72eb31836fc9e` | Stage 2 reference calibration for R70 + 216 + Hybrid + GM 5L40-E |
| `BMW_E46_320d_R70_216_Hybrid_Stage3.bin` | `af8e6d70defa440bd73e05a8f7eae99e` | Stage 3 calibration for R70 + 216 + Hybrid + GM 5L40-E |
| `BMW_E46_320d_R70_216_Hybrid_Stage3_Popcorn_4800RPM.bin` | `473863e9e3037357dda31f3e5af4ae46` | Stage 3 + 4800 RPM Hardcut / Popcorn |
| `bmw backup.bin` | `db288c01ac8fa701f72eb9444e85906a` | Original analyzed readout (Stage 1 + EGR Off + inflated 131 injector duration — **do not run with 216 injectors**) |
| `bmw_e46_Original SOI.bin` | `c11fbcf15ae1519b55cf4c066951248e` | Reference file with 216 injector Duration and stock SOI |

### Variant Comparison Archive (`stage2_variants/`)

Contains 10 additional Stage 2 / Stage 3 experimental binaries (`bmw_e46_stage2*.bin`, `bmw_e46_stage3*.bin`) documented in [`stage2_variants/Stage2_File_Comparison.md`](stage2_variants/Stage2_File_Comparison.md).

---

## Key Calibration Highlights

1. **True Bosch `0 445 110 216` Injector Duration (`0x0F5300 – 0x0F6D58`):** Replaces the +15% inflated `131` injector duration maps in `bmw backup.bin` (which over-fueled by ~39–40% on 216 injectors) with true 216 flow timing (`95 mg/str @ 1600 bar = 1032 µs`).
2. **GM 5L40-E Automatic Transmission Protection (`0x0E6D74`, `0x0E6E42`, `0x0E943A – 0x0E95D2`):** Activates per-gear torque limits (protecting 1st, 2nd, and 5th overdrive gears), enables TCC lock-up torque ramping between 1250–2000 RPM, and restores linear CAN-Bus NM2IQ torque reporting for the EGS.
3. **Stock Sensor Headroom:** Keeps target boost safely below the `3000 mbar` stock 3-bar MAP sensor ceiling (max `2780 mbar` target / `2850 mbar` SVBL on Stage 3) and rail pressure at `1650 bar` safely below the `1750 bar` stock overpressure cutoff.

---

## WinOLS / TunerPro Map Address Reference (`SW 1037361858` / `O_U6K482`)

| Category | Map / Function (Bosch DAMOS Name) | Data Address *(Header/Axis)* | Size | Format & Scaling |
| :--- | :--- | :--- | :---: | :--- |
| **Pedal** | Driver Wish 1 (`AccPed_trqEngLow_MAP`) | `0x0E0672` *(`0x0E063C`)* | 16x9 | 16-bit HiLo Signed, `× 0.1 = Nm` |
| **Pedal** | Driver Wish 2 (`AccPed_trqEngHigh_MAP`) | `0x0E08B6` *(`0x0E0880`)* | 16x9 | 16-bit HiLo Signed, `× 0.1 = Nm` |
| **Air / EGR** | EGR Base Map (`AirCtl_mDesBas_MAP`) | `0x0E13AE` *(`0x0E1372`)* | 12x16 | 16-bit HiLo, `× 0.1 = mg/str` |
| **Air / EGR** | EGR Hysteresis 1 & 2 (`AirCtl_qHiRgn_CUR` / `qLoRgn_CUR`) | `0x0E2A22`, `0x0E2B54` | 25x1 (x2) | 16-bit HiLo, `× 0.01 = mg/str` (`0 = EGR Off`) |
| **Air / Flaps** | Swirl Flaps (`IndSys_rVSA_MAP`) | `0x0E9EEC` *(`0x0E9EA8`)* | 16x16 | 16-bit HiLo, `× 0.01 = %` |
| **Torque** | Torque Limiter 1 (`EngPrt_trqLim_CUR`) | `0x0E66DA` *(`0x0E66AE`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque / EGS** | AT TCC Lock-Up Gear Switch (`EngPrt_swtTrqGear_CUR`) | `0x0E6D86` *(`0x0E6D74`)* | 8x1 | 16-bit HiLo, `0 = Off, 1 = Active` |
| **Torque** | Main Torque Limiter 2 (`EngPrt_trqLim1_CUR`) | `0x0E6DC2` *(`0x0E6D96`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque** | Launch Torque Limiter 3 (`EngPrt_trqLimDA_CUR`) | `0x0E6E18` *(`0x0E6DEC`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque / EGS** | AT TCC Lock-Up Torque Limiter 4 (`EngPrt_trqCBLim_CUR`) | `0x0E6E6A` *(`0x0E6E42`)* | 19x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque** | Torque Limiter 5 (`EngPrt_trqCBLim1_CUR`) | `0x0E6EC4` *(`0x0E6E98`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque / Cut** | Rev Limiter / Normal Op. Torque Limit 6 (`EngPrt_trqNLim_CUR`) | `0x0E6F1A` *(`0x0E6EEE`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **GM 5L40-E** | 1st–5th Gear Torque Limits (`Gearbx_trqMaxGear1..5_CUR`) | `0x0E945A`, `0x0E94C0`, `0x0E9526`, `0x0E958C`, `0x0E95F2` | 15x1 (x5) | 16-bit HiLo, `× 0.1 = Nm` |
| **Smoke** | Smoke / Lambda Maps 1 & 2 (`FlMng_rLmbdSmk_MAP` / `Smk2`) | `0x0E77D2`, `0x0E7A16` | 16x16 (x2) | 16-bit HiLo, `× 0.001 = Lambda` |
| **Conversion** | Torque → IQ Maps 1–3 (`FMTC_trq2qBas_MAP`) | `0x0E80EA`, `0x0E832E`, `0x0E8572` | 16x16 (x3) | 16-bit HiLo, `× 0.01 = mg/str` |
| **Duration** | Injector Duration Maps 1–6 (`InjVCD_tiET_MAP`) | `0x0F5364`, `0x0F57C8`, `0x0F5C2C`, `0x0F6090`, `0x0F64F4`, `0x0F6958` | 16x32 (x6) | 16-bit HiLo, `× 1.0 = µs` |
| **Turbo VNT** | VNT N75 Duty Cycle Maps 1–4 (`PCR_rCtlBas_MAP`) | `0x0F7F44`, `0x0F8478`, `0x0F86BC`, `0x0F8900` | 16x16 (x4) | 16-bit HiLo, `× 0.012207 = %` |
| **Turbo Boost** | Target Boost Maps 1–3 (`PCR_pDesBas_MAP`) | `0x0F9394`, `0x0F95D8`, `0x0F981C` | 16x16 (x3) | 16-bit HiLo, `× 1.0 = mbar` |
| **Turbo Limit** | Atmospheric Max Boost (`PCR_pDesMaxAP_MAP`) | `0x0F9A48` *(`0x0F9A1C`)* | 10x10 | 16-bit HiLo, `× 1.0 = mbar` |
| **Turbo SVBL** | Single Value Boost Limit (`PCR_pDesMax_C`) | `0x0F9C60` | 1x1 | 16-bit HiLo, `× 1.0 = mbar` |
| **Rail** | Rail Pressure Base Map 1 (`Rail_pSetPointBase_MAP`) | `0x0FC9D0` *(`0x0FC98C`)* | 16x16 | 16-bit HiLo, `× 0.1 = bar` |
| **Rail Limit** | Rail Single Limiters & Max Table (`Rail_pSetPointMax`) | `0x0FD060` (2x1), `0x0FD1DC` (12x8) | 2x1, 12x8 | 16-bit HiLo, `× 0.1 = bar` |

---

## Important Safety & Verification Notice

- **Checksum Verification Required:** Always verify and recalculate EDC16C31 checksums using a dedicated flashing tool (e.g., KESS, MPPS, BDM100, or WinOLS checksum module) before writing any `.bin` file to an ECU.
- **Independent Verification Advisories:** As documented in [`stage2_variants/Stage2_File_Comparison.md`](stage2_variants/Stage2_File_Comparison.md), SOI window/scaling definitions, the 2nd rail map boundary, and NM2IQ axes in the variant binaries require verification against matched ECU definition files before flashing.
- **Disclaimer:** All binaries and notes are provided for educational and research purposes only. Always perform live datalogging (boost, rail pressure, IQ, EGT, and transmission slip) and use entirely at your own risk.

---

## Related ECU Calibration Projects

- [**Suzuki Grand Vitara 1.9 DDiS (F9Q / Bosch EDC16C3-10.25) — ECU Tuning Package**](https://github.com/AyemKaan/Suzuki-Grand-Vitara-1.9-DDiS-EDC16C3) — Stage 1+ calibrations, N75/VNT limp-mode fix, EGR/TVA delete, 4300 RPM hardcut popcorn, and dyno curves.
