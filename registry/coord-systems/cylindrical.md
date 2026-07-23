---
id: cylindrical
human_name: "Cylindrical"
kind: coord-system
variables: [r, phi, z]
axis_singularity: true
---
## Definition
Cylindrical frame `(r, φ, z)`. The **physical coordinate frame** the problem is posed in, not a
grid (SPEC §1.6).

## Params schema
None. Domain extents given per coordinate in `geometry.domain` (e.g. `r: [0,1], z: [0,1]`).

## Notes
Position variables `r, phi, z` available to the expression language (§4). Problems posed here that
include the axis `r=0` typically carry the `axis-singularity` analysis treatment.

## Refs
(none)
