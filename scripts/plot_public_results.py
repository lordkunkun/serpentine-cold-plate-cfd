#!/usr/bin/env python3
"""Regenerate the public figures from the repository data."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"

INK = "#16202f"
MUTED = "#657184"
TEAL = "#007f73"
BLUE = "#1976d2"
ORANGE = "#e67e22"
RED = "#c53b3b"
GRID = "#dce3ea"


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "text.color": INK,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def triangular_row(
    x_start: float,
    x_end: float,
    y: float,
    amplitude: float,
    pitch: float,
) -> list[tuple[float, float]]:
    direction = 1.0 if x_end >= x_start else -1.0
    length = abs(x_end - x_start)
    half_pitch = 0.5 * pitch
    steps = max(1, int(math.ceil(length / half_pitch)))
    points = [(x_start, y)]
    sign = 1.0
    for index in range(1, steps):
        x = x_start + direction * min(index * half_pitch, length)
        offset = sign * amplitude if index % 2 else 0.0
        points.append((x, y + offset))
        if index % 2 == 0:
            sign *= -1.0
    points.append((x_end, y))
    return points


def serpentine_centerline(config: dict[str, float | int]) -> np.ndarray:
    length = float(config["plate_length_mm"])
    width = float(config["plate_width_mm"])
    count = int(config["channel_count"])
    margin = float(config["edge_margin_mm"])
    amplitude = float(config["zigzag_amplitude_mm"])
    pitch = float(config["zigzag_pitch_mm"])
    y_values = np.linspace(margin, width - margin, count)
    left = margin
    right = length - margin

    points: list[tuple[float, float]] = [(0.0, y_values[0]), (left, y_values[0])]
    moving_right = True
    for index, y in enumerate(y_values):
        start, end = (left, right) if moving_right else (right, left)
        if points[-1] != (start, y):
            points.append((start, y))
        points.extend(triangular_row(start, end, y, amplitude, pitch)[1:])
        if index < len(y_values) - 1:
            points.append((end, y_values[index + 1]))
        moving_right = not moving_right
    points.append((length, y_values[-1]))
    return np.asarray(points)


def plot_geometry(config: dict) -> None:
    geometry = config["geometry"]
    boundaries = config["boundaries"]
    length = geometry["plate_length_mm"]
    width = geometry["plate_width_mm"]
    centerline = serpentine_centerline(geometry)

    fig, (ax, bx) = plt.subplots(
        1,
        2,
        figsize=(13.0, 6.3),
        gridspec_kw={"width_ratios": [1.42, 1.0]},
        constrained_layout=True,
    )
    plate = Rectangle((0, 0), length, width, facecolor="#f3f6f8", edgecolor=INK, lw=1.7)
    ax.add_patch(plate)
    ax.plot(
        centerline[:, 0],
        centerline[:, 1],
        color="#9bd6c7",
        lw=11,
        solid_capstyle="round",
        solid_joinstyle="round",
    )
    ax.plot(centerline[:, 0], centerline[:, 1], color=TEAL, lw=1.2, alpha=0.95)
    ax.scatter(*centerline[0], s=60, color=BLUE, zorder=5)
    ax.scatter(*centerline[-1], s=60, color="#6f42c1", zorder=5)
    ax.annotate(
        f"Inlet\n{boundaries['inlet_mass_flow_kg_s']:.3f} kg/s, "
        f"{boundaries['inlet_temperature_K']:.0f} K",
        xy=centerline[0],
        xytext=(30, 48),
        arrowprops={"arrowstyle": "->", "color": BLUE, "lw": 1.8},
        color=BLUE,
        fontsize=10,
        weight="semibold",
    )
    ax.annotate(
        "Outlet\n0 Pa gauge",
        xy=centerline[-1],
        xytext=(250, 275),
        arrowprops={"arrowstyle": "->", "color": "#6f42c1", "lw": 1.8},
        color="#6f42c1",
        fontsize=10,
        weight="semibold",
    )
    ax.text(
        length / 2,
        -22,
        f"{length:.0f} mm",
        ha="center",
        va="center",
        color=MUTED,
    )
    ax.text(
        -24,
        width / 2,
        f"{width:.0f} mm",
        ha="center",
        va="center",
        rotation=90,
        color=MUTED,
    )
    ax.set(
        xlim=(-42, length + 18),
        ylim=(-40, width + 18),
        aspect="equal",
        xlabel="x [mm]",
        ylabel="y [mm]",
        title="Nine-channel plan-view reconstruction",
    )
    ax.grid(color=GRID, lw=0.6, alpha=0.65)
    ax.set_axisbelow(True)

    base = np.array([[0.08, 0.18], [0.64, 0.18], [0.90, 0.32], [0.34, 0.32]])
    layers = [
        (0.00, "#f8c7be", RED, "7000 W/m2 heat flux"),
        (0.12, "#b9d8ff", BLUE, "Aluminum lower plate"),
        (0.24, "#bfead7", TEAL, "Water channel + coupled interface"),
        (0.36, "#e3e8ee", MUTED, "Aluminum upper plate"),
    ]
    for offset, fill, edge, label in layers:
        polygon = base.copy()
        polygon[:, 1] += offset
        bx.add_patch(Polygon(polygon, closed=True, facecolor=fill, edgecolor=edge, lw=1.6))
        bx.text(0.53, polygon[:, 1].mean(), label, ha="center", va="center", fontsize=10)
    bx.annotate(
        "Heat leaves through the coolant",
        xy=(0.50, 0.49),
        xytext=(0.04, 0.76),
        arrowprops={"arrowstyle": "->", "lw": 1.8, "color": ORANGE},
        color=ORANGE,
        weight="semibold",
    )
    bx.text(
        0.5,
        0.05,
        "Independent reconstruction from public dimensions\n"
        "Original CAD and report surfaces were not available",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=9,
    )
    bx.set(xlim=(0, 1), ylim=(0, 0.95), title="Thermal-domain and boundary ledger")
    bx.axis("off")
    fig.suptitle("Serpentine cold-plate baseline", fontsize=17, weight="bold")
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "geometry_boundary_conditions.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_fields() -> None:
    temperature = pd.read_csv(DATA / "field_samples" / "solid_top_temperature.csv")
    pressure = pd.read_csv(DATA / "field_samples" / "fluid_interface_pressure.csv")

    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.2), constrained_layout=True)
    panels = [
        (axes[0], temperature, "temperature_K", "inferno", "Temperature [K]", "Solid top temperature"),
        (axes[1], pressure, "pressure_Pa", "viridis", "Gauge pressure [Pa]", "Fluid-side interface pressure"),
    ]
    for ax, frame, field, cmap, colorbar_label, title in panels:
        contour = ax.tricontourf(
            frame["x_m"],
            frame["y_m"],
            frame[field],
            levels=18,
            cmap=cmap,
        )
        ax.tricontour(
            frame["x_m"],
            frame["y_m"],
            frame[field],
            levels=10,
            colors="white",
            linewidths=0.28,
            alpha=0.42,
        )
        colorbar = fig.colorbar(contour, ax=ax, pad=0.02)
        colorbar.set_label(colorbar_label)
        ax.set(
            xlabel="x [m]",
            ylabel="y [m]",
            title=title,
            aspect="equal",
        )
        ax.grid(color="white", lw=0.35, alpha=0.35)
    fig.suptitle("Sampled fields from the promoted Fluent result", fontsize=16, weight="bold")
    fig.savefig(FIGURES / "field_overview.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_benchmark() -> None:
    frame = pd.read_csv(DATA / "q010_results.csv")
    labels = {
        "pressure_drop": "Pressure drop",
        "maximum_temperature": "Maximum temperature",
        "heat_input_vs_reported_transfer": "Heat ledger",
        "full_top_surface_T_sigma": "Full-surface T_sigma",
    }
    colors = {
        "reproduced": TEAL,
        "ledger_only": ORANGE,
        "not_reproduced": RED,
    }
    y = np.arange(len(frame))
    errors = frame["error_percent"].abs().to_numpy()

    fig, ax = plt.subplots(figsize=(10.2, 4.8), constrained_layout=True)
    bars = ax.barh(
        y,
        errors,
        color=[colors[value] for value in frame["assessment"]],
        height=0.58,
    )
    ax.axvline(3, color=BLUE, ls="--", lw=1.3, label="3% primary-metric target")
    ax.axvline(5, color=ORANGE, ls=":", lw=1.3, label="5% ledger reference")
    ax.set_yticks(y, [labels[value] for value in frame["quantity"]])
    ax.invert_yaxis()
    ax.set(
        xlabel="Absolute difference from literature [%]",
        title="Design 4 literature comparison",
        xlim=(0, max(errors) * 1.18),
    )
    ax.grid(axis="x", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    for bar, error, assessment in zip(bars, errors, frame["assessment"]):
        ax.text(
            error + 0.35,
            bar.get_y() + bar.get_height() / 2,
            f"{error:.2f}%  {assessment.replace('_', ' ')}",
            va="center",
            fontsize=9,
        )
    ax.legend(loc="upper right", frameon=False)
    fig.savefig(FIGURES / "benchmark_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_sensitivity() -> None:
    frame = pd.read_csv(DATA / "numerical_sensitivity.csv")
    frame["gate_fraction_percent"] = (
        frame["relative_change_percent"].abs() / frame["criterion_percent"] * 100.0
    )
    label_map = {
        "pressure_drop": "pressure drop",
        "maximum_temperature": "maximum temperature",
        "outlet_temperature": "outlet temperature",
        "heat_input": "heat input",
        "interface_temperature_difference": "interface delta T",
        "full_top_surface_T_sigma": "full-surface T_sigma",
    }
    check_map = {
        "mesh_A_to_B": "mesh",
        "hydraulic_time_step": "hydraulic dt",
        "steady_thermal_continuation": "steady continuation",
    }
    labels = [
        f"{check_map[row.check]}: {label_map[row.quantity]}"
        for row in frame.itertuples()
    ]
    y = np.arange(len(frame))

    fig, ax = plt.subplots(figsize=(11.0, 6.2), constrained_layout=True)
    bars = ax.barh(y, frame["gate_fraction_percent"], color=TEAL, height=0.60)
    ax.axvline(100, color=RED, ls="--", lw=1.4, label="declared criterion")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set(
        xlabel="Observed change as a fraction of its acceptance criterion [%]",
        title="Numerical sensitivity checks",
        xlim=(0, 110),
    )
    ax.grid(axis="x", color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    for bar, change in zip(bars, frame["relative_change_percent"]):
        x = max(bar.get_width() + 1.0, 3.0)
        ax.text(
            x,
            bar.get_y() + bar.get_height() / 2,
            f"{change:+.4g}%",
            va="center",
            fontsize=8.5,
        )
    ax.legend(loc="lower right", frameon=False)
    fig.savefig(FIGURES / "numerical_sensitivity.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    set_style()
    config = json.loads((DATA / "case_config.json").read_text(encoding="utf-8"))
    plot_geometry(config)
    plot_fields()
    plot_benchmark()
    plot_sensitivity()
    print(f"Generated public figures in {FIGURES}")


if __name__ == "__main__":
    main()
