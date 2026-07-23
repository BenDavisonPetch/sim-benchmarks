---
id: rigid-wall
human_name: "Rigid wall (internal obstacle surface)"
kind: internal-boundary
physical: true
---
## Definition
Surface of a rigid internal obstacle within the domain: no-penetration (zero normal velocity) on
the fluid side of an embedded solid body. A physical interior wall, never a numerical (cut-cell /
immersed-boundary) treatment.

## Params schema
Geometry of the obstacle surface + (optional) motion. No method fields.

## Notes
The **internal**-boundary analogue of the `reflecting` domain-face BC. Often paired with a
`rigid-body` material for the obstacle itself. Presence sets `has_internal_boundaries = true`;
geometry does not further fork identity. An adversarial obstacle geometry additionally carries a
`geometry_stress` tag (§2.3 exception).

## Refs
(none)
