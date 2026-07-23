---
id: symmetry
human_name: "Symmetry plane"
kind: internal-boundary
physical: true
---
## Definition
Internal symmetry plane: the solution is mirrored across the surface (zero normal gradient of
scalars, reflected normal velocity), reducing the modelled domain by a physical symmetry of the
problem. A physical statement of the problem's symmetry, never a numerical treatment.

## Params schema
Geometry of the symmetry plane. No method fields.

## Notes
A physical symmetry of the problem (contrast with a method's use of symmetry to save cost, which is
not stored). Presence sets `has_internal_boundaries = true`. Do not use symmetry as a validation
proxy where AMR/gridding breaks it (SPEC §6.3, body `## Qualitative behaviour` warning).

## Refs
(none)
