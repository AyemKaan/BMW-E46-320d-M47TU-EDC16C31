# BMW E46 — Stage 2 Variant File Comparison

**Date:** 2026-11-04  
**Reference File:** `BMW_E46_320d_R70_216_Hybrid_Stage2.bin`  
**Compared Folder:** `stage2_variants/`  
**Hardware Context (per main report):** M47TÜ, Bosch CP3 R70 pump, Bosch 216 injectors, hybrid turbo, GM 5L40-E automatic transmission.

## 1. Scope and Verification Boundaries

All 10 binary files in this folder were compared byte-for-byte against the reference file. Every file is `1,048,576` bytes in size. None of the binaries were modified; this document solely records the comparison findings.

**Byte diffs and raw numerical values were computed directly. Map names, addresses, dimensions, and scaling factors were taken from [`BMW_E46_EDC16C31_Analysis_and_Stage_Report.md`](../BMW_E46_EDC16C31_Analysis_and_Stage_Report.md) and were not independently verified against matched ECU definition files.** In particular, boundary/definition inconsistencies were observed in the SOI maps and the second rail pressure table. This document is not a flashing approval, safety guarantee, or dyno report.

## 2. Horsepower and Torque: What Is Known?

| File Group | Power / HP | Main Torque Curve Peak | Other Torque Curves Peak | Assessment |
| :--- | :--- | ---: | ---: | :--- |
| Reference Stage 2 | Main report lists ~235 HP target; unverified by measurement | 485 Nm | 500 Nm | HP was not measured or calculated in this comparison |
| 10 variant files in this folder | Actual HP unknown; no reliable HP figure can be inferred from files alone | 515 Nm | 550 Nm | Table values using report scaling; not measured engine output |

**Having `515 Nm` or `550 Nm` in a table does not mean the engine produces that torque.** Real output depends on active limiters, actual airflow, injected fuel mass, turbo efficiency, temperatures, injection timing, and transmission torque intervention. Similarly, `stage3` in a filename does not prove a specific power level.

Power and torque are related at the same RPM point via `P(kW) = T(Nm) × RPM / 9549`. Combining peak torque with a different RPM to estimate HP is invalid. Real figures require dyno testing and vehicle datalogs.

## 3. Per-File Byte Comparison

Reference MD5: `7b945c6124e0ededb2a72eb31836fc9e`

| File | Bytes Differing from Reference | MD5 |
| :--- | ---: | :--- |
| `bmw_e46_stage2.bin` | 3,587 | `be74cd18e8c13e4dae39d264d336afbc` |
| `bmw_e46_stage2_fix.bin` | 3,573 | `34b1daf7fd28fdebce0e979c16196221` |
| `bmw_e46_stage2_fix2.bin` | 3,501 | `a6d87098a09f40f19a453031e10b34c8` |
| `bmw_e46_stage2_pre_rail1700.bin` | 3,618 | `eb6f69508639be98fe47c39d960baf6b` |
| `bmw_e46_stage2_pre_v2.bin` | 3,610 | `206f67552d2593b032eca2d0e4cb30c1` |
| `bmw_e46_stage2_pre_v3.bin` | 3,587 | `a4941362b68a31c6e81b0d65b9deef37` |
| `bmw_e46_stage2_verified.bin` | 3,362 | `4e1136d1b40f7f33a3e334fd58354ba1` |
| `bmw_e46_stage3_fix2_rail.bin` | 3,486 | `a2bd768f751068ebd2567def1a0e7faa` |
| `bmw_e46_stage3_incremental.bin` | 3,488 | `549686b7947615ed627309a345bb7859` |
| `bmw_e46_stage3b_iqb_only.bin` | 3,473 | `0054b4dce754b78ea88ffd51ffc939c8` |

None of the 10 files are identical to the reference or to one another. Fewer differing bytes does not imply a better or safer calibration.

## 4. Boost, Rail, Fueling, and Other Core Differences

The variant values below are shared across all 10 files in this folder:

| Region / Parameter | Reference Stage 2 | All 10 Variant Files |
| :--- | :--- | :--- |
| Maximum across 3 target boost maps | 2680 mbar absolute | 2650 mbar absolute |
| Approximate gauge boost (assuming 1000 mbar ambient) | 1.68 bar | 1.65 bar |
| Atmospheric boost limit map maximum | 2720 mbar | 2700 mbar |
| Single Value Boost Limit / SVBL (`0xF9C60`) | 2750 mbar | 2750 mbar (identical) |
| Rail single value limiters (`0xFD060` & `0xFD062`) | 1655 bar | 1648.5 bar |
| Rail maximum table (`0xFD1DC`, 96 cells) | All 1655 bar | All 1648.5 bar |
| Remaining bytes in checked rail region | Reference content | Identical |
| Main torque curve max (data start `0xE6DC2`) | 485 Nm | 515 Nm |
| Certain other torque curves max | 500 Nm | 550 Nm |
| Both Lambda / smoke maps | All 1.080 | Byte-identical |
| All 6 injector Duration regions | Reference content | Byte-identical |
| VNT region | Reference content | Byte-identical |
| SOI region | Reference content | 1,305 bytes different |
| Pilot injection region | Reference content | 459 bytes different |
| Per-gear torque limiters region | Reference content | 150 bytes different |
| Swirl flaps region | Reference content | 182 bytes different |
| Driver Wish / pedal region | Reference content | 64 bytes different |

Within the inspected rail range `0xFC98C–0xFD29C`, exactly 98 bytes differ. Every change corresponds solely to the raw value transition `16550 → 16485` across the two single limiters and the 96-cell maximum table.

**Despite filenames containing `pre_rail1700` and `stage3...rail`, no 1700 bar rail setting was found anywhere in the inspected rail regions.**

### Rail Table Boundary Warning

In the main report, the second rail data block starting at `0xFCE64` with 256 16-bit cells overlaps with the single-value limiters at `0xFD060/0xFD062`. Consequently, the observed `1655 → 1653.6` change in that window's maximum must not be interpreted as a separate rail target map change. Exact table dimensions and boundaries require independent verification.

## 5. Main Torque Curve Differences by RPM

Data start `0xE6DC2` (using the report's `× 0.1 Nm` factor). This curve is identical across all 10 variant files:

| RPM | Reference Stage 2 | Variant Files | Delta |
| ---: | ---: | ---: | ---: |
| 1500 RPM | 385 Nm | 438 Nm | +53 Nm |
| 1750 RPM | 425 Nm | 491 Nm | +66 Nm |
| 2000 RPM | 455 Nm | 515 Nm | +60 Nm |
| 2250 RPM | 480 Nm | 515 Nm | +35 Nm |
| 2500 RPM | 485 Nm | 515 Nm | +30 Nm |
| 3000 RPM | 485 Nm | 508 Nm | +23 Nm |
| 4000 RPM | 472 Nm | 495 Nm | +23 Nm |
| 4600 RPM | 445 Nm | 473 Nm | +28 Nm |
| 4800 RPM | 365 Nm | 378 Nm | +13 Nm |
| 4900 RPM | 315 Nm | 313 Nm | −2 Nm |
| 5020 RPM | 0 Nm | 0 Nm | 0 Nm |

Low-RPM torque limit increases are especially pronounced. Whether this is safe for a GM 5L40-E transmission cannot be established from file values alone; active protections, real delivered torque, and transmission health are decisive.

## 6. Rev Limiter / High-RPM Differences

Across all 10 variant files:

- The 4700 RPM cell of the 6th torque limiter is **`86.1 Nm`** instead of the reference's **`480 Nm`**.
- On the same curve, the 4600 RPM cell remains `525 Nm` and the 4950 RPM cell remains `0`.
- The final two RPM breakpoints of the 1st and 3rd torque-to-IQ (NM2IQ) maps are changed from **`4600 / 4950`** to **`4700 / 4701`**.

This high-RPM structure differs from Reference Stage 2. **Actual fuel-cut RPM, popcorn behavior, or kickdown interruption behavior is not verified by this comparison alone.**

## 7. Second Torque-to-Fuel (NM2IQ) Table Axis Differences

Last seven breakpoints of the axis identified as RPM in the main report:

| File / Group | Last Seven Breakpoints |
| :--- | :--- |
| Reference Stage 2 | `3000, 3500, 4000, 4200, 4400, 4600, 4950` |
| `bmw_e46_stage2.bin` | `6000, 7000, 8000, 8400, 8800, 9400, 9401` |
| `fix`, `pre_rail1700`, `pre_v2`, `pre_v3` | `3750, 4375, 5000, 5250, 5500, 5875, 5876` |
| `fix2`, `verified`, `stage3_fix2_rail`, `stage3_incremental`, `stage3b_iqb_only` | `3000, 3500, 4000, 4200, 4400, 4700, 4701` |

Raw 16-bit value at `0xE832C` (interpreted in the main report as the final torque axis point of the same table):

- Reference: `5150`
- `stage2.bin`: `10299`
- `fix`, `pre_rail1700`, `pre_v2`, `pre_v3`: `6437`
- `fix2`, `verified`, and the three `stage3*` files: `5150`

Whether these axis rescalings are deliberate or erroneous cannot be concluded without verifying the exact ECU function definitions and map selection logic. In particular, `bmw_e46_stage2.bin` should not be assumed to be a normal Stage 2 calibration.

## 8. Pairwise Differences Among Variant Files

| File Pair | Differing Bytes | Notes |
| :--- | ---: | :--- |
| `pre_rail1700` ↔ `pre_v2` | 8 | Four 16-bit values differ; rail region identical |
| `stage3_fix2_rail` ↔ `stage3_incremental` | 2 | Only `0xE6B38` raw value `17000 ↔ 18000`; rail region identical |
| `stage3_fix2_rail` ↔ `stage3b_iqb_only` | 187 | All within regions associated with EGR in the main report |
| `stage3_incremental` ↔ `stage3b_iqb_only` | 189 | The 187 bytes above plus `0xE6B38` |
| `stage2.bin` ↔ `pre_v3` | 96 | All within torque-to-IQ region |
| `stage2.bin` ↔ `fix` | 544 | EGR, torque-to-IQ, and four standalone 16-bit values |
| `stage2.bin` ↔ `fix2` | 612 | EGR, torque-to-IQ, and four standalone 16-bit values |
| `fix` ↔ `fix2` | 179 | EGR and torque-to-IQ regions |
| `stage2.bin` ↔ `verified` | 298 | EGR, torque-to-IQ, and region identified as DTC |
| `pre_v3` ↔ `verified` | 298 | EGR, torque-to-IQ, and region identified as DTC |
| `fix2` ↔ `verified` | 559 | Distinct variants; not the same file |

**`verified` is only a filename label; it does not imply verified checksums, vehicle testing, or power validation.**

## 9. Other Address Differences

Common changes present across all 10 variant files outside the primary map ranges:

| Address | Reference Hex | Variant Files Hex |
| :--- | :--- | :--- |
| `0xE4D56` | `4A70` | `0000` |
| `0xE4D62` | `41F1` | `0000` |
| `0xE4D6C` | `4B22` | `0000` |
| `0xEA0ED` | `00` | `64` |
| `0xEB31B` | `91` | `6B` |

In `bmw_e46_stage2_verified.bin`, `0xE4D52` (`4A71`) and `0xE4D76` (`4B33`) are additionally zeroed. The `0xE4Dxx` area is associated with DTC tables in the main report; which exact faults are affected has not been independently verified.

In several files, the following raw 16-bit values are changed `17000 → 18000`; without function verification they should not be labeled as specific pressure or protection thresholds:

| Address(es) | Files Containing the Change |
| :--- | :--- |
| `0xE38C4`, `0xE38F6`, `0xE6F6E` | `fix`, `fix2`, `pre_rail1700`, `stage3_fix2_rail`, `stage3_incremental`, `stage3b_iqb_only` |
| `0xE6B38` | `fix`, `fix2`, `pre_rail1700`, `stage3_incremental` |

No byte below `0xE0000` changed. Without verified memory layout or disassembly, this alone does not prove the functional effect of every modification.

## 10. SOI Definition and Checksum Warnings

### SOI

The SOI regions across all 10 variant files are identical to each other and differ from Reference Stage 2 by 1,305 bytes. However, applying the start addresses, dimensions, and scaling factor from the main report yields window maximums around `~175°`, which is inconsistent with the report's `~32°` claim.

**This does not mean actual engine injection timing is 175°; it indicates that the map start address, window boundary, signedness/encoding, or scaling definition must be re-verified.** Therefore, no conclusion is drawn that timing is "correct" or "optimized".

### Checksum

Two 32-bit fields listed as checksum fields in the main report:

| Address | Reference Stage 2 | All 10 Variant Files |
| :--- | :--- | :--- |
| `0xFEF74` | `337C0120` | `DF40BEBA` |
| `0xFEFF8` | `9A24ADB3` | `609B39E6` |

Across 10 distinct binaries with different payloads, both fields remain identical. While that alone does not conclusively prove invalid checksums without running the ECU algorithm, **no ECU-specific EDC16 checksum algorithm was executed and checksum validity is NOT verified.** Always verify/correct checksums with a proper EDC16 flashing tool or WinOLS before flashing.

## 11. Summary

Compared to Reference Stage 2 (`BMW_E46_320d_R70_216_Hybrid_Stage2.bin`), the 10 variant files in this folder feature:

- Higher main torque curve peak (`515 Nm` vs. `485 Nm`).
- Higher peak values on several other torque curves (`550 Nm` vs. `500 Nm`).
- Slightly lower target boost (`2650 mbar` vs. `2680 mbar` absolute).
- Lower rail pressure limiters (`1648.5 bar` vs. `1655 bar`).
- Identical injector duration, VNT, and Lambda regions.
- Different SOI, pilot injection, per-gear torque, and swirl flap regions.
- Altered high-RPM / NM2IQ axes and a torque limiter cell dropping to `86.1 Nm` at `4700 RPM`.

**Actual HP and torque were not measured. The ~235 HP figure in the main report is an unverified estimate, and no reliable HP number can be assigned to the variant files. None of these files are certified ready-to-flash or mechanically safe based solely on this comparison.**

Priority verification items before any vehicle use: NM2IQ axes and map selection, high-RPM torque drop, SOI map definitions, 2nd rail map boundaries, ECU-specific checksum validation, and live on-vehicle datalogging.
