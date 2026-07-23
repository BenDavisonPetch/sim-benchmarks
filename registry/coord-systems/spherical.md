---
id: spherical
human_name: "Spherical"
kind: coord-system
variables: [r, theta, phi]
axis_singularity: true
---
## Definition
Spherical frame `(r, θ, φ)`. The **physical coordinate frame** the problem is posed in, not a grid
(SPEC §1.6): a spherical frame the physics is posed in is problem; a spherical *grid* is method.

## Params schema
None. Domain extents given per coordinate in `geometry.domain`.

## Notes
Position variables `r, theta, phi` available to the expression language (§4). Problems including
`r=0` or the polar axis typically carry the `axis-singularity` analysis treatment.

## Refs
(none)
