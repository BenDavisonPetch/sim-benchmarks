---
id: axisymmetric
human_name: "Axisymmetric (cylindrical, ∂/∂φ = 0)"
kind: coord-system
variables: [r, z]
axis_singularity: true
---
## Definition
Axisymmetric frame: cylindrical `(r, z)` with no azimuthal dependence (`∂/∂φ = 0`). The **physical
coordinate frame** the problem is posed in — a symmetry of the physical problem, not a grid choice
(SPEC §1.6).

## Params schema
None. Domain extents given per coordinate in `geometry.domain` (e.g. `r: [0,1], z: [0,1]`).

## Notes
Position variables `r, z` available to the expression language (§4). The axis `r=0` typically
demands the `axis-singularity` analysis treatment. Distinct from full `cylindrical` (which retains
`φ`).

## Refs
(none)
