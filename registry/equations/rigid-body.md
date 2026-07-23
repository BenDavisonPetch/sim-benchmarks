---
id: rigid-body
human_name: "Rigid body (inert obstacle)"
phase: solid
requires_eos: false
velocity: fixed-zero            # v ≡ 0
evolves: []                     # nothing internal evolves; no field interaction
interchangeable_with: [perfect-conductor]
interchangeable_when: "no coupling magnetic field is present / the body carries no field"
---
## Definition
Non-deforming body with no magnetic-field interaction — an inert obstacle. Velocity is identically
zero and no internal quantity evolves. Phase of matter: solid.

## Params schema
None. No EoS (`requires_eos: false`).

## Notes
Interchangeable with `perfect-conductor` when no coupling field is present (§2.3 / §2.4). Use for
pure hydrodynamic obstacles.

## Refs
(none)
