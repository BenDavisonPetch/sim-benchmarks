---
id: dirichlet
human_name: "Dirichlet (fixed value)"
kind: bc-type
requires_state: true
physical: true
---
## Definition
Prescribed field values on the face, given by a `state` expression per variable. A physical
statement of an imposed value; the numerical enforcement is a method choice, not stored here.

## Params schema
- `state` — per-variable IC-expression-language expressions (§4). May reference `x,y,z` and `t`.
  A `state` expression referencing `t` sets `capability_flags.time_dependent_bc = true` (§2.3,
  `validate.py` check 6).

## Notes
For an imposed inflow with a physical characterisation prefer `subsonic-inflow` /
`supersonic-inflow`; use `dirichlet` for a generic fixed-value face.

## Refs
(none)
