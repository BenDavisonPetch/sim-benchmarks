---
id: none
human_name: "None"
kind: analysis-treatment
---
## Definition
No extra analysis treatment beyond the base problem: the test poses no special grid-alignment,
axis, or multi-material analysis demand. The default member of `analysis_treatments`.

## Params schema
None.

## Notes
Part of the identity signature (§2.1 item 2): `analysis_treatments: [none]` vs a non-trivial set
distinguishes sibling entries (e.g. 1D Sod `[none]` vs 2D-rotated Sod `[oblique-to-grid]`). A
searchable descriptor, not itself a capability fork.

## Refs
(none)
