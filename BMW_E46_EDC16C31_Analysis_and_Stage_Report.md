# BMW E46 320d (M47TÜ) EDC16C31 — ECU Analysis & Stage 1 / 2 / 3 + Popcorn Calibration Report

**Date:** 2026-11-04  
**Base File Analyzed:** `bmw backup.bin`  
**Reference A2L / DAMOS Sources:** Bosch EDC16 A2L / DAMOS Database (`361811BMWEDC16.ols`, `BMW_30D_EDC16_218PS__E60.ols`, `BMW E87 120d DDE5.0 120kW.ols`, `4M534389.A2L`, `4M702389.A2L`)  
**Hardware Setup:** Bosch CP3 **R70** High-Pressure Fuel Pump + Bosch **0 445 110 216** Injectors + **Hybrid Turbo** + **GM 5L40-E 5-Speed Automatic Transmission** + **Stock 3-Bar MAP Sensor (`3000 mbar`)** + **Stock 1800-Bar Rail Pressure Sensor (`1650 bar` safe operating ceiling)**

> **Note:** For independent byte-level comparison and verification caveats regarding the Stage 2/3 variant files (including SOI window/scaling checks, 2nd rail table boundary overlap, and checksum verification status), also see [`stage2_variants/Stage2_File_Comparison.md`](stage2_variants/Stage2_File_Comparison.md).

---

## 1. ECU, Software, and Binary File Identification

### 1.1. ECU & Software Identity
- **Vehicle / Engine:** BMW E46 320d 2.0d 150 HP (110 kW) — **M47TÜ (M47D20O1)**, 4-Cylinder, 16V Common-Rail Diesel
- **ECU Type:** Bosch **EDC16C31** (DDE 5.0), 1 MB Flash (`1,048,576` bytes, Big-Endian 16-bit)
- **Bosch Software Number (SW):** `1037361858` (`10373618581974842A`)
- **BMW Calibration / Data ID:** `O_U6K482` (`0001970048020KU60`)
- **Reference A2L / DAMOS Matches:**
  - `361811BMWEDC16.ols` (`0281010565`, SW `1037361811`)
  - `BMW_30D_EDC16_218PS__E60.ols` (`0281011120`, SW `1037361888`, factory `0 445 110 216` injector DAMOS)
  - `BMW E87 120d DDE5.0 120kW.ols` and `4M534389.A2L` / `4M702389.A2L` (Bosch EDC16 C31/C35 4-cylinder DDE function definitions)

### 1.2. Comparison of Reference & Source `.bin` Files

| File Name | Size | MD5 Hash | Summary / Status |
| :--- | :--- | :--- | :--- |
| `bmw backup.bin` | 1,048,576 B | `db288c01ac8fa701f72eb9444e85906a` | **Primary analyzed base file.** Not stock; contains EGR Off + Stage 1 (~432 Nm) + decalibrated (+15% inflated) 131-injector Duration maps. |
| `bmw backup` *(local duplicate)* | 1,048,576 B | `db288c01ac8fa701f72eb9444e85906a` | Byte-identical to `bmw backup.bin`. |
| `bmw_e46.bin` *(local duplicate)* | 1,048,576 B | `db288c01ac8fa701f72eb9444e85906a` | Byte-identical to `bmw backup.bin`. |
| `berat` *(local duplicate)* | 1,048,576 B | `db288c01ac8fa701f72eb9444e85906a` | Byte-identical to `bmw backup.bin`. |
| `bmw_e46/bmw_e46` *(intermediate)* | 1,048,576 B | `a462e635d898aee7be5c97f9b09f081b` | Intermediate file with stock 131-injector Duration calibration, 515 Nm torque limit, EGR Off. |
| `TUNERPAD_bmw_e46_NOCHK_...bin` | 1,048,576 B | `46c1314bb8e669094055c61a3fba7868` | Differs from `bmw_e46/bmw_e46` by only 1 byte (`0x0E51D9` DTC switch); unchecksummed version. |
| `bmw_e46_Original SOI.bin` | 1,048,576 B | `c11fbcf15ae1519b55cf4c066951248e` | **216 Injector Duration calibration** (`95 mg/str = 1032 µs`) applied, SOI kept stock, 515 Nm / 85 mg file. |
| `berat son 19.10.2026` | 1,048,576 B | `15d661e458a80fa8cf1a85f774cae747` | **216 Injector Duration** + **SOI 32.51° CA** + **VNT** + **2650 mbar Boost / 2750 SVBL** + MAF/EGR delete file. |

---

## 2. Map-by-Map Status Inside `bmw backup.bin` (What Is Active vs. Disabled)

The table below lists all critical control maps inside `bmw backup.bin`, including their addresses, dimensions, and current calibration status:

| Map / Function (Bosch DAMOS Name) | Start – End Address | Size | Current Values in `bmw backup.bin` | Status & Technical Condition |
| :--- | :--- | :--- | :--- | :--- |
| **Driver Wish 1 & 2** (`AccPed_trqEngLow/High_MAP`) | `0x0E063C – 0x0E0792` `0x0E0880 – 0x0E09D6` | 16x9 (x2) | At 100% pedal: max **432.5 Nm** (@ 2500 RPM), **356.2 Nm** @ 4000 RPM | **Stage 1 Tuned** *(Flat 555.0 Nm in other files)* |
| **Main EGR Map** (`AirCtl_mDesBas_MAP`) | `0x0E1372 – 0x0E152E` | 12x16 | `280.0 – 1040.9 mg/str` (Factory values intact) | **Inactive** *(Disabled via hysteresis)* |
| **EGR Regen / Alternate Maps** (`AirCtl_mDesRgn1/2_MAP`) | `0x0E17FC – 0x0E19BA` `0x0E1A40 – 0x0E1BFE` | 12x16 (x2) | Entire table flat `1200.0 mg/str` (`12000`) | **EGR Disabled Mode** |
| **EGR Hysteresis Curves (EGR Off)** (`AirCtl_qHiRgn_CUR` / `qLoRgn_CUR`) | `0x0E29EE – 0x0E2A52` `0x0E2B20 – 0x0E2B84` | 25x1 (x2) | All injection thresholds set to **`0`**, axis zeroed above 3000 RPM | **EGR OFF** |
| **Swirl Flaps** (`IndSys_rVSA_MAP`) | `0x0E9EA8 – 0x0EA0EA` | 16x16 | `100%` (`10000`) at low/mid load, `0%` (`0`) at high RPM/load | **ON (Active / Stock)** |
| **Torque Limiter 1** (`EngPrt_trqLim_CUR`) | `0x0E66AE – 0x0E6704` | 21x1 | Flat **`500.0 Nm`** from 700–4950 RPM, 5020 RPM: `0 Nm` | **Flat 500 Nm (Curve flattened)** |
| **Torque Limiter 2** (`EngPrt_trqLim1_CUR`) | `0x0E6D96 – 0x0E6DEC` | 21x1 | Flat **`500.0 Nm`** from 0–4900 RPM, 5020 RPM: `82.0 Nm` | **Flat 500 Nm (Curve flattened)** |
| **Torque Limiter 3** (`EngPrt_trqLimDA_CUR`) | `0x0E6DEC – 0x0E6E42` | 21x1 | Flat **`500.0 Nm`** from 0–5000 RPM, 5250 RPM: `0 Nm` | **Flat 500 Nm (Curve flattened)** |
| **Torque Limiter 4 (Gear/EGS)** (`EngPrt_trqCBLim_CUR`) | `0x0E6E42 – 0x0E6E90` | 19x1 | Flat **`500.0 Nm`** from 750–4900 RPM, 5020 RPM: `0 Nm` | **Flat 500 Nm (Curve flattened)** |
| **Torque Limiter 5** (`EngPrt_trqCBLim1_CUR`) | `0x0E6E98 – 0x0E6EEE` | 21x1 | Flat **`500.0 Nm`** from 0–4800 RPM, 4900 RPM: `0 Nm` | **Flat 500 Nm (Curve flattened)** |
| **Rev Limiter / Normal Op. Torque Limit** (`EngPrt_trqNLim_CUR`) | `0x0E6EEE – 0x0E6F44` | 21x1 | 2000–3000 RPM: **`625.0 Nm`**, 4600 RPM: `525.0 Nm`, 4700 RPM: `86.1 Nm`, 4950 RPM: `0 Nm` | **OFF (No Popcorn, soft limiter)** |
| **Speed Limiter / Overheat Protection** (`EngPrt_qOvhtPrvVRng_MAP`) | `0x0E6F46 – 0x0E7024` | 13x16 | Y-axis up to `260.0 km/h`, entire table `100.0 mg/str` (`10000`) | **Vmax Raised (~250+ km/h)** |
| **Smoke Limiter / Lambda Map 1** (`FlMng_rLmbdSmk_MAP`) | `0x0E778E – 0x0E79D2` | 16x16 | `0.80 – 1.00` at low airflow, `1.10` (`1100`) at high load | **Open (Medium-High Fuel Allowance)** |
| **Smoke Limiter / Lambda Map 2** (`FlMng_rLmbdSmk2_MAP`) | `0x0E79D2 – 0x0E7C16` | 16x16 | Flat **`1.00`** (`1000` = AFR 14.5:1) above 1750 RPM across airflows | **Open (Smoky / Rich AFR)** |
| **Torque-to-Fuel Conversion Maps (x3)** (`FMTC_trq2qBas_MAP`) | `0x0E80A6 – 0x0E82EA` `0x0E82EA – 0x0E852E` `0x0E852E – 0x0E8772` | 16x16 (x3) | Y-axis rescaled from `400 Nm` to **`460 Nm`**; `460 Nm` column = `72.6 – 74.0 mg/str` | **Scaled to 460 Nm / ~74 mg/str** |
| **Start of Injection / SOI Maps (x5)** (`InjCrv_phiMI1Bas1..5_MAP`) | `0x0EA7C6 – 0x0EB31A` | 16x16 (x5) | Y-axis max `65 mg/str`, max `30.38° – 33.40° CA` @ 4800 RPM | **Stock (Untouched)** |
| **Pilot Injection Quantity** (`InjCrv_qPiI1Bas_MAP` x2) | `0x0EEBA4 – 0x0EEDE8` `0x0EF0D0 – 0x0EF314` | 16x16 (x2) | Stock `131` injector values (`0.52 – 3.26 mg/inj`) | **Stock (Calibrated for 131 Injectors)** |
| **Injection Duration (x6)** (`InjVCD_tiET_MAP`) | `0x0F5300 – 0x0F6D58` | 16x32 (x6) | Y-axis `90 mg/str`, `1600 bar / 90 mg` = **`1397 – 1436 µs`** (+15% inflated 131 injector!) | **INCORRECT (Incompatible with 216 Injectors!)** |
| **Turbo VNT (N75) Maps (x4)** (`PCR_rCtlBas_MAP` series) | `0x0F7F00 – 0x0F8144` `0x0F8434 – 0x0F8B00` | 16x16 (x4) | Stock VNT geometry (`12.9% – 69.6%` duty cycle) | **Stock (Not Adapted for Hybrid Turbo)** |
| **Target Boost Maps (x3)** (`PCR_pDesBas_MAP` series) | `0x0F9350 – 0x0F9A1C` | 16x16 (x3) | Peak **`2592 mbar`** (~1.59 bar) @ 2250–2750 RPM, `2498 mbar` @ 4000 RPM | **Stage 1 Boost (~1.59 bar)** |
| **Atmospheric Max Boost & SVBL** (`PCR_pDesMaxAP_MAP` & `PCR_pDesMax_C`) | `0x0F9A1C – 0x0F9B10` `0x0F9C60 – 0x0F9C62` | 10x10 1x1 | Table max `2640 mbar`, Single Value Boost Limit (SVBL): **`2650 mbar`** (1.65 bar) | **SVBL 2650 mbar** |
| **Rail Pressure Maps (x2) & Limiters** (`Rail_pSetPointBase_MAP` & `Max`) | `0x0FC98C – 0x0FCC00` `0x0FCE20 – 0x0FD29C` | 16x16 (x2) 12x8 | In-map peak **`1653.6 bar`**, Single (`0x0FD060`) & Table (`0x0FD1B0`) Limiters: **`1648.5 bar`** | **~1650 bar (+3% Increased)** |
| **Diagnostic Trouble Code (DTC) Table** (`DSM_ClaDfp_...`) | `0x0E4D40 – 0x0E5900` | Table | All fault classes stock and active | **ACTIVE (No DTC Deletes)** |

---

## 3. Critical Engineering Findings for the Upgraded Hardware (R70 Pump + 216 Injectors + Hybrid Turbo)

1. **Injector Duration Mismatch (`0x0F5300 – 0x0F6D58`):**
   - The Duration maps in `bmw backup.bin` belong to the stock `0 445 110 131` injectors and have their upper columns (`57.5 – 90 mg/str`) artificially inflated by +15% (`1600 bar / 90 mg = 1436 µs`).
   - The installed **Bosch `0 445 110 216`** injectors have significantly higher flow capacity. In the true 216 injector calibration found in `bmw_e46_Original SOI.bin` and `berat son 19.10.2026`, at `1600 bar`:
     - `60 mg/str` = **`735 µs`** (vs. `764–779 µs` in `bmw backup.bin`)
     - `75 mg/str` = **`861 µs`** (vs. `1194–1196 µs` in `bmw backup.bin` — **39% longer opening time!**)
     - `85 mg/str` = **`947 µs`** (vs. `1296–1327 µs` in `bmw backup.bin` — **40% longer opening time!**)
     - `95 mg/str` = **`1032 µs`**
   - **Conclusion:** Running `bmw backup.bin` with 216 injectors causes the ECU to believe it is injecting `74 mg` while physically delivering **~105+ mg** of fuel. This causes severe black smoke, excessive exhaust gas temperature (EGT), late combustion, and piston damage risk. **All Stage 1, Stage 2, and Stage 3 calibrations must use true 216 injector Duration tables.**

2. **Flattened 500 Nm Torque Limiters (`0x0E66AE – 0x0E6EEE`):**
   - Five torque limiters in `bmw backup.bin` were set to a completely flat `500.0 Nm` from 700 RPM up to 4950 RPM.
   - To protect the drivetrain, crankshaft, and automatic transmission at low RPM (1000–1750 RPM) and keep EGT under control at high RPM (4200+ RPM), the torque limiters must be shaped as a **progressive, realistic torque curve**.

3. **Start of Injection / Timing Advance (`0x0EA7C6 – 0x0EB31A`):**
   - SOI maps in `bmw backup.bin` are completely stock (axis up to `65 mg/str`).
   - When delivering 75–95 mg/str with 216 injectors and an R70 pump, the SOI axis should be rescaled to `85–95 mg/str` with stage-appropriate timing advance (**+1.5° to +4.0° CA** in the high-RPM/high-load region) to prevent excessive end-of-injection (EOI) retard past TDC.

4. **Hybrid Turbo VNT (N75), Boost, and Stock 3-Bar MAP Sensor (`0x0F7F00 – 0x0F9C62`):**
   - The vehicle uses the **stock 3-bar MAP sensor (`3000 mbar` absolute ceiling)** (`0x0E3A2A` and `0x0FA7E0` linearization tables end at `3000 mbar`).
   - If target boost is pushed too close to `2950–3000 mbar`, transient 80–120 mbar overboost spikes during hybrid turbo spool will hit the `3000 mbar` sensor ceiling and trigger an **Overboost / Limp Mode** fault.
   - To ensure reliable, fault-free operation on the stock 3-bar MAP sensor:
     - **Stage 1:** Target Boost **`2600 mbar`** (1.60 bar gauge), SVBL **`2680 mbar`**
     - **Stage 2:** Target Boost **`2680 mbar`** (1.68 bar gauge), SVBL **`2750 mbar`**
     - **Stage 3:** Target Boost **`2780 mbar`** (1.78 bar gauge), SVBL **`2850 mbar`** (leaving 150+ mbar diagnostic headroom)

5. **CP3 R70 High-Pressure Pump & Stock Rail Pressure Sensor (`0x0FC98C – 0x0FD29C`):**
   - The vehicle retains the **stock 1800-bar Rail pressure sensor** (`0x0FA800` linearization upper bound `1900 bar`).
   - ECU fault/cutoff thresholds for **Rail Overpressure** at `0x0FBFA4` and `0x0FC098` are defined at **`1750 bar` (`17500`)** and `1850 bar` (`18500`).
   - Because the R70 pump delivers high volume, targeting `1680–1700 bar` risks transient spikes touching `1750 bar` during gear shifts or sudden lift-off, triggering **Rail Pressure Fault / Limp Mode / Engine Cutoff**.
   - Therefore, target rail maps are kept at **`1650 bar` (`1648.5–1653.6 bar`)** and single/table rail limiters at **`1650–1655 bar` (`16485–16550`)**. The R70 pump holds a rock-solid `1650 bar` even under `90+ mg/str` fueling demand.

6. **GM 5L40-E 5-Speed Automatic Transmission & Torque Converter Calibration (`0x0E6D74`, `0x0E6E42`, `0x0E943A – 0x0E95D2`):**
   - On automatic E46 320d models equipped with the **GM 5L40-E** (A5S390R), the most vulnerable regions are **torque converter clutch (TCC) lock-up engagement between 1500–2100 RPM** and **high-load operation in 5th gear (Overdrive, 0.75:1)**.
   - In the stock calibration, the gear-based torque protection switch (`EngPrt_swtTrqGear_CUR` @ `0x0E6D74`) is disabled (`0`) and the per-gear torque limiters (`Gearbx_trqMaxGear1..5_CUR` @ `0x0E943A – 0x0E95D2`) are set to a flat `600 Nm`.
   - Furthermore, the **+15% artificial fuel inflation** applied to the `750–1500 RPM` rows of NM2IQ Map 1 (`0x0E80EA`) in `berat son 19.10.2026` creates a **15% discrepancy between actual torque and CAN-Bus reported torque** read by the EGS transmission control unit, causing harsh shifts, shift flare, and TCC shudder.
   - Accordingly, all generated Stage 1, 2, 3, and Popcorn files include a **GM 5L40-E Automatic Transmission Protection Package**:
     - **TCC Lock-Up Limiter Enabled (`EngPrt_swtTrqGear_CUR` @ `0x0E6D74`):** Set to `[0, 0, 1, 1, 1, 1, 1, 0]` for gears 1–5, activating the `EngPrt_trqLim1_CUR` (`0x0E6E42`) converter lock-up torque curve.
     - **Anti-Shudder Low-RPM Ramp (`1250 – 2000 RPM`):** Torque ramps progressively until TCC lock-up is fully seated; peak torque (**440 / 485 / 515 Nm**) arrives once the converter is locked and the hybrid turbo is fully spooled (**2250 – 3500 RPM**).
     - **Per-Gear Torque Limits (`Gearbx_trqMaxGear1..5_CUR` @ `0x0E943A – 0x0E95D2`):**
       - **1st Gear (`0x0E943A`):** `400 Nm` (Stage 1) / `420 Nm` (Stage 2) / `440 Nm` (Stage 3) — reduces planetary gearset and drivetrain shock on launch.
       - **2nd Gear (`0x0E94A0`):** `430 Nm` (Stage 1) / `465 Nm` (Stage 2) / `490 Nm` (Stage 3) — smooths the 1→2 shift.
       - **3rd & 4th Gear (`0x0E9506`, `0x0E956C`):** Full target torque (`440 / 485 / 515 Nm`).
       - **5th Gear (`0x0E95D2`):** `430 Nm` (Stage 1) / `465 Nm` (Stage 2) / `485 Nm` (Stage 3) — protects the 5th-gear overdrive clutch pack and TCC on highway pulls.
     - **Linear CAN-Bus Torque Reporting (`FMTC_trq2qBas_MAP` @ `0x0E80A6 – 0x0E8772`):** Removed the +15% low-RPM NM2IQ distortion so the EGS receives accurate motor torque values and commands proper hydraulic line pressure.
     - **Eliminated Kickdown Shift Cut:** On non-Popcorn Stage 1, 2, and 3 files, the NM2IQ RPM axis is restored to the factory `4600 / 4950 RPM` layout, preventing premature fuel cut at `4701 RPM` during full-throttle kickdown shifts.

---

## 4. Stage 1, Stage 2, Stage 3 & Popcorn Calibration Specifications (GM 5L40-E Adapted)

The matrix below details the calibration targets for the four `.bin` files generated for **R70 Pump + 216 Injectors + Hybrid Turbo + GM 5L40-E Automatic + Stock 3-Bar MAP + Stock Rail Sensor**:

| Parameter / Map Group | Stage 1 (`..._Stage1.bin`) | Stage 2 (`..._Stage2.bin`) | Stage 3 (`..._Stage3.bin`) | Stage 3 + Popcorn (`..._Popcorn_4800RPM.bin`) |
| :--- | :--- | :--- | :--- | :--- |
| **Target Power & Torque** *(estimated, unverified on dyno)* | **~205–210 HP / 440 Nm** | **~235 HP / 485 Nm** | **~255–265 HP / 515 Nm** | **~255–265 HP / 515 Nm + 4800 RPM Hardcut** |
| **Driver Wish (`0x0E063C`, `0x0E0880`)** | Max `450 Nm` (smooth GM 5L40-E pedal) | Max `500 Nm` (sporty GM 5L40-E pedal) | Max `540 Nm` (progressive GM 5L40-E pedal) | Max `540 Nm` (progressive GM 5L40-E pedal) |
| **Main & TCC Torque Limiters (`0x0E6D96`, `0x0E6E42`)** | 1750 RPM: `395 Nm`, 2250–2750 RPM: **`440 Nm`**, 4000 RPM: `426 Nm` | 1750 RPM: `415 Nm`, 2250–3000 RPM: **`485 Nm`**, 4000 RPM: `472 Nm` | 1750 RPM: `435 Nm`, 2250–3000 RPM: **`515 Nm`**, 4000 RPM: `500 Nm` | **`4790 RPM: Full Torque` → `4800 RPM: 0 Nm`** (6 limiters + 3 NM2IQ synchronized) |
| **GM 5L40-E Gear Torque Limits (`0x0E943A – 0x0E95D2`)** | 1st: **`400 Nm`**, 2nd: **`430 Nm`**, 3rd–4th: **`440 Nm`**, 5th: **`430 Nm`** | 1st: **`420 Nm`**, 2nd: **`465 Nm`**, 3rd–4th: **`485 Nm`**, 5th: **`465 Nm`** | 1st: **`440 Nm`**, 2nd: **`490 Nm`**, 3rd–4th: **`515 Nm`**, 5th: **`485 Nm`** | 1st: **`440 Nm`**, 2nd: **`490 Nm`**, 3rd–4th: **`515 Nm`**, 5th: **`485 Nm`** |
| **Torque → IQ (`0x0E80A6 – 0x0E8772`)** | `440 Nm` → **`~72 mg/str`** (CAN-Bus linear) | `485 Nm` → **`~80 mg/str`** (CAN-Bus linear) | `515 Nm` → **`~88–90 mg/str`** (CAN-Bus linear) | `515 Nm` → **`~88–90 mg/str`** (CAN-Bus linear) |
| **Injector Duration (`0x0F5300 – 0x0F6D58`)** | **True 216 Calibration** (`72 mg @ 1600 bar = ~835 µs`) | **True 216 Calibration** (`80 mg @ 1600 bar = 902 µs`) | **True 216 Calibration** (`90 mg @ 1600 bar = ~990 µs`) | **True 216 Calibration** (`90 mg @ 1600 bar = ~990 µs`) |
| **Start of Injection / SOI (`0x0EA7C6 – 0x0EB31A`)** | `40%` blend (**`+1.0° – +1.5° CA`**) | `75%` blend (**`+2.0° – +2.8° CA`**) | `100%` target (**`32.51° CA`** max) | `100%` target (**`32.51° CA`** max) |
| **Target Boost (`0x0F9350 – 0x0F9A1C`)** | **`2600 mbar`** (1.60 bar — stock 3-bar MAP safe) | **`2680 mbar`** (1.68 bar — stock 3-bar MAP safe) | **`2780 mbar`** (1.78 bar — stock 3-bar MAP safe ceiling) | **`2780 mbar`** (1.78 bar — stock 3-bar MAP safe ceiling) |
| **Single Value Boost Limit / SVBL (`0x0F9C60`)** | **`2680 mbar`** (1.68 bar) | **`2750 mbar`** (1.75 bar) | **`2850 mbar`** (1.85 bar — safely below 3000 mbar sensor) | **`2850 mbar`** (1.85 bar — safely below 3000 mbar sensor) |
| **VNT / N75 (`0x0F7F00 – 0x0F8B00`)** | Base VNT calibration | Hybrid turbo VNT calibration | Hybrid turbo VNT calibration | Hybrid turbo VNT calibration |
| **Rail Pressure & Limiters (`0x0FC98C – 0x0FD29C`)** | **`1650 bar`** (`1648.5 bar` limit — stock sensor safe) | **`1650 bar`** (`1655.0 bar` limit — stock sensor safe) | **`1650 bar`** (`1655.0 bar` limit — stock sensor safe) | **`1650 bar`** (`1655.0 bar` limit — stock sensor safe) |
| **Smoke / Lambda (`0x0E778E`, `0x0E79D2`)** | Lambda **`1.15`** (`1150` — AFR 16.7, smoke-free) | Lambda **`1.08`** (`1080` — AFR 15.6, minimal haze) | Lambda **`1.03`** (`1030` — AFR 14.9, power-oriented) | Lambda **`1.03`** (`1030` — AFR 14.9, power-oriented) |
| **EGR & Swirl Flaps** | EGR **OFF**, Swirl Flaps Stock | EGR **OFF**, Swirl Flaps **OFF (`0%`)** | EGR **OFF**, Swirl Flaps **OFF (`0%`)** | EGR **OFF**, Swirl Flaps **OFF (`0%`)** |
| **Popcorn / Hardcut RPM** | None (`4950–5020 RPM` soft cut, uninterrupted kickdown) | None (`4950–5020 RPM` soft cut, uninterrupted kickdown) | None (`4950–5020 RPM` soft cut, uninterrupted kickdown) | **ENABLED (`4790 → 4800 RPM` Hardcut)** |

---

## 5. Generated Calibration `.bin` Files

| File Name | Size | MD5 Hash | Description |
| :--- | :--- | :--- | :--- |
| `BMW_E46_320d_R70_216_Hybrid_Stage1.bin` | 1,048,576 B | `5c63681a2f2a92dd1d0121de6b4e0e4c` | Stage 1 (440 Nm / ~72 mg / 1.60 bar Boost / 1650 bar Rail / 216 Injectors / GM 5L40-E Protection / EGR Off) |
| `BMW_E46_320d_R70_216_Hybrid_Stage2.bin` | 1,048,576 B | `7b945c6124e0ededb2a72eb31836fc9e` | Stage 2 (485 Nm / ~80 mg / 1.68 bar Boost / 1650 bar Rail / 216 Injectors / GM 5L40-E Protection / Hybrid VNT / Flaps & EGR Off) |
| `BMW_E46_320d_R70_216_Hybrid_Stage3.bin` | 1,048,576 B | `af8e6d70defa440bd73e05a8f7eae99e` | Stage 3 (515 Nm / ~90 mg / 1.78 bar Boost - 2850 SVBL / 1650 bar Rail / 216 Injectors / GM 5L40-E Protection / Full SOI & VNT) |
| `BMW_E46_320d_R70_216_Hybrid_Stage3_Popcorn_4800RPM.bin` | 1,048,576 B | `473863e9e3037357dda31f3e5af4ae46` | Stage 3 + **4800 RPM Popcorn / Hardcut Limiter** (`4790 → 4800 RPM` synchronized across all torque limiters and NM2IQ + GM 5L40-E Protection) |

---

## 6. Detailed Analysis of `berat son 19.10.2026`

Inspection of `berat son 19.10.2026` (`MD5: 15d661e458a80fa8cf1a85f774cae747`) shows it is a **Stage 2 / Stage 2+ (~230–240 HP / 515 Nm)** calibration built for **216 Injectors + Hybrid Turbo + R70 Pump + Stock 3-Bar MAP Sensor**, containing an incomplete **4700 RPM Popcorn** attempt.

### 6.1. Power, Torque, Fueling, and Boost Profile
- **Torque Limiters (`0x0E6DC2` & `0x0E6E6A`):**
  - `1500 RPM`: `438.0 Nm` (`393.0 Nm` in gear/TCC limiter)
  - `1750 RPM`: `491.0 Nm` (`446.0 Nm` in gear/TCC limiter)
  - `2000 – 2500 RPM`: Peak **`515.0 Nm`**
  - `3000 RPM`: `508.0 Nm` | `3500 RPM`: `505.0 Nm` | `4000 RPM`: **`492.0 – 495.0 Nm`** | `4400 RPM`: `475.0 – 478.0 Nm`
- **Torque → Fuel Conversion (`0x0E80A6`):**
  - Between `2000 – 3500 RPM`, `515 Nm` requests **`84.8 – 85.5 mg/str`**.
  - Between `4000 – 4400 RPM`, the `515 Nm` column specifies `88.3 – 89.6 mg/str`, but because the main torque limiter caps output at `495 Nm` @ 4000 RPM (`478 Nm` @ 4400 RPM), actual commanded fuel is **`~82 – 84 mg/str`** (`~920 µs` injection duration at `1600 bar` on 216 injectors).
- **Boost Pressure (`0x0F9350 – 0x0F9C60`):**
  - Flat **`2650 mbar` (1.65 bar gauge)** target from `2250 – 4250 RPM`,
  - Atmospheric Max Boost (`0x0F9A48`): **`2700 mbar` (1.70 bar)**,
  - Single Value Boost Limit / SVBL (`0x0F9C60`): **`2750 mbar` (1.75 bar)**.
- **Estimated Real Output:**
  - With `1.65 bar` boost and `82–84 mg/str` at `4000–4400 RPM`, realistic output is **~230–240 HP** and **~490–510 Nm**. Because boost stays capped at `1.65 bar`, top-end `84 mg` fueling cannot burn completely smoke-free and produces visible black smoke.

### 6.2. Specific Modifications & Deficiencies in `berat son 19.10.2026`

| Feature / Region | Address (Hex) | Status in `berat son 19.10.2026` | Technical Assessment |
| :--- | :--- | :--- | :--- |
| **216 Injector Duration** | `0x0F5300 – 0x0F6D58` | `95 mg/str = 1032 µs` (@ 1600 bar) | **Correct:** Proper 216 injector calibration applied. |
| **4700 RPM Popcorn (Hardcut)** | `0x0E80A6` (NM2IQ 1) & `0x0E6EEE` (TL6) | NM2IQ 1 sets `4700 RPM: 89.8 mg` → `4701 RPM: 0.0 mg`; **however, `TL6` still tapers from `4600 RPM: 525 Nm` → `4700 RPM: 86.1 Nm`!** | **Incomplete / Flawed:** Because `TL6` pulls torque down to `86 Nm` between `4620–4680 RPM`, the engine cannot hit the `4701 RPM` cut under full load, leaving the popcorn weak/muffled. |
| **Low-RPM Fuel & MAF Patch** | `0x0E80EA`, `0x0E1000 – 0x0E1A7C` | NM2IQ inflated by `+15%` between `750–1500 RPM` (`1500 RPM = 112.5 mg/str`); MAF/EGR tables raised | Intended to sharpen off-boost throttle response, but causes low-RPM smoke and CAN-Bus torque mismatch for the EGS. |
| **Start of Injection (SOI x5)** | `0x0EA7C6 – 0x0EB31A` | Y-axis extended to `85 mg/str`, **`32.51° CA`** advance across `2500–4800 RPM` | Appropriate target range for 216 injectors and elevated IQ. |
| **Hybrid Turbo VNT (N75 x4)** | `0x0F7F00 – 0x0F8AF2` | All 4 VNT maps rescaled for hybrid turbo | Adapted for spool behavior and higher exhaust flow at top RPM. |
| **EGR & DTC Delete** | `0x0E2A10`, `0x0E4D56 – 0x0E4D6E` | EGR hysteresis zeroed and 3 EGR/MAF fault codes (`19056`, `16881`, `19234`) disabled | **EGR & EGR DTCs OFF.** |
| **Swirl Flaps & Pilot IQ** | `0x0E9EEE`, `0x0EEBE8` | Left stock | Swirl flaps remain active; pilot IQ still calibrated for 131 injectors. |

---

## 7. Map Address Reference Table (WinOLS / TunerPro)

| Category | Map Description | Start Address (Hex) | Size | Data Type / Factor |
| :--- | :--- | :--- | :--- | :--- |
| **Pedal** | Driver Wish 1 (`AccPed_trqEngLow_MAP`) | `0x0E0672` *(Axis: `0x0E063C`)* | 16x9 | 16-bit HiLo Signed, `× 0.1 = Nm` |
| **Pedal** | Driver Wish 2 (`AccPed_trqEngHigh_MAP`) | `0x0E08B6` *(Axis: `0x0E0880`)* | 16x9 | 16-bit HiLo Signed, `× 0.1 = Nm` |
| **Air / EGR** | EGR Map (`AirCtl_mDesBas_MAP`) | `0x0E13AE` *(Axis: `0x0E1372`)* | 12x16 | 16-bit HiLo, `× 0.1 = mg/str` |
| **Air / EGR** | EGR Hysteresis 1 (`AirCtl_qHiRgn_CUR`) | `0x0E2A22` *(Axis: `0x0E29EE`)* | 25x1 | 16-bit HiLo, `× 0.01 = mg/str` |
| **Air / EGR** | EGR Hysteresis 2 (`AirCtl_qLoRgn_CUR`) | `0x0E2B54` *(Axis: `0x0E2B20`)* | 25x1 | 16-bit HiLo, `× 0.01 = mg/str` |
| **Air / Flaps** | Swirl Flaps (`IndSys_rVSA_MAP`) | `0x0E9EEE` *(Axis: `0x0E9EA8`)* | 16x16 | 16-bit HiLo, `× 0.01 = %` |
| **Torque** | Torque Limiter 1 | `0x0E66DA` *(Axis: `0x0E66AE`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque / EGS** | AT Converter Lock-Up Gear Switch (`EngPrt_swtTrqGear_CUR`) | `0x0E6D86` *(Axis: `0x0E6D74`)* | 8x1 | 16-bit HiLo, `0 = Off, 1 = Active` |
| **Torque** | Torque Limiter 2 (Main Torque Limiter) | `0x0E6DC2` *(Axis: `0x0E6D96`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque** | Torque Limiter 3 (Launch Limiter `EngPrt_trqLimDA_CUR`) | `0x0E6E18` *(Axis: `0x0E6DEC`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque / EGS** | Torque Limiter 4 (AT Converter Lock-Up `EngPrt_trqLim1_CUR`) | `0x0E6E6A` *(Axis: `0x0E6E42`)* | 19x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque** | Torque Limiter 5 | `0x0E6EC4` *(Axis: `0x0E6E98`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Torque / Rev Cut** | Torque Limiter 6 / Rev Limiter (`EngPrt_trqNLim_CUR`) | `0x0E6F1A` *(Axis: `0x0E6EEE`)* | 21x1 | 16-bit HiLo, `× 0.1 = Nm` |
| **Transmission** | 1st–6th Gear & Reverse Torque Limits (`Gearbx_trqMaxGear1..R_CUR`) | `0x0E943A`, `0x0E94A0`, `0x0E9506`, `0x0E956C`, `0x0E95D2`, `0x0E9638`, `0x0E969E` | 15x1 (x7) | 16-bit HiLo, `× 0.1 = Nm` |
| **Smoke** | Lambda / Smoke Map 1 (`FlMng_rLmbdSmk_MAP`) | `0x0E77D2` *(Axis: `0x0E778E`)* | 16x16 | 16-bit HiLo, `× 0.001 = Lambda` |
| **Smoke** | Lambda / Smoke Map 2 (`FlMng_rLmbdSmk2_MAP`) | `0x0E7A16` *(Axis: `0x0E79D2`)* | 16x16 | 16-bit HiLo, `× 0.001 = Lambda` |
| **Conversion** | Torque → IQ Map 1 (`FMTC_trq2qBas_MAP`) | `0x0E80EA` *(Axis: `0x0E80A6`)* | 16x16 | 16-bit HiLo, `× 0.01 = mg/str` |
| **Conversion** | Torque → IQ Map 2 | `0x0E832E` *(Axis: `0x0E82EA`)* | 16x16 | 16-bit HiLo, `× 0.01 = mg/str` |
| **Conversion** | Torque → IQ Map 3 | `0x0E8572` *(Axis: `0x0E852E`)* | 16x16 | 16-bit HiLo, `× 0.01 = mg/str` |
| **Timing (SOI)** | SOI Maps 1 – 5 (`InjCrv_phiMI1Bas1..5_MAP`) *(verify window/scaling before use)* | `0x0EA80A`, `0x0EAA4E`, `0x0EAC92`, `0x0EAED6`, `0x0EB11A` | 16x16 (x5) | 16-bit HiLo Signed, `× 0.0234375 = °CA` |
| **Duration (Ti)** | Injector Duration 1 – 6 (`InjVCD_tiET_MAP`) | `0x0F5364`, `0x0F57C8`, `0x0F5C2C`, `0x0F6090`, `0x0F64F4`, `0x0F6958` | 16x32 (x6) | 16-bit HiLo, `× 1.0 = µs` |
| **Turbo VNT** | VNT Duty Cycle 1 – 4 (`PCR_rCtlBas_MAP`) | `0x0F7F44`, `0x0F8478`, `0x0F86BC`, `0x0F8900` | 16x16 (x4) | 16-bit HiLo, `× 0.012207 = %` |
| **Turbo Boost** | Target Boost 1 – 3 (`PCR_pDesBas_MAP`) | `0x0F9394`, `0x0F95D8`, `0x0F981C` | 16x16 (x3) | 16-bit HiLo, `× 1.0 = mbar` |
| **Turbo Limit** | Atmospheric Max Boost (`PCR_pDesMaxAP_MAP`) | `0x0F9A48` *(Axis: `0x0F9A1C`)* | 10x10 | 16-bit HiLo, `× 1.0 = mbar` |
| **Turbo SVBL** | Single Value Boost Limit (`PCR_pDesMax_C`) | `0x0F9C60` | 1x1 | 16-bit HiLo, `× 1.0 = mbar` |
| **Rail** | Rail Pressure Map 1 & 2 (`Rail_pSetPointBase_MAP`) *(verify 2nd map boundary)* | `0x0FC9D0`, `0x0FCE64` | 16x16 (x2) | 16-bit HiLo, `× 0.1 = bar` |
| **Rail Limit** | Rail Single Limit & Max Map (`Rail_pSetPointMax`) | `0x0FD060` (2x1), `0x0FD1DC` (12x8) | 2x1, 12x8 | 16-bit HiLo, `× 0.1 = bar` |
| **Checksum** | Calibration Block Signature & Checksum Fields *(verify with ECU flash tool)* | `0x0FEF74 – 0x0FEF78`, `0x0FEFF8 – 0x0FEFFC` | 32-bit (x2) | 32-bit Big-Endian |
