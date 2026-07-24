# Validation and Numerical Evidence

## Acceptance logic

This project separates three questions:

1. Did the solver produce a stable, internally explainable result?
2. Are the promoted quantities insensitive to the tested mesh and solver
   protocol?
3. Do the same quantities agree with the literature target?

Passing one question does not automatically pass the others.

## Literature comparison

For the promoted q010 baseline, the project used a 3% reproduction tolerance
for maximum temperature and pressure drop.

| Quantity | Literature | Fluent | Error | Result |
|---|---:|---:|---:|---|
| Pressure drop | 9386 Pa | 9550.5973 Pa | +1.753% | pass |
| Maximum temperature | 318.21 K | 321.49101 K | +1.031% | pass |
| Full top-surface T_sigma | 3.90 K | 4.933507821 K | +26.500% | fail |

The local heat input is 737.79972 W. Comparing it with the paper's 703 W
heat-transfer entry gives +4.95%, but the two quantities may not use the same
report object. It is retained as an energy-ledger comparison, not promoted as a
closed benchmark.

## Mesh sensitivity

The controlled mesh comparison changes only mesh density within the same
reconstruction route.

| Quantity | Mesh A | Mesh B | Relative change |
|---|---:|---:|---:|
| Pressure drop | 9550.5973 Pa | 9471.6628 Pa | -0.8265% |
| Maximum temperature | 321.49101 K | 321.45461 K | -0.0113% |
| Coolant outlet temperature | 317.68550 K | 317.68808 K | +0.0008% |
| Heat input | 737.79972 W | 737.80000 W | +0.00004% |
| Interface temperature difference | 0.15563 K | 0.15606 K | +0.276% |
| Full top-surface T_sigma | 4.933507821 K | 4.933537449 K | +0.0006% |

The primary quantities are insensitive to the tested pair. The result supports
an engineering mesh-sensitivity statement, not formal asymptotic convergence.

## Time-step and steady-protocol checks

The hydraulic time-step check compares the same mesh and physical end time:

| Time step | Steps x inner iterations | Physical time | Pressure drop |
|---:|---:|---:|---:|
| 5e-5 s | 160 x 5 | 0.008 s | 9471.6628 Pa |
| 1e-4 s | 80 x 5 | 0.008 s | 9482.3454 Pa |

The difference is +0.1128%.

The thermal calculation is steady. Its continuation check is:

| Thermal state | Maximum temperature | Outlet temperature |
|---|---:|---:|
| Initial 20 thermal iterations | 321.65068 K | 317.65547 K |
| Continued to 100 thermal iterations | 321.45461 K | 317.68808 K |

Maximum temperature changes by -0.0610%. Calling this a thermal time-step
independence study would be incorrect; it is a steady iteration/protocol
stability check.

## Internal closure

For the promoted thermal case:

- energy residual: approximately 2.6e-6;
- inlet mass flow: 0.0099999903 kg/s;
- outlet mass flow: -0.0099996113 kg/s;
- net mass flow: 3.79e-7 kg/s;
- imposed bottom heat input: 737.8 W;
- fluid-solid interface mean temperature difference: 0.156 K.

The thermal continuity residual remains relatively high, so the case is not
presented as validated from residuals alone. Mass balance, energy behavior,
target monitors, mesh sensitivity, and physical fields are read together.

## Temperature-uniformity audit

The full top-surface statistic is numerically stable but does not match the
paper. Several physically plausible battery-contact footprints produce values
near 3.90 K, which indicates that the metric is report-surface dependent.
Because the paper does not publish the exact contact footprint or STAR-CCM+
report object, those candidate surfaces remain diagnostic.

The public conclusion is therefore:

> Pressure drop and maximum temperature are closely reproduced for the q010
> baseline. Full-surface temperature standard deviation is numerically stable
> but not literature-matched because the benchmark report surface is not
> sufficiently specified.
