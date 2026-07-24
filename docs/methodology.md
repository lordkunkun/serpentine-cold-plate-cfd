# Methodology

## 1. Reconstruction target

The target is Design 4 from Table 5 of Jayarajan and Azimov (2023): a
nine-channel zig-zag serpentine cold plate operated at 0.010 kg/s coolant mass
flow. The paper supplies the design family, operating conditions, and scalar
targets, but not the native STAR-CCM+ project, exact CAD, or report-object
definitions.

The model was therefore treated as an independent reconstruction. Dimensions
and boundary conditions were taken from the public paper; hidden fillets,
contact footprints, and solver-native report surfaces were not inferred as
known facts.

## 2. Geometry and domains

The reconstructed plate footprint is 340 mm by 310 mm with a 5 mm total
thickness. The coolant channel is 12 mm wide and 2 mm deep. Design 4 uses nine
passes with a nominal zig-zag amplitude of 10 mm and pitch of 36 mm.

The model contains:

- one water domain;
- one aluminum solid domain;
- a coupled fluid-solid interface;
- inlet and outlet extensions used to keep the pressure boundaries away from
  the cold-plate footprint;
- a bottom heat-flux surface and adiabatic remaining exterior surfaces.

The reconstructed geometry is traceable, but it is not the authors' original
CAD.

## 3. Boundary and source ledger

| Boundary or source | Type | Value |
|---|---|---:|
| Coolant inlet | Mass-flow inlet | 0.010 kg/s |
| Inlet temperature | Thermal inlet | 300 K |
| Coolant outlet | Pressure outlet | 0 Pa gauge |
| Plate bottom | Heat-flux boundary | 7000 W/m2 |
| Fluid-solid interface | Coupled wall | Conservative heat transfer |
| Other exterior walls | Adiabatic wall | 0 W/m2 |

The heated bottom area is 0.1054 m2, giving an imposed heat-input ledger of
737.8 W. The water density is 997 kg/m3 and the fixed dynamic viscosity is
0.000797 Pa s. The viscosity choice was kept explicit because pressure drop in
this case is materially sensitive to it.

## 4. Mesh route

The Fluent Meshing route used a polyhedral core and one local prism layer in
the promoted reconstruction. The two compared meshes kept the same geometry,
zone map, material points, prism-layer scope, cells-per-gap control, and solver
protocol.

| Mesh | Total cells | Prism/poly cells | Minimum orthogonal quality | Cells below 0.10 |
|---|---:|---:|---:|---:|
| Mesh A | 5,495,768 | 778,258 | 0.102 | 0 |
| Mesh B | 5,791,456 | 822,566 | 0.101 | 0 |

This is an engineering mesh-sensitivity comparison of the finest controlled
pair. It is not a three-grid Richardson extrapolation or Grid Convergence Index
study, and it is not recovery of the paper's native STAR-CCM+ mesh.

## 5. Solver protocol

### Thermal branch

The main heat-transfer calculation is steady conjugate heat transfer in ANSYS
Fluent. The energy equation is active in both the water and aluminum domains.
The flow is laminar, and pressure-velocity coupling uses SIMPLE.

The thermal case was initialized from a developed hydraulic state, solved for
20 iterations after enabling the thermal setup, and then continued to 100
thermal iterations. Maximum temperature changed by -0.0610% from the early
thermal state to the continued state.

### Hydraulic branch

Pressure-drop sensitivity was checked with a first-order transient hydraulic
solve. Two time steps, 5e-5 s and 1e-4 s, were compared at the same physical
time of 0.008 s. The pressure-drop difference was 0.1128%.

The short transient branch is a numerical pressure-drop audit. It is not used
to claim a time-resolved battery heating process.

## 6. Monitored quantities

The promoted quantities were defined before the final comparison:

- inlet-to-outlet pressure drop;
- global maximum temperature;
- coolant outlet temperature;
- imposed heat input;
- inlet/outlet mass balance;
- fluid-solid interface temperature difference;
- area-weighted surface temperature standard deviation.

The area-weighted temperature standard deviation is

$$
T_{\mathrm{sigma}} =
\sqrt{
\frac{\int_A (T-T_{\mathrm{mean}})^2\,dA}
{\int_A dA}
}.
$$

Face areas were reconstructed from Fluent case topology and matched against
Fluent surface-area reports before the statistic was used.

## 7. Evidence chain

The full internal project retains Fluent case/data HDF5 files, solver
transcripts, mesh transcripts, and source ledgers. This public repository keeps
the smaller evidence needed to audit the published claims:

1. source-original literature targets;
2. promoted scalar result tables;
3. mesh, time-step, and steady-protocol comparisons;
4. surface statistics with the extraction object named;
5. deterministic downsampled field extracts;
6. scripts that validate the tables and regenerate the figures.

See [validation.md](validation.md) for the acceptance logic and
[limitations.md](limitations.md) for the statement boundary.
