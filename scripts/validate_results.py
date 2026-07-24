#!/usr/bin/env python3
"""Validate the public scalar tables and statement boundaries."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def close_enough(left: float, right: float, tolerance: float = 0.02) -> bool:
    return math.isclose(left, right, abs_tol=tolerance)


def validate() -> list[str]:
    messages: list[str] = []
    config = json.loads((DATA / "case_config.json").read_text(encoding="utf-8"))
    results = pd.read_csv(DATA / "q010_results.csv").set_index("quantity")
    sensitivity = pd.read_csv(DATA / "numerical_sensitivity.csv")
    meshes = pd.read_csv(DATA / "mesh_quality.csv")
    targets = pd.read_csv(DATA / "benchmark_targets.csv")

    assert config["scope"]["flow_rate_sweep_completed"] is False
    assert config["scope"]["promoted_mass_flow_points"] == 1
    assert config["scope"]["experimental_validation"] is False
    messages.append("Scope: one promoted operating point; no experimental validation")

    design4 = targets.loc[targets["design"] == "Design 4"].iloc[0]
    pressure = results.loc["pressure_drop"]
    tmax = results.loc["maximum_temperature"]
    sigma = results.loc["full_top_surface_T_sigma"]

    assert close_enough(float(pressure["literature_value"]), float(design4["delta_p_Pa"]))
    assert close_enough(float(tmax["literature_value"]), float(design4["Tmax_K"]))
    assert close_enough(float(sigma["literature_value"]), float(design4["T_sigma_K"]))

    for name, row in (("pressure drop", pressure), ("maximum temperature", tmax)):
        recomputed = (
            (float(row["fluent_value"]) - float(row["literature_value"]))
            / float(row["literature_value"])
            * 100.0
        )
        assert close_enough(recomputed, float(row["error_percent"]))
        assert abs(recomputed) < 3.0
        assert row["assessment"] == "reproduced"
        messages.append(f"Primary metric: {name} = {recomputed:+.3f}%")

    assert sigma["assessment"] == "not_reproduced"
    assert abs(float(sigma["error_percent"])) > 20.0
    messages.append("T_sigma boundary: full-surface comparison remains open")

    observed = sensitivity["relative_change_percent"].abs()
    assert (observed <= sensitivity["criterion_percent"]).all()
    assert (sensitivity["status"] == "pass").all()
    messages.append(f"Numerical sensitivity: {len(sensitivity)} checks pass")

    assert (meshes["status"] == "pass").all()
    assert (meshes["minimum_orthogonal_quality"] >= 0.10).all()
    assert (meshes["cells_below_0_10"] == 0).all()
    messages.append(f"Mesh quality: {len(meshes)} promoted meshes pass")
    return messages


def main() -> None:
    for message in validate():
        print(f"PASS - {message}")


if __name__ == "__main__":
    main()
