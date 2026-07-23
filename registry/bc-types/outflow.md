---
id: outflow
human_name: "Outflow (zero-gradient)"
kind: bc-type
requires_state: false
physical: true
---
## Definition
Open boundary through which the flow leaves the domain with no imposed incoming state
(zero-gradient / non-reflecting in intent). A physical statement that the boundary is open, not a
specific numerical non-reflecting scheme.

## Params schema
None. No `state` expression (`requires_state: false`).

## Notes
Used for far-field/open faces (e.g. the tail and flanks of the worked Mercury example). Never
references `t`.

## Refs
(none)
