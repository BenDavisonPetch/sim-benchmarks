---
id: hydro
human_name: "Hydrodynamics (compressible Euler base)"
phase: fluid
requires_eos: true
velocity: evolved
evolves: [rho, v, E]            # mass, momentum, total energy
interchangeable_with: []
interchangeable_when: null
---
## Definition
Compressible fluid-dynamics base: the Euler equations for mass, momentum, and total energy. Closed
by an equation of state (`requires_eos: true`). With **no terms** this base is the inviscid Euler
system; adding term toggles builds the Navier–Stokes family (§7.1 `base` semantics).

## Params schema
None intrinsic to the base. Thermodynamic closure is the material's `eos` (required). Physical
terms enter via the independent `terms` toggles, each param-bearing when present:
- `+ viscosity` (+ optional `heat-conduction`) = **Navier–Stokes**.
- `+ gravity` = self-/externally-gravitating hydro.

## Notes
Single-material hydro tests still use a 1-element `materials` list. Euler = `hydro` with `terms: []`.
Terms are independent toggles (§7.1), so viscous vs inviscid are **different entries** (term
presence forks identity, §2.3).

## Refs
(none)
