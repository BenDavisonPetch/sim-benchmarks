---
id: cartesian
human_name: "Cartesian"
kind: coord-system
variables: [x, y, z]
axis_singularity: false
---
## Definition
Rectangular Cartesian frame `(x, y, z)`. The **physical coordinate frame the problem is posed in**,
not a grid (SPEC §1.6): a Cartesian frame is problem; a Cartesian *grid* is method.

## Params schema
None. Domain extents given per axis in `geometry.domain` (e.g. `{ x: [0,1], y: [0,1] }`).

## Notes
Position variables `x, y, z` available to the expression language (§4). No axis singularity.

## Refs
(none)
