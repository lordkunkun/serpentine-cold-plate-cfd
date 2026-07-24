# Limitations and Intended Use

## What the repository supports

- An independent Fluent reconstruction of the public Design 4 operating point.
- Close agreement with the literature pressure drop and maximum temperature.
- Engineering mesh-sensitivity evidence for the promoted quantities.
- A hydraulic time-step check and a separate steady thermal continuation check.
- Traceable, area-weighted surface-temperature statistics.
- A compact portfolio example of geometry reconstruction, source and boundary
  bookkeeping, solver control, post-processing, and evidence-based reporting.

## What it does not support

- The original authors' CAD or STAR-CCM+ project has not been recovered.
- The paper's exact temperature-standard-deviation report surface is unknown.
- No experiment, manufacturer data, or real battery-pack measurement is
  included.
- The model is not validated for product sign-off, warranty, certification, or
  production release.
- The public repository does not contain the full Fluent case/data files.
- The 0.010 kg/s baseline is the only promoted operating point. A flow-rate
  sweep and multi-objective optimization remain future work.
- The paper's six-design target table is included for context; this repository
  does not claim that every design has been independently validated in Fluent.

## Modeling assumptions

- Water properties are fixed at the documented baseline values.
- The flow is modeled as laminar.
- Exterior surfaces other than the heated bottom are adiabatic.
- Battery cells, thermal-interface material, contact resistance, manufacturing
  tolerances, and external heat loss are outside the reconstructed model.
- The short hydraulic transient is used to audit pressure-drop numerics, not to
  describe pack warm-up or long-time battery behavior.

## Data policy

The full promoted Fluent case and data files total roughly 1.27 GB. Large
solver files, meshes, and internal debugging artifacts are excluded from Git to
keep the repository reviewable. The included field files are deterministic
surface samples generated from the authoritative HDF5 result.

Anyone using the scalar tables should preserve the named extraction object,
weighting method, operating point, and comparison scope. In particular, the
diagnostic battery-contact candidates must not be relabeled as the authors'
original report surface without new evidence.
