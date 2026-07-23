---
id: stiffened
human_name: "Stiffened-gas EoS"
kind: eos
params: [gamma, p_inf]
---
## Definition
Stiffened-gas equation of state `p = (γ − 1) ρ e − γ p_∞`, extending the gamma-law with a pressure
offset `p_∞` so it can represent nearly-incompressible liquids and solids. Common for
multi-material and compressible-liquid problems.

## Params schema
- `gamma` — effective ratio of specific heats (dimensionless). Required.
- `p_inf` — stiffening pressure offset (pressure units, as authored). Required.

Both stored as authored; source-defined values recorded `needs-source` + `source_ref` (§5.2).

## Notes
Referenced from a material's `eos.type`. Reduces to `gamma-law` when `p_inf = 0` — but the EoS
**type id** is a physics_signature element (§2.1), so a stiffened material with `p_inf = 0` is not
automatically the same signature as a `gamma-law` material; dedup compares the declared type.
Parameter values never affect identity (§2.2).

## Refs
(none)
