---
id: perfect-conductor
human_name: "Perfect-conductor boundary"
kind: bc-type
requires_state: false
physical: true
---
## Definition
Perfectly-conducting **domain face**: the normal magnetic field and tangential electric field
vanish at the boundary (field cannot penetrate / is line-tied). A physical electromagnetic wall
condition for MHD faces.

## Params schema
None intrinsic. No `state` expression (`requires_state: false`).

## Notes
Distinct from the `perfect-conductor` **equation-set** base (a solid-phase conducting body) and from
the `perfect-conductor-wall` **internal**-boundary kind (an interior conducting surface). This id is
a `domain_bc` face type. Interpreted under the entry's `b_field_convention`.

## Refs
(none)
