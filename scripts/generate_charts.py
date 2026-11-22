#!/usr/bin/env python3
"""
Generate English dark-theme calibration and estimated dyno charts for the
BMW E46 320d (M47TU) Bosch EDC16C31 repository directly from the .bin files.

Outputs:
  - docs/dyno_curves.png
  - docs/calibration_overview.png
"""

import os
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ---------------------------------------------------------------------------
# Binary reading helpers (Bosch EDC16C31 — Big-Endian 16-bit)
# ---------------------------------------------------------------------------

def read_u16(data: bytes, addr: int, count: int) -> list[int]:
    return list(struct.unpack(f">{count}H", data[addr : addr + 2 * count]))


def read_s16(data: bytes, addr: int, count: int) -> list[int]:
    return list(struct.unpack(f">{count}h", data[addr : addr + 2 * count]))


def load_effective_torque(path: str, rpm_grid: np.ndarray) -> np.ndarray:
    """Return active ECU torque limit (Nm) = min(TL2, TL4_TCC, TL6_Rev, DW1_100%)."""
    data = open(path, "rb").read()

    # Main Torque Limiter 2 (EngPrt_trqLim1_CUR, 21x1)
    tl2_x = read_u16(data, 0x0E6D98, 21)
    tl2_y = [v * 0.1 for v in read_u16(data, 0x0E6DC2, 21)]

    # AT TCC Lock-Up Torque Limiter 4 (EngPrt_trqCBLim_CUR / trqLim1, 19x1)
    tl4_x = read_u16(data, 0x0E6E44, 19)
    tl4_y = [v * 0.1 for v in read_u16(data, 0x0E6E6A, 19)]

    # Rev Limiter / Normal Operating Torque Limit 6 (EngPrt_trqNLim_CUR, 21x1)
    tl6_x = read_u16(data, 0x0E6EF0, 21)
    tl6_y = [v * 0.1 for v in read_u16(data, 0x0E6F1A, 21)]

    # Driver Wish 1 at 100% pedal (AccPed_trqEngLow_MAP, 16x9)
    dw_x = read_u16(data, 0x0E0640, 16)
    dw_y = [read_s16(data, 0x0E0672 + r * 18 + 16, 1)[0] * 0.1 for r in range(16)]

    tl2 = np.interp(rpm_grid, tl2_x, tl2_y)
    tl4 = np.interp(rpm_grid, tl4_x, tl4_y)
    tl6 = np.interp(rpm_grid, tl6_x, tl6_y)
    dw = np.interp(rpm_grid, dw_x, dw_y)

    return np.minimum.reduce([tl2, tl4, tl6, dw])


def load_boost_curve(path: str) -> tuple[list[int], list[int]]:
    """Read max-IQ column of Target Boost Map 1 (PCR_pDesBas_MAP @ 0x0F9350)."""
    data = open(path, "rb").read()
    rpm_axis = read_u16(data, 0x0F9354, 16)
    max_col = [read_u16(data, 0x0F9394 + r * 32 + 30, 1)[0] for r in range(16)]
    return rpm_axis, max_col


def load_gear_limits(path: str) -> list[float]:
    """Read max torque limit (Nm) for Gears 1..5 (Gearbx_trqMaxGear1..5_CUR)."""
    data = open(path, "rb").read()
    bases = [0x0E943A, 0x0E94A0, 0x0E9506, 0x0E956C, 0x0E95D2]
    out = []
    for base in bases:
        n = read_u16(data, base, 1)[0]
        vals = [v * 0.1 for v in read_u16(data, base + 2 + 2 * n, n)]
        out.append(max(vals))
    return out


def load_duration_1600bar(path: str) -> tuple[list[float], list[int]]:
    """Read 1600 bar row from Injector Duration Map 1 (InjVCD_tiET_MAP @ 0x0F5300)."""
    data = open(path, "rb").read()
    rows, cols = read_u16(data, 0x0F5300, 2)
    rail_axis = read_u16(data, 0x0F5304, rows)
    iq_axis = [v * 0.01 for v in read_u16(data, 0x0F5304 + 2 * rows, cols)]
    ds = 0x0F5304 + 2 * rows + 2 * cols
    idx_1600 = min(range(rows), key=lambda i: abs(rail_axis[i] - 16000))
    row_us = read_u16(data, ds + idx_1600 * 2 * cols, cols)
    # Skip duplicate 0.0 column at index 1 for clean plotting
    pts = [(iq_axis[i], row_us[i]) for i in range(cols) if not (i == 1 and iq_axis[i] == 0.0)]
    return [p[0] for p in pts], [p[1] for p in pts]


# ---------------------------------------------------------------------------
# Styling constants (GitHub Dark aesthetic)
# ---------------------------------------------------------------------------

BG_FIG = "#0d1117"
BG_AX = "#131922"
GRID_COLOR = "#263040"
SPINE_COLOR = "#303c4d"
TEXT_MAIN = "#f0f6fc"
TEXT_MUTED = "#8b949e"

C_STOCK = "#94a3b8"   # Slate gray
C_S1 = "#38bdf8"      # Sky blue
C_S2 = "#4ade80"      # Emerald green
C_S3 = "#f59e0b"      # Amber gold
C_POP = "#fb7185"     # Coral red
C_BACKUP = "#a78bfa"  # Soft violet
C_BERAT = "#2dd4bf"   # Teal


def style_ax(ax):
    ax.set_facecolor(BG_AX)
    ax.grid(True, linestyle="--", linewidth=0.65, color=GRID_COLOR, alpha=0.85)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(SPINE_COLOR)
        spine.set_linewidth(0.9)
    ax.tick_params(colors=TEXT_MUTED, labelsize=9.5)


# ---------------------------------------------------------------------------
# Chart 1: Dyno / Estimated Power & ECU Torque Limiter Curves
# ---------------------------------------------------------------------------

def build_dyno_chart(out_path: str):
    # Fine RPM grid that includes every exact breakpoint (4600, 4700, 4790, 4800, 4900, 4950, 5020)
    rpm_pts = sorted(
        set(
            list(range(1000, 5021, 10))
            + [1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3500, 4000, 4200, 4400, 4600, 4700, 4790, 4800, 4900, 4950, 5020]
        )
    )
    rpm = np.array(rpm_pts, dtype=float)

    # Stock M47TU 150 HP reference (TL2 from 361811BMWEDC16.ols + OEM low-RPM ramp)
    stock_x = [1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3500, 4000, 4200, 4400, 4600, 4800, 4900, 4950, 5020]
    stock_y = [220.0, 275.0, 339.5, 348.2, 358.0, 362.3, 366.7, 367.9, 365.2, 347.5, 322.0, 309.3, 292.6, 274.5, 134.0, 106.8, 0.0, 0.0]
    trq_stock = np.interp(rpm, stock_x, stock_y)

    trq_s1 = load_effective_torque("BMW_E46_320d_R70_216_Hybrid_Stage1.bin", rpm)
    trq_s2 = load_effective_torque("BMW_E46_320d_R70_216_Hybrid_Stage2.bin", rpm)
    trq_s3 = load_effective_torque("BMW_E46_320d_R70_216_Hybrid_Stage3.bin", rpm)
    trq_pop = load_effective_torque("BMW_E46_320d_R70_216_Hybrid_Stage3_Popcorn_4800RPM.bin", rpm)

    # M47TU mechanical + pumping friction loss curve (Nm), calibrated so Stock 361811 = 150 HP @ 4000 RPM & 330 Nm peak
    fric_x = [1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3500, 4000, 4200, 4400, 4600, 4800, 5020]
    fric_y = [20.0, 22.0, 25.0, 28.0, 31.0, 34.0, 37.0, 41.0, 45.0, 52.0, 59.0, 62.0, 66.0, 70.0, 75.0, 80.0]
    fric = np.interp(rpm, fric_x, fric_y)

    def est_hp(trq_ecu: np.ndarray) -> np.ndarray:
        crank = np.where(trq_ecu > 0, np.maximum(0.0, trq_ecu - fric), 0.0)
        return crank * rpm / 7023.5

    hp_stock = est_hp(trq_stock)
    hp_s1 = est_hp(trq_s1)
    hp_s2 = est_hp(trq_s2)
    hp_s3 = est_hp(trq_s3)
    hp_pop = est_hp(trq_pop)

    fig, (ax_hp, ax_tq) = plt.subplots(1, 2, figsize=(16, 6.6), dpi=180)
    fig.patch.set_facecolor(BG_FIG)

    fig.suptitle(
        "BMW E46 320d (M47TÜ / BOSCH EDC16C31) — ECU TORQUE & ESTIMATED OUTPUT CURVES",
        color=TEXT_MAIN,
        fontsize=15,
        fontweight="bold",
        y=0.96,
    )
    fig.text(
        0.5,
        0.902,
        "Active ECU Torque Limiters (0x0E6DC2 / 0x0E6E6A / 0x0E6F1A)  |  R70 Pump + Bosch 216 Injectors + Hybrid Turbo + GM 5L40-E  |  Power Estimated (Unverified on Dyno)",
        ha="center",
        color=TEXT_MUTED,
        fontsize=9.3,
    )

    # Highlight GM 5L40-E TCC lock-up ramp zone on both panels
    for ax in (ax_hp, ax_tq):
        style_ax(ax)
        ax.axvspan(1500, 2100, color="#38bdf8", alpha=0.06, zorder=1)
        ax.axvline(4800, color=C_POP, linestyle="--", linewidth=1.4, alpha=0.85, zorder=2)

    # --- Left Panel: Estimated Crank Power (HP) ---
    ax_hp.set_title("ESTIMATED CRANK POWER (HP)", color=TEXT_MAIN, fontsize=11.5, fontweight="bold", pad=10)
    ax_hp.plot(rpm, hp_stock, color=C_STOCK, linestyle="--", linewidth=2.0, label="Stock OEM Ref (~150 HP / 330 Nm crank)")
    ax_hp.plot(rpm, hp_s1, color=C_S1, linestyle="-.", linewidth=2.3, label="Stage 1 (~207–216 HP / 440 Nm ECU)")
    ax_hp.plot(rpm, hp_s2, color=C_S2, linewidth=2.6, label="Stage 2 (~234–244 HP / 485 Nm ECU)")
    ax_hp.plot(rpm, hp_s3, color=C_S3, linewidth=2.6, label="Stage 3 (~250–262 HP / 515 Nm ECU)")

    # Plot Popcorn branch cleanly from 4400 RPM onwards so it stands out sharply
    pop_mask = rpm >= 4400
    ax_hp.plot(
        rpm[pop_mask],
        hp_pop[pop_mask],
        color=C_POP,
        linestyle=":",
        linewidth=2.8,
        label="Stage 3 + 4800 RPM Popcorn (4790→4800 Hardcut)",
        zorder=5,
    )
    ax_hp.scatter([4790], [hp_pop[rpm == 4790][0]], color=C_POP, s=36, zorder=6)

    ax_hp.set_xlabel("Engine Speed (RPM)", color=TEXT_MUTED, fontsize=10, labelpad=6)
    ax_hp.set_ylabel("Estimated Crank Power (HP)", color=TEXT_MUTED, fontsize=10, labelpad=6)
    ax_hp.set_xlim(1000, 5050)
    ax_hp.set_ylim(0, 315)
    ax_hp.xaxis.set_major_locator(mticker.MultipleLocator(500))
    ax_hp.legend(loc="upper left", facecolor="#161d27", edgecolor=SPINE_COLOR, labelcolor=TEXT_MAIN, fontsize=8.5, framealpha=0.94)
    ax_hp.text(
        1800,
        14,
        "GM 5L40-E TCC\nLock-Up Ramp",
        color="#7dd3fc",
        fontsize=8,
        ha="center",
        va="bottom",
        alpha=0.85,
    )
    ax_hp.text(
        4745,
        24,
        "4800 RPM\nPopcorn Hardcut",
        color=C_POP,
        fontsize=8.5,
        fontweight="bold",
        ha="right",
        va="bottom",
    )

    # --- Right Panel: Active ECU Torque Limiter (Nm) ---
    ax_tq.set_title("ACTIVE ECU TORQUE LIMITER (Nm)", color=TEXT_MAIN, fontsize=11.5, fontweight="bold", pad=10)
    ax_tq.plot(rpm, trq_stock, color=C_STOCK, linestyle="--", linewidth=2.0, label="Stock OEM Ref (368 Nm ECU / 330 Nm crank)")
    ax_tq.plot(rpm, trq_s1, color=C_S1, linestyle="-.", linewidth=2.3, label="Stage 1 (440 Nm ECU peak)")
    ax_tq.plot(rpm, trq_s2, color=C_S2, linewidth=2.6, label="Stage 2 (485 Nm ECU peak)")
    ax_tq.plot(rpm, trq_s3, color=C_S3, linewidth=2.6, label="Stage 3 (515 Nm ECU peak)")
    ax_tq.plot(
        rpm[pop_mask],
        trq_pop[pop_mask],
        color=C_POP,
        linestyle=":",
        linewidth=2.8,
        label="Stage 3 + 4800 RPM Popcorn (4790→4800: 0 Nm)",
        zorder=5,
    )
    ax_tq.scatter([4790], [trq_pop[rpm == 4790][0]], color=C_POP, s=36, zorder=6)

    ax_tq.set_xlabel("Engine Speed (RPM)", color=TEXT_MUTED, fontsize=10, labelpad=6)
    ax_tq.set_ylabel("ECU Indicated Torque Limit (Nm)", color=TEXT_MUTED, fontsize=10, labelpad=6)
    ax_tq.set_xlim(1000, 5050)
    ax_tq.set_ylim(0, 620)
    ax_tq.xaxis.set_major_locator(mticker.MultipleLocator(500))
    ax_tq.legend(loc="lower left", facecolor="#161d27", edgecolor=SPINE_COLOR, labelcolor=TEXT_MAIN, fontsize=8.5, framealpha=0.94)
    ax_tq.text(
        1800,
        560,
        "TCC Lock-Up\nRamp Zone",
        color="#7dd3fc",
        fontsize=8,
        ha="center",
        va="top",
        alpha=0.85,
    )
    ax_tq.text(
        4745,
        42,
        "4800 RPM\nHardcut (0 Nm)",
        color=C_POP,
        fontsize=8.5,
        fontweight="bold",
        ha="right",
        va="bottom",
    )

    plt.tight_layout(rect=[0.01, 0.01, 0.99, 0.87])
    fig.savefig(out_path, dpi=180, facecolor=BG_FIG)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Chart 2: Boost Targets, GM 5L40-E Per-Gear Limits & Injector Duration
# ---------------------------------------------------------------------------

def build_calibration_overview(out_path: str):
    fig, (ax_boost, ax_gear, ax_dur) = plt.subplots(1, 3, figsize=(18, 6.0), dpi=180)
    fig.patch.set_facecolor(BG_FIG)

    fig.suptitle(
        "BMW E46 320d (EDC16C31) — BOOST, GM 5L40-E GEAR PROTECTION & INJECTOR DURATION",
        color=TEXT_MAIN,
        fontsize=14.5,
        fontweight="bold",
        y=0.96,
    )
    fig.text(
        0.5,
        0.90,
        "Raw Byte-Verified Calibration Curves Directly Extracted from Repository .bin Files (Zero Extrapolation)",
        ha="center",
        color=TEXT_MUTED,
        fontsize=9.3,
    )

    for ax in (ax_boost, ax_gear, ax_dur):
        style_ax(ax)

    # --- Panel 1: Target Boost vs. Stock 3-Bar MAP Ceiling ---
    ax_boost.set_title("TARGET BOOST vs. 3-BAR MAP CEILING", color=TEXT_MAIN, fontsize=10.5, fontweight="bold", pad=10)
    for label, fn, col, ls, lw in [
        ("bmw backup (2592 mbar)", "bmw backup.bin", C_BACKUP, "--", 1.8),
        ("berat son (2650 mbar)", "berat son 19.10.2026", C_BERAT, ":", 1.9),
        ("Stage 1 (2600 mbar)", "BMW_E46_320d_R70_216_Hybrid_Stage1.bin", C_S1, "-.", 2.2),
        ("Stage 2 (2680 mbar)", "BMW_E46_320d_R70_216_Hybrid_Stage2.bin", C_S2, "-", 2.4),
        ("Stage 3 (2780 mbar)", "BMW_E46_320d_R70_216_Hybrid_Stage3.bin", C_S3, "-", 2.5),
    ]:
        rx, by = load_boost_curve(fn)
        # Plot from 1000 RPM upward
        pts = [(r, b) for r, b in zip(rx, by) if r >= 1000]
        ax_boost.plot([p[0] for p in pts], [p[1] for p in pts], color=col, linestyle=ls, linewidth=lw, label=label)

    ax_boost.axhline(3000, color=C_POP, linestyle="--", linewidth=1.6, label="Stock 3-Bar MAP Ceiling (3000 mbar)")
    ax_boost.axhspan(2850, 3000, color=C_POP, alpha=0.09)
    ax_boost.text(4680, 2975, "3000 mbar Sensor Limit", color=C_POP, fontsize=8, fontweight="bold", ha="right", va="top")
    ax_boost.text(4680, 2862, "Stage 3 SVBL (2850)", color="#fca5a5", fontsize=7.6, ha="right", va="bottom")
    ax_boost.set_xlabel("Engine Speed (RPM)", color=TEXT_MUTED, fontsize=9.5)
    ax_boost.set_ylabel("Absolute Boost Target (mbar)", color=TEXT_MUTED, fontsize=9.5)
    ax_boost.set_xlim(1000, 4800)
    ax_boost.set_ylim(1400, 3150)
    ax_boost.legend(loc="lower right", facecolor="#161d27", edgecolor=SPINE_COLOR, labelcolor=TEXT_MAIN, fontsize=7.8, framealpha=0.94)

    # --- Panel 2: GM 5L40-E Per-Gear Torque Limits ---
    ax_gear.set_title("GM 5L40-E PER-GEAR TORQUE LIMITS", color=TEXT_MAIN, fontsize=10.5, fontweight="bold", pad=10)
    gears = np.arange(5)
    gear_labels = ["1st Gear\n(Launch)", "2nd Gear", "3rd Gear", "4th Gear\n(Direct)", "5th Gear\n(Overdrive)"]

    g_bak = load_gear_limits("bmw backup.bin")
    g_s1 = load_gear_limits("BMW_E46_320d_R70_216_Hybrid_Stage1.bin")
    g_s2 = load_gear_limits("BMW_E46_320d_R70_216_Hybrid_Stage2.bin")
    g_s3 = load_gear_limits("BMW_E46_320d_R70_216_Hybrid_Stage3.bin")

    w = 0.20
    b0 = ax_gear.bar(gears - 1.5 * w, g_bak, width=w, color=C_BACKUP, alpha=0.55, edgecolor=C_BACKUP, label="bmw backup (600 Nm Unprotected)")
    b1 = ax_gear.bar(gears - 0.5 * w, g_s1, width=w, color=C_S1, alpha=0.90, label="Stage 1 (400–440 Nm)")
    b2 = ax_gear.bar(gears + 0.5 * w, g_s2, width=w, color=C_S2, alpha=0.90, label="Stage 2 (420–485 Nm)")
    b3 = ax_gear.bar(gears + 1.5 * w, g_s3, width=w, color=C_S3, alpha=0.90, label="Stage 3 (440–515 Nm)")

    for bars, col in [(b1, "#bae6fd"), (b2, "#bbf7d0"), (b3, "#fde68a")]:
        for bar in bars:
            h = bar.get_height()
            ax_gear.text(
                bar.get_x() + bar.get_width() / 2,
                h + 7,
                f"{int(round(h))}",
                ha="center",
                va="bottom",
                color=col,
                fontsize=7.2,
                fontweight="bold",
            )

    ax_gear.set_xticks(gears)
    ax_gear.set_xticklabels(gear_labels, fontsize=8.5)
    ax_gear.set_ylabel("Gear Torque Limit (Nm)", color=TEXT_MUTED, fontsize=9.5)
    ax_gear.set_ylim(0, 810)
    ax_gear.legend(loc="upper right", facecolor="#161d27", edgecolor=SPINE_COLOR, labelcolor=TEXT_MAIN, fontsize=7.8, framealpha=0.95)

    # --- Panel 3: Injector Duration @ 1600 bar (131 Inflated vs. Bosch 216) ---
    ax_dur.set_title("INJECTOR DURATION @ 1600 BAR (0x0F5364)", color=TEXT_MAIN, fontsize=10.5, fontweight="bold", pad=10)
    iq_bak, us_bak = load_duration_1600bar("bmw backup.bin")
    iq_216, us_216 = load_duration_1600bar("BMW_E46_320d_R70_216_Hybrid_Stage2.bin")

    ax_dur.plot(iq_bak, us_bak, color=C_POP, linewidth=2.5, linestyle="--", marker="o", markersize=3.5, label="bmw backup.bin (+15% Inflated 131 Inj.)")
    ax_dur.plot(iq_216, us_216, color=C_S2, linewidth=2.6, marker="s", markersize=3.5, label="Stage 1/2/3 (True Bosch 216 Calibration)")

    # Shade over-fueling mismatch zone between 60 and 90 mg/str
    iq_common = np.linspace(57.5, 90.0, 60)
    us_bak_i = np.interp(iq_common, iq_bak, us_bak)
    us_216_i = np.interp(iq_common, iq_216, us_216)
    ax_dur.fill_between(iq_common, us_216_i, us_bak_i, color=C_POP, alpha=0.16)

    # Annotate exact 75 mg/str & 85 mg/str delta
    ax_dur.annotate(
        "+39% open time\n(1194 vs 861 µs)",
        xy=(75, 1194),
        xytext=(50, 1265),
        color="#fda4af",
        fontsize=8,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=C_POP, lw=1.2),
    )
    ax_dur.annotate(
        "216: 95 mg = 1032 µs",
        xy=(95, 1032),
        xytext=(57, 600),
        color="#86efac",
        fontsize=8,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=C_S2, lw=1.2),
    )

    ax_dur.set_xlabel("Commanded Fuel Mass (mg/str)", color=TEXT_MUTED, fontsize=9.5)
    ax_dur.set_ylabel("Injector Opening Duration (µs)", color=TEXT_MUTED, fontsize=9.5)
    ax_dur.set_xlim(10, 98)
    ax_dur.set_ylim(250, 1520)
    ax_dur.legend(loc="upper left", facecolor="#161d27", edgecolor=SPINE_COLOR, labelcolor=TEXT_MAIN, fontsize=7.8, framealpha=0.94)

    plt.tight_layout(rect=[0.01, 0.01, 0.99, 0.865])
    fig.savefig(out_path, dpi=180, facecolor=BG_FIG)
    plt.close(fig)


def main():
    os.makedirs("docs", exist_ok=True)
    build_dyno_chart(os.path.join("docs", "dyno_curves.png"))
    build_calibration_overview(os.path.join("docs", "calibration_overview.png"))
    print("Generated docs/dyno_curves.png and docs/calibration_overview.png")


if __name__ == "__main__":
    main()
