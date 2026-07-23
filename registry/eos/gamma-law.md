---
id: gamma-law
human_name: "Ideal gamma-law EoS"
kind: eos
params: [gamma]
---
## Definition
Ideal-gas (polytropic) equation of state `p = (γ − 1) ρ e`, with constant ratio of specific heats
`γ`. The default closure for `hydro` / `mhd` fluid bases.

## Params schema
- `gamma` — ratio of specific heats (dimensionless). Required. Stored as authored; a value defined
  only by a source is recorded `needs-source` with a `source_ref` (§5.2), never typed from memory.

## Notes
Referenced from a material's `eos.type` (present iff the base declares `requires_eos: true`,
invariant §11.11). Parameter value never affects identity (§2.2).

## Refs
(none)
