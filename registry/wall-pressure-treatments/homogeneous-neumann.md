---
id: homogeneous-neumann
human_name: "Naive homogeneous Neumann on pressure (n·grad p = 0)"
kind: wall-pressure-treatment
---
## Definition
The reference imposed `n·∇p = 0` at a perfectly-conducting wall — the zero-Lorentz-force
approximation of the force-balance condition (`force-balance`). Correct only where `n·(J × B)`
vanishes at the wall; elsewhere it perturbs the near-wall equilibrium and can drive a spurious
boundary layer.

## Params schema
None.

## Notes
Recorded per reference in `reference_results[].wall_pressure_bc` — a method choice, never part of
the problem block (SPEC §1.6).

## Refs
(none)
