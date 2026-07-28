---
id: force-balance
human_name: "Wall-normal force balance (n·grad p = n·(J x B))"
kind: wall-pressure-treatment
---
## Definition
The reference imposed the wall-normal momentum balance on pressure at a perfectly-conducting wall:
`n·∇p = n·(J × B)`. The physically correct condition (`registry/bc-types/perfect-conductor.md`).

## Params schema
None.

## Notes
Recorded per reference in `reference_results[].wall_pressure_bc` — a method choice, never part of
the problem block (SPEC §1.6).

## Refs
(none)
