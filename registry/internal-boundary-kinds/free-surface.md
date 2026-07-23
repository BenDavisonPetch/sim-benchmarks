---
id: free-surface
human_name: "Free surface"
kind: internal-boundary
physical: true
---
## Definition
Interface between a material and a (near-)void / passive ambient, where the traction (pressure)
vanishes on the material side — a free boundary that deforms with the flow. A physical interface
condition, never a numerical treatment.

## Params schema
Geometry of the surface + (optional) motion. No method fields.

## Notes
Distinct from `material-contact` (two active materials). Presence sets `has_internal_boundaries =
true` (§2.3); interface geometry does not further fork identity.

## Refs
(none)
