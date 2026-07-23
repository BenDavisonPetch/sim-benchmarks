---
id: electromagnetic-coupling
human_name: "Electromagnetic coupling"
kind: internal-boundary
physical: true
---
## Definition
Field-continuity coupling across the interface between two evolved bodies — e.g. a plasma governed
by `mhd` and a conducting interior governed by `magnetic-diffusion` / `perfect-conductor`. Enforces
continuity of the electromagnetic field across the interface. A physical coupling, never a
numerical method.

## Params schema
Geometry of the interface + (optional) motion, as for other internal-boundary kinds. No method
fields.

## Notes
Distinct from `material-contact` (a hydrodynamic contact between fluids). Used where a conductor is
embedded in, or bounds, a plasma.

## Refs
(none)
