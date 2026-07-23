---
id: material-contact
human_name: "Material contact"
kind: internal-boundary
physical: true
---
## Definition
Hydrodynamic contact interface between two fluid materials: continuity of normal velocity and
pressure across a shared surface, with the materials otherwise distinct (different `base`/`eos`). A
physical interface, never a numerical treatment (never `ghost-fluid`, `cut-cell`).

## Params schema
Geometry of the interface + (optional) motion, as for other internal-boundary kinds. No method
fields.

## Notes
The canonical multi-material coupling. Distinct from `electromagnetic-coupling` (field continuity
between a plasma and a conductor). Its presence sets `has_internal_boundaries = true` (§2.3); the
specific interface geometry does **not** further fork identity (§11.12).

## Refs
(none)
