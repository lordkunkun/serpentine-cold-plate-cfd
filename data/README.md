# Public Data

This folder contains the compact evidence used by the repository.

| File | Content |
|---|---|
| `case_config.json` | Reconstructed geometry, materials, boundaries, and solver protocol |
| `benchmark_targets.csv` | Table 5 target values transcribed from the cited paper |
| `q010_results.csv` | Promoted Design 4 literature comparison |
| `numerical_sensitivity.csv` | Mesh, hydraulic time-step, and steady thermal checks |
| `mesh_quality.csv` | Promoted mesh quality summary |
| `surface_temperature_stats.csv` | Area-weighted Fluent surface statistics |
| `field_samples/*.csv` | Deterministic downsampled Fluent surface fields |

The field samples contain triangle centroids and cell values from the promoted
surface VTU exports. They are derived visualization data, not complete solver
databases.

All temperatures are in kelvin, pressures in pascal, lengths in metre unless a
column name states otherwise.
