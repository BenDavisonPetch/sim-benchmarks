---
id: periodic
human_name: "Periodic"
kind: bc-type
requires_state: false
physical: true
---
## Definition
The domain wraps: the field at one face equals the field at the opposite face. A physical statement
about the problem's topology, not a numerical treatment.

## Params schema
None. No `state` expression (`requires_state: false`); paired faces must both be `periodic`.

## Notes
Never references `t`, so it never sets `time_dependent_bc`. Applied per face in `domain_bc`.

## Refs
(none)
