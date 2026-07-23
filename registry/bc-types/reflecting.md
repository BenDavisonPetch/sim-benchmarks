---
id: reflecting
human_name: "Reflecting (solid wall)"
kind: bc-type
requires_state: false
physical: true
---
## Definition
Solid-wall boundary: zero normal velocity (free-slip or no-penetration), tangential/other fields
mirrored. A physical wall condition, stated without prescribing a numerical (ghost-cell) treatment.

## Params schema
None intrinsic. No `state` expression (`requires_state: false`).

## Notes
Distinct from the `rigid-wall` **internal**-boundary kind (an interior obstacle surface);
`reflecting` is a **domain** face BC. Never references `t`.

## Refs
(none)
