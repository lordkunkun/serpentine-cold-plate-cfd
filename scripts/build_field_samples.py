#!/usr/bin/env python3
"""Create a compact, deterministic centroid sample from a surface VTU file."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import meshio
import numpy as np


def triangle_centroids_and_fields(
    path: Path,
    field_names: list[str],
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    mesh = meshio.read(path)
    centroid_blocks: list[np.ndarray] = []
    field_blocks = {name: [] for name in field_names}

    for block_index, block in enumerate(mesh.cells):
        if block.type != "triangle":
            continue
        centroid_blocks.append(mesh.points[block.data].mean(axis=1))
        for name in field_names:
            if name not in mesh.cell_data:
                raise KeyError(f"Field {name!r} is not present in {path}")
            field_blocks[name].append(np.asarray(mesh.cell_data[name][block_index]))

    if not centroid_blocks:
        raise ValueError(f"No triangle cells found in {path}")

    centroids = np.vstack(centroid_blocks)
    fields = {name: np.concatenate(blocks) for name, blocks in field_blocks.items()}
    return centroids, fields


def choose_rows(
    centroids: np.ndarray,
    fields: dict[str, np.ndarray],
    *,
    max_points: int,
    seed: int,
    x_min: float | None,
    x_max: float | None,
    y_min: float | None,
    y_max: float | None,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    keep = np.isfinite(centroids).all(axis=1)
    for values in fields.values():
        keep &= np.isfinite(values)
    if x_min is not None:
        keep &= centroids[:, 0] >= x_min
    if x_max is not None:
        keep &= centroids[:, 0] <= x_max
    if y_min is not None:
        keep &= centroids[:, 1] >= y_min
    if y_max is not None:
        keep &= centroids[:, 1] <= y_max

    centroids = centroids[keep]
    fields = {name: values[keep] for name, values in fields.items()}
    if len(centroids) == 0:
        raise ValueError("No cells remain after applying the requested bounds")

    if len(centroids) > max_points:
        rng = np.random.default_rng(seed)
        selected = np.sort(rng.choice(len(centroids), size=max_points, replace=False))
        centroids = centroids[selected]
        fields = {name: values[selected] for name, values in fields.items()}
    return centroids, fields


def write_csv(path: Path, centroids: np.ndarray, fields: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    names = ["x_m", "y_m", "z_m", *fields]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(names)
        for index, point in enumerate(centroids):
            writer.writerow(
                [
                    f"{point[0]:.9g}",
                    f"{point[1]:.9g}",
                    f"{point[2]:.9g}",
                    *[f"{fields[name][index]:.9g}" for name in fields],
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_vtu", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--field", action="append", required=True, dest="fields")
    parser.add_argument("--max-points", type=int, default=8000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--x-min", type=float)
    parser.add_argument("--x-max", type=float)
    parser.add_argument("--y-min", type=float)
    parser.add_argument("--y-max", type=float)
    args = parser.parse_args()

    centroids, fields = triangle_centroids_and_fields(args.input_vtu, args.fields)
    centroids, fields = choose_rows(
        centroids,
        fields,
        max_points=args.max_points,
        seed=args.seed,
        x_min=args.x_min,
        x_max=args.x_max,
        y_min=args.y_min,
        y_max=args.y_max,
    )
    write_csv(args.output_csv, centroids, fields)
    print(f"Wrote {len(centroids):,} sampled cells to {args.output_csv}")


if __name__ == "__main__":
    main()
