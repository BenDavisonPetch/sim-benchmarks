---
id: neumann
human_name: "Neumann (fixed gradient)"
kind: bc-type
requires_state: true
physical: true
---
## Definition
Prescribed normal-gradient values on the face, given by a `state` expression per variable
(the normal derivative). A physical statement of an imposed flux/gradient.

## Params schema
- `state` — per-variable IC-expression-language expressions (§4) giving the imposed normal
  derivative. May reference `x,y,z` and `t`; a `t`-reference sets `time_dependent_bc = true` (§2.3).

## Notes
Zero-gradient outflow has its own id (`outflow`); use `neumann` for a nonzero or otherwise
specified imposed gradient.

## Refs
(none)
