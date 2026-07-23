---
id: well-balancing
human_name: "Well-balancing"
kind: procedure
formula_ref: "docs/procedures.md §7"
---
## Applies to
Problems with a nontrivial `equilibrium` state (SPEC §4 split; typically `gravity`-bearing
hydrostatic setups).

## Inputs (slots)
- equilibrium reference (the IC).
- evolve time, `variables`, deviation tolerance.
- optional perturbation-preservation check.

## Steps / formula
Defined in `docs/procedures.md` §7. Initialize the `equilibrium`, evolve, and require the deviation
norm (`§1` norms of `u(t) − u_equilibrium`) to stay below tolerance. Optionally add the
`perturbation` and check it is transported/maintained rather than swamped by discrete equilibrium
error.

## Output form
Deviation norm(s) vs time; optional perturbation-preservation measure.

## Pass-criterion
Deviation below tolerance (well-balanced); perturbation preserved within tolerance.

## Refs
(none)
