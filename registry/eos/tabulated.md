---
id: tabulated
human_name: "Tabulated EoS"
kind: eos
params: [table]
---
## Definition
Equation of state defined by a tabulated dataset (e.g. SESAME-style `p(ρ,e)`, `T(ρ,e)`) rather than
a closed form. The specific named table + its provenance/refs live as an id-referenced entry under
`registry/tabulated-eos/`; this file is the generic `eos.type`.

## Params schema
- `table` — id of a `registry/tabulated-eos/<id>` entry naming the canonical tabulated dataset and
  its provenance. Required when the type is `tabulated`.

## Notes
Referenced from a material's `eos.type`. The table id is the identity-bearing element (an entry
using table A vs table B differs in physics_signature). `registry/tabulated-eos/` is seeded but may
be empty this build — named tables are authored only as real entries need them (see
`SPEC_DEVIATIONS` D-005).

## Refs
(none)
